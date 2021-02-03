from django.urls import reverse
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from .models import ApiHit, QRCode
from django.http import Http404, HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.views.generic import DetailView
import requests
import uuid


def download_code(request, short_uuid):
    if request.user.is_authenticated:
        try:
            short_uuid = uuid.UUID(short_uuid)
            # short_uuid is a valid uuid object
            code, created = QRCode.objects.get_or_create(uuid=short_uuid,
                                                         defaults={'department': request.user.department})
        except ValueError:
            # short_uuid is not a valid uuid object
            code, created = QRCode.objects.get_or_create(short_uuid=short_uuid,
                                                         defaults={'department': request.user.department})
        if created:
            code.title = request.GET.get('title', 'Auto Generated Code')
            code.save()
    else:
        try:
            short_uuid = uuid.UUID(short_uuid)
            # short_uuid is a valid uuid object
            code = QRCode.objects.get(uuid=short_uuid)
        except ValueError:
            # short_uuid is not a valid uuid object
            code = QRCode.objects.get(short_uuid=short_uuid)

    code_url = request.build_absolute_uri(reverse("qrcode-detail", kwargs=dict(short_uuid=code.short_uuid)))
    image_url = f'http://qrcodeservice.herokuapp.com/?query={code_url}'
    image_resp = requests.get(image_url).text

    response = HttpResponse(image_resp, content_type='image/svg+xml')
    response['Content-Length'] = len(response.content)
    response['Content-Disposition'] = f'attachment; filename="{code.title}.svg"'
    return response


# @login_required
# def generate(request, amount):
#     zip_filename = 'generated_codes.zip'
#     s = io.BytesIO()
#
#     zf = zipfile.ZipFile(s, mode='w', compression=zipfile.ZIP_DEFLATED)
#     uuids = [uuid.uuid4() for _ in range(amount)]
#
#     for uid in uuids:
#         code_url = request.build_absolute_uri(reverse('qrcode-detail', kwargs=dict(short_uuid=uid)))
#         image_url = f'http://qrcodeservice.herokuapp.com/?query={code_url}'
#         res = requests.get(image_url)
#         zf.writestr(f'Auto Generated Code-{uid}.svg', res.content)
#
#     zf.close()
#
#     resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
#     resp['Content-Disposition'] = f'attachment; filename={zip_filename}'
#     return resp


class CodeView(DetailView):
    template_name = 'qrtoolkit_core/qrcode/code.html'
    pk_url_kwarg = 'short_uuid'
    queryset = QRCode.objects.all()
    context_object_name = 'code'

    def get_object(self, queryset=None):
        uid = self.kwargs.get(self.pk_url_kwarg)
        try:
            try:
                short_uuid = uuid.UUID(uid)
                # short_uuid is a valid uuid object
                return self.queryset.get(uuid=short_uuid)
            except ValueError:
                # short_uuid is not a valid uuid object
                return self.queryset.get(short_uuid=uid)
        except QRCode.DoesNotExist or ValidationError:
            raise Http404


class QRCodeDetails(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    permission_classes = []

    @staticmethod
    def get_object(short_uuid):
        try:
            try:
                short_uuid = uuid.UUID(short_uuid)
                # short_uuid is a valid uuid object
                return QRCode.objects.get(uuid=short_uuid)
            except ValueError:
                # short_uuid is not a valid uuid object
                return QRCode.objects.get(short_uuid=short_uuid)

        except (QRCode.DoesNotExist or ValidationError) as error:
            hit = ApiHit(code=None, action=ApiHit.ACTION_CHOICES.ERROR,
                         message=f'code with "{str(short_uuid)}" does not exist.')
            hit.save()
            raise Http404

    def get(self, request, short_uuid=None, format=None):
        qrcode = self.get_object(short_uuid=short_uuid)

        if request.accepted_renderer.format == 'json' or format == 'json':
            if request.user.is_authenticated:
                hit = ApiHit(
                    code=qrcode, action=ApiHit.ACTION_CHOICES.JSON)
                hit.save()
                return redirect(to=f'{settings.API_URL}/qrcodes/{qrcode.id}/', permanent=False)
            else:
                raise NotAuthenticated

        if request.accepted_renderer.format == 'html' or format == 'html':
            if qrcode.urls.count() == 0:
                hit = ApiHit(code=qrcode, action=ApiHit.ACTION_CHOICES.BASIC_INFO)
                hit.save()
                return Response({'qrcode': qrcode}, template_name='qrtoolkit_core/qrcode/index.html')

            if qrcode.mode == QRCode.REDIRECT_MODE_CHOICES.REDIRECT:
                hit = ApiHit(
                    code=qrcode, action=ApiHit.ACTION_CHOICES.REDIRECT)
                hit.save()
                return redirect(qrcode.urls.first().url, permanent=False)
            if qrcode.mode == QRCode.REDIRECT_MODE_CHOICES.KIOSK:
                hit = ApiHit(code=qrcode, action=ApiHit.ACTION_CHOICES.KIOSK)
                hit.save()
                return Response({'qrcode': qrcode}, template_name='qrtoolkit_core/qrcode/kiosk.html')
            if qrcode.mode == QRCode.REDIRECT_MODE_CHOICES.INFO_PAGE:
                hit = ApiHit(code=qrcode, action=ApiHit.ACTION_CHOICES.BASIC_INFO)
                hit.save()
                return Response({'qrcode': qrcode}, template_name='qrtoolkit_core/qrcode/index.html')

            return Response({'qrcode': qrcode}, template_name='qrtoolkit_core/qrcode/index.html')

        hit = ApiHit(
            code=qrcode, action=ApiHit.ACTION_CHOICES.JSON)
        hit.save()
        return redirect(to=f'{settings.API_URL}/qrcodes/{qrcode.id}/', permanent=False)
