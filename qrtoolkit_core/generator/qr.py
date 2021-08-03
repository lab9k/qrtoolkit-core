import io
import segno
from django.conf import settings


def create_qr_code(code, form):
    """

    :type code: qrtoolkit_core.models.QRCode
    :type form: qrtoolkit_core.generator.forms.QrGenerateForm
    """
    out = io.BytesIO()
    url = f'{settings.REDIRECT_SERVICE_URL}/{code.short_uuid}/'
    qr = segno.make_qr(url)
    qr.save(out,
            dark=form.cleaned_data['dark'],
            light=form.cleaned_data['light'],
            scale=form.cleaned_data['scale'],
            kind=form.cleaned_data['kind'])
    return out.getvalue()
