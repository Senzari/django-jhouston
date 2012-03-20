import logging
log = logging.getLogger(__name__)

from django.forms import ModelForm

from models import ErrorReport

class ErrorReportForm(ModelForm):
    
    class Meta:
        fields = ('message', 'url', 'line_number',)
        model = ErrorReport

    def save(self, *a, **k):
        log.error('error')
        return super(ErrorReportForm, self).save(*a, **k)