import io
import zipfile

from .qr import create_qr_code


def generate_qr_zip(codes, form):
    s = io.BytesIO()

    zf = zipfile.ZipFile(s, mode='w', compression=zipfile.ZIP_DEFLATED)

    for code in codes:
        code_buffer = create_qr_code(code, form)
        zf.writestr(f'{code.title}.{form.cleaned_data["kind"]}', code_buffer)

    zf.close()

    return s.getvalue()
