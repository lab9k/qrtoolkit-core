from django.urls import reverse
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from .models import ApiHit, QRCode, LinkUrl
from django.http import Http404, HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
import uuid
import logging

logger = logging.getLogger('qrtoolkit_core.views')


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
                         message=f'code with id {{{str(short_uuid)}}} does not exist.')
            hit.save()
            raise Http404

    def get(self, request, short_uuid=None, format=None):
        qrcode = self.get_object(short_uuid=short_uuid)

        if request.accepted_renderer.format == 'json' or format == 'json':
            hit = ApiHit(
                code=qrcode, action=ApiHit.ACTION_CHOICES.JSON)
            hit.save()
            response = redirect(to=f'{settings.API_URL}/qrcodes/{qrcode.id}/', permanent=False)
            auth_header = request.headers.get('apiKey')
            if auth_header is None:
                raise NotAuthenticated
            response['apiKey'] = auth_header
            return response

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
            if qrcode.mode == QRCode.REDIRECT_MODE_CHOICES.API_CALL:
                hit = ApiHit(code=qrcode, action=ApiHit.ACTION_CHOICES.API_CALL)
                hit.save()
                return Response({'qrcode': qrcode}, template_name='qrtoolkit_core/qrcode/kiosk_call.html')

            return Response({'qrcode': qrcode}, template_name='qrtoolkit_core/qrcode/index.html')

        hit = ApiHit(
            code=qrcode, action=ApiHit.ACTION_CHOICES.JSON)
        hit.save()
        return redirect(to=f'{settings.API_URL}/qrcodes/{qrcode.id}/', permanent=False)


def link_url_clicked(request, pk):
    u = get_object_or_404(LinkUrl, pk=pk)
    handle_api_calls(u)
    return redirect(to=u.url, permanent=False)


def handle_api_calls(url):
    """
    If the code has apicalls configured, fire them off.
    :type url: LinkUrl
    """
    import requests
    for api_call in url.api_calls.all():
        headers = {}
        for header in api_call.headers.all():
            headers[header.key] = header.value
        logger.info(f'posting api_call from {url.name} to {api_call.url}')
        r = requests.post(api_call.url, api_call.payload, headers=headers)
        logger.info(f'response: {r.content.decode("utf-8")}, status_code: {r.status_code}')
