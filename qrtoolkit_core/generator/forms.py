from django import forms
from django.core import validators

QrKindTypes = [
    ('svg', 'Svg'),
    ('png', 'Png'),
    ('pdf', 'Pdf')
]


class HexField(forms.CharField):
    def __init__(self, **kwargs):
        super(HexField, self).__init__(max_length=7, min_length=4, **kwargs)
        self.validators.append(validators.RegexValidator(regex='^#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?$'))


class QrGenerateForm(forms.Form):
    query = forms.HiddenInput()
    kind = forms.ChoiceField(choices=QrKindTypes, required=False, initial='svg')
    light = HexField(required=False, initial='#FFFFFF', widget=forms.TextInput(attrs={'type': 'color'}))
    dark = HexField(required=False, initial='#000000', widget=forms.TextInput(attrs={'type': 'color'}))
    scale = forms.IntegerField(required=False, initial=3)

    def clean_kind(self):
        if not self['kind'].html_name in self.data:
            return self.fields['kind'].initial
        return self.cleaned_data['kind']

    def clean_light(self):
        if not self['light'].html_name in self.data:
            return self.fields['light'].initial
        return self.cleaned_data['light']

    def clean_dark(self):
        if not self['dark'].html_name in self.data:
            return self.fields['dark'].initial
        return self.cleaned_data['dark']

    def clean_scale(self):
        if not self['scale'].html_name in self.data:
            return self.fields['scale'].initial
        return self.cleaned_data['scale']
