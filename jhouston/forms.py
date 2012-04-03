from django import forms
from models import ErrorReport, LogReport

LOG_LEVELS = ('INFO', 'DEBUG', 'ERROR', 'CRITICAL', 'WARNING')

class ErrorReportForm(forms.ModelForm):
    
    class Meta:
        fields = ('message', 'url', 'line_number',)
        model = ErrorReport

class LogReportForm(forms.ModelForm):
    class Meta:
        model = LogReport