from django import forms
from django.conf import settings
from django.core import validators
from django.utils.text import get_valid_filename

QrKindTypes = [
    ('svg', 'Svg'),
    ('png', 'Png'),
    ('pdf', 'Pdf')
]

QrFilenameChoices = [
    ('title', 'title.ext'),
    ('envtitle', 'env-title.ext'),
    ('basic', 'basic_info.ext'),
    ('envbasic', 'env-basic_info.ext'),
    ('uuid', 'uuid.ext'),
    ('envuuid', 'env-uuid.ext')
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
    filename = forms.ChoiceField(choices=QrFilenameChoices, required=False, initial='title')

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

    def clean_filename(self):
        if not self['filename'].html_name in self.data:
            return self.fields['filename'].initial
        return self.cleaned_data['filename']

    def create_filename(self, code):
        filename_setting = self.cleaned_data['filename']
        ext = self.cleaned_data["kind"]
        name = f'{code.title}.{ext}'
        if filename_setting == 'envtitle':
            name = f'{settings.ENVIRONMENT}-{code.title}.{ext}'
        if filename_setting == 'basic':
            subname = code.basic_info[:200].replace(':', '_')
            name = f'{subname}.{ext}'
        if filename_setting == 'envbasic':
            subname = code.basic_info[:200].replace(':', '_')
            name = f'{settings.ENVIRONMENT}-{subname}.{ext}'
        if filename_setting == 'uuid':
            name = f'{code.short_uuid}.{ext}'
        if filename_setting == 'envuuid':
            name = f'{settings.ENVIRONMENT}-{code.short_uuid}.{ext}'

        return get_valid_filename(name)
