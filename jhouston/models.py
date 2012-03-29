import json
import logging
log = logging.getLogger(__name__)

from raven import Client
from django.db import models
from django.conf import settings

log_format_str = "Front End: %(line_number)s [%(abbv_user_agent)s]"

class LogReport(models.Model):
    message = models.CharField(max_length=1e9)
    log_level = models.CharField(max_length=8)
    extra = models.CharField(help_text='JSON serialized extra information', blank=True, max_length=1e9)

    def save(self, *a, **k):
        """
        Don't save to the database, send to sentry instead.
        """
        log_level = self.log_level
        
        if self.extra:
            extra = {"extra": json.loads(self.extra)}
                
        client = Client(settings.SENTRY_DSN)
        client.capture(
            "Message",
            message=self.message,
            data=extra,
        )

class ErrorReport(models.Model):
    message = models.TextField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    # Ideally, URLField(max_length=1024) would be used.  However,
    # MySQL has a max_length limitation of 255 for URLField.
    url = models.TextField()
    line_number = models.PositiveIntegerField()
    user_agent = models.TextField()
    remote_addr = models.IPAddressField(blank=True)
    data = models.TextField(blank=True)
    
    
    def save(self, *a, **k):
        """
        Don't save to database, post to sentry instead.
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
    Given a full user agent string, return either "IE", "Firefox", "Chrome"...
    """
    ua = ua.lower()
    
    if 'firefox' in ua:
        return 'Firefox'
    
    if 'chrome' in ua:
        return "Chrome"
    
    if 'msie 7' in ua:
        return "IE7"

    if 'msie 6' in ua:
        return "IE6"
    
    return "Other"

def get_filename(url):
    """
    Given a complete url for a file, return just the last directory and
    filename. http://senzari.com/static/blah/views/artist.js -> blah/artist.js
    """
    return "/".join(url.split('/')[-2:])
    