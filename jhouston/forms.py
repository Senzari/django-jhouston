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
    
    def clean_log_level(self):
        level = self.cleaned_data['log_level'].upper()
        if level not in LOG_LEVELS:
            raise forms.ValidationError('invalid level, must be one of: ' + str(LOG_LEVELS))
        return level