import uuid
import string
import random

from django.db import models
from django.utils.translation import gettext_lazy as _

from qrtoolkit_core.validators import validate_is_api_mode_qrcode


class ApiHit(models.Model):
    # noinspection PyPep8Naming
    class ACTION_CHOICES(models.TextChoices):
        BASIC_INFO = 'basic_info', _('Basic Info')
        KIOSK = 'kiosk', _('Kiosk')
        JSON = 'json', _('Json Response')
        REDIRECT = 'redirect', _('Redirect')
        API_CALL = 'api_call', _('Api Call')
        ERROR = 'error', _('Error')

    hit_date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(
        max_length=16, choices=ACTION_CHOICES.choices, default=ACTION_CHOICES.BASIC_INFO)
    code = models.ForeignKey(
        'QRCode', on_delete=models.CASCADE, related_name='hits', null=True, blank=True)
    message = models.CharField(max_length=255, blank=True, null=True,
                               help_text='Extra information about errors or other extra info')

    class Meta:
        ordering = ['-hit_date']


class Department(models.Model):
    name = models.CharField(max_length=128, unique=True)
    users = models.ManyToManyField('auth.User', related_name='departments', blank=True)

    def __str__(self) -> str:
        return f'{self.name}'


class LinkUrl(models.Model):
    name = models.CharField(max_length=64, blank=True,
                            default='', help_text='Name of the url. Used in buttons and links when a code is scanned.')
    url = models.URLField(blank=True,
                          default='',
                          help_text='redirect to external page',
                          max_length=800)
    priority = models.FloatField(default=1)
    visible = models.BooleanField(default=True, null=True, blank=True,
                                  help_text='Sets the visibility for this link in KIOSK mode.')
    code = models.ForeignKey(
        to='QRCode',
        on_delete=models.CASCADE,
        related_name='urls')

    def __str__(self):
        return f'"{self.name}" on code: "{self.code.title}"'

    class Meta:
        ordering = ['-priority']


QR_MODE_HELP_TEXT = """
Sets the mode this code is in.<br/>
Kiosk Mode: Show buttons to choose a link from<br/>
Redirect Mode: Instantly redirects to the url with the highest priority.<br/>
Information Page Mode: Show basic info with links to different urls.<br/>
Api call Mode: Will look for ApiCall's in the database that correspond to the selected link_url, and execute them. (Extended Kiosk mode)
"""


class QRCode(models.Model):
    # noinspection PyPep8Naming
    class REDIRECT_MODE_CHOICES(models.TextChoices):
        KIOSK = 'kiosk', _('Kiosk Mode')
        REDIRECT = 'redirect', _('Redirect Mode')
        INFO_PAGE = 'info_page', _('Information Page Mode')
        API_CALL = 'api_call', _('Api call Mode')

    title = models.CharField(blank=True, default='', max_length=100, unique=True)
    department = models.ForeignKey(
        to=Department, on_delete=models.CASCADE, related_name='qrcodes', blank=True, null=True)

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True
    )
    short_uuid = models.SlugField(
        unique=True,
        blank=True,
        null=True,
    )

    basic_info = models.TextField(blank=True, default='')
    kiosk_introduction = models.TextField(blank=True, default='')

    mode = models.CharField(
        max_length=16, choices=REDIRECT_MODE_CHOICES.choices, default=REDIRECT_MODE_CHOICES.REDIRECT,
        help_text=QR_MODE_HELP_TEXT)

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if (not self.short_uuid) or (QRCode.objects.filter(short_uuid=self.short_uuid).exclude(pk=self.pk).count() > 0):
            short = random_string()
            while QRCode.objects.filter(short_uuid=short).exclude(pk=self.pk).count() > 0:
                short = random_string()
            self.short_uuid = short
        return super(QRCode, self).save(*args, **kwargs)

    def __str__(self) -> str:
        if self.department is not None:
            return f'{self.title}, {self.department.name}'
        return f'{self.title}'


class ApiCall(models.Model):
    url = models.URLField()
    link_url = models.ForeignKey(LinkUrl, on_delete=models.CASCADE, related_name='api_calls',
                                 validators=[validate_is_api_mode_qrcode])
    payload = models.TextField()

    def __str__(self):
        return f'link: {self.link_url_id}: {self.url}'


class Header(models.Model):
    api_call = models.ForeignKey(ApiCall, on_delete=models.CASCADE, related_name='headers')
    key = models.CharField(max_length=128)
    value = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.key}'


def random_string():
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, k=8))
