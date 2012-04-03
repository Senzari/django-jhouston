import json
import logging
import warnings

log = logging.getLogger(__name__)

import httpagentparser

from raven import Client
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

JHOUSTON_STORAGE_METHOD = getattr(settings, "JHOUSTON_STORAGE_METHOD", None)
if not JHOUSTON_STORAGE_METHOD:
    warnings.warn("No setting for JHOUSTON_STORAGE_METHOD, using database as default")
    JHOUSTON_STORAGE_METHOD = 'database'

# the format for the front end error message title.
log_format_str = "Front End: %(line_number)s [%(abbv_user_agent)s]"

class SaveMixin(object):
    """
    Save method for determining if a sentry call, database save, or
    both is needed. Use this on all Report models, as the logic will always
    be the same.
    """
    def save(self, *a, **k):
        if "sentry" in JHOUSTON_STORAGE_METHOD:
            self.send_to_sentry()
        
        if "database" in JHOUSTON_STORAGE_METHOD:
            super(LogReport, self).save(*a, **k)


class LogReport(models.Model, SaveMixin):
    """
    Each instance of this model represents a generic event that happened on
    the front end. It could be an error, or any other interesting condition
    that a developer wants to track.
    """
    
    reported_at = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=1e9)
    log_level = models.CharField(max_length=8)
    js_url = models.CharField(max_length=255, null=True, blank=True)
    extra = models.CharField(help_text='JSON serialized extra information', blank=True, max_length=1e9)
    
    def clean_log_level(self):
        level = self.cleaned_data['log_level'].upper()
        if level not in LOG_LEVELS:
            raise ValidationError('invalid level, must be one of: ' + str(LOG_LEVELS))
        return level
    
    def send_to_sentry(self):
        """
        Send this error to sentry where it will be stored and aggregated.
        """
        
        log_level = self.log_level
        filename = get_filename(self.js_url)
        
        data={
            filename: {
                'url': self.js_url,
                'data': {},
                'query_string': '...',
                'method': 'POST',
            },
            'logger': 'front_end',
            'site': 'site.name',
        }
        
        if self.extra:
            data.update({"extra": json.loads(self.extra)})
                
        client = Client(settings.SENTRY_DSN)
        client.capture(
            "Message",
            message=self.message,
            data=data,
        )


class ErrorReport(models.Model, SaveMixin):
    """
    Each instance of this model represents an error that happened on the front
    end.
    """
    
    message = models.TextField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    # Ideally, URLField(max_length=1024) would be used.  However,
    # MySQL has a max_length limitation of 255 for URLField.
    url = models.TextField()
    line_number = models.PositiveIntegerField()
    user_agent = models.TextField()
    remote_addr = models.IPAddressField(blank=True)
    data = models.TextField(blank=True)

    def send_to_sentry(self):
        """
        Send this error to sentry where it will be stored and aggregated.
        """
        
        line_number = self.line_number
        abbv_user_agent = get_pretty_useragent(self.user_agent)
        filename = get_filename(self.url)
        
        msg = "Front End: %s [%s] %s" % (filename, abbv_user_agent, self.message)
        
        client = Client(settings.SENTRY_DSN)
        client.capture(
            "Message",
            message=msg,
            data={
                "extra": {
                    "linenumber": self.line_number,
                    "user_agent": self.user_agent,
                    "url": self.url,
                }
            }
        )


def get_pretty_useragent(ua):
    """
    Given a full user agent string, return either "IE", "Firefox",
    "Chrome"... something abbreviated and pretty.
    """
    return httpagentparser.simple_detect(ua)[1]


def get_filename(url):
    """
    Given a complete url for a file, return just the last directory and
    filename. http://senzari.com/static/blah/views/artist.js -> blah/artist.js
    """
    return "/".join(url.split('/')[-2:])
    