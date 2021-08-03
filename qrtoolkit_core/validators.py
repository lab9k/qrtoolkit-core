from django.core.exceptions import ValidationError


def validate_is_api_mode_qrcode(value):
    """

    :type value: LinkUrl
    """
    from .models import QRCode, LinkUrl
    qrcode = LinkUrl.objects.select_related('code').get(pk=value).code
    if qrcode.mode != QRCode.REDIRECT_MODE_CHOICES.API_CALL:
        raise ValidationError('The selected qr code is not in Api call Mode.')
