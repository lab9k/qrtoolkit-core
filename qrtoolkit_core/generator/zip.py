import io
import zipfile

from .qr import create_qr_code


def generate_qr_zip(codes, form):
    """

    :type codes: list[qrtoolkit_core.models.QRCode]
    :type form: qrtoolkit_core.generator.forms.QrGenerateForm
    """
    s = io.BytesIO()

    zf = zipfile.ZipFile(s, mode='w', compression=zipfile.ZIP_DEFLATED)

    for code in codes:
        code_buffer = create_qr_code(code, form)
        filename = form.create_filename(code)
        zf.writestr(filename, code_buffer)

    zf.close()

    return s.getvalue()
