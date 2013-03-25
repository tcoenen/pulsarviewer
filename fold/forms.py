from django import forms


def check_period(period):
    if period is not None and period <= 0:
        raise forms.ValidationError('Period must be larger than 0 (ms).')
    return period


def check_largerthanzero(value, quantity):
    if value is not None and value <= 0:
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

# TODO : figure out what is wrong when posting the form (if I put a 0
# in lo_redchisq field it does not show up in output).
#    def clean(self):
#        cleaned_data = super(ConstraintsForm, self).clean()
#
#        if cleaned_data['hi_p'] is not None and cleaned_data['lo_p'] is not None:
#            if cleaned_data['hi_p'] <= cleaned_data['lo_p']:
#                raise forms.ValidationError('Highest period must be larger than lowest')
#
#        if cleaned_data['hi_redchisq'] is not None and cleaned_data['lo_redchisq'] is not None:
#            if cleaned_data['hi_redchisq'] <= cleaned_data['lo_redchisq']:
#                raise forms.ValidationError('Highest reduced chi-squared  must be larger than lowest')
#
##        if cleaned_data['hi_dm'] is not None and cleaned_data['lo_dm'] is not None:
##            if cleaned_data['hi_dm'] <= cleaned_data['lo_dm']:
##                raise forms.ValidationError('Highest DM must be larger than lowest')

        return cleaned_data
