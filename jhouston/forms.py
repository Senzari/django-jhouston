import logging
log = logging.getLogger(__name__)

from raven import Client
from django.forms import ModelForm
from models import ErrorReport

class ErrorReportForm(ModelForm):
    
    class Meta:
        fields = ('message', 'url', 'line_number',)
        model = ErrorReport

    def save(self, *a, **k):
        client = Client()
        client.capture("Message", message='foo', data={
            "extra": self.cleaned_data['line_number'],
            "user_agent": self.cleaned_data['user_agent'], 
        })
        return super(ErrorReportForm, self).save(*a, **k)