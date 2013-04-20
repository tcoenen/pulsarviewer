from django import forms

from taggit.forms import TagField

from models import Bestprof


def check_period(period):
    if period is not None and period <= 0:
        raise forms.ValidationError('Period must be larger than 0 (ms).')
    return period


def check_largerthanzero(value, quantity):
    if value is not None and value < 0:
        raise forms.ValidationError('%s must be larger than zero.' % quantity)
    return value


class ConstraintsForm(forms.Form):
    lo_p = forms.FloatField(required=False, label='Lowest period (ms)')
    hi_p = forms.FloatField(required=False, label='Higest period (ms)')
    lo_redchisq = forms.FloatField(required=False,
                                   label='Lowest reduced chi-squared')
    hi_redchisq = forms.FloatField(required=False,
                                   label='Highest reduced chi-squared')
    lo_dm = forms.FloatField(required=False, min_value=0, label='Lowest DM')
    hi_dm = forms.FloatField(required=False, label='Highest DM')

    def clean_lo_p(self):
        return check_period(self.cleaned_data['lo_p'])

    def clean_hi_p(self):
        return check_period(self.cleaned_data['hi_p'])

    def clean_lo_redchisq(self):
        return check_largerthanzero(self.cleaned_data['lo_redchisq'],
                                    'Reduced chi-squared')

    def clean_hi_redchisq(self):
        return check_largerthanzero(self.cleaned_data['hi_redchisq'],
                                    'Reduced chi-squared')

    def clean_hi_dm(self):
        return check_largerthanzero(self.cleaned_data['hi_dm'], 'DM')


class CandidateTagForm(forms.ModelForm):
    class Meta:
        model = Bestprof
        fields = ('tags',)
