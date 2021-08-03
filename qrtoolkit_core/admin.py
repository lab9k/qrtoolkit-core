import datetime
import uuid

import django.http.request
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.urls import path
from django.shortcuts import render, redirect, reverse

from .generator.forms import QrGenerateForm
from .generator.zip import generate_qr_zip
from .models import ApiHit, Department, LinkUrl, QRCode, ApiCall, Header
from .serializers import ApiHitSerializer
from rest_framework.renderers import JSONRenderer

User = get_user_model()

admin.site.unregister(User)


class DepartmentInline(admin.TabularInline):
    model = Department.users.through


@admin.register(User)
class MyUserAdmin(UserAdmin):
    inlines = [DepartmentInline]


@admin.register(ApiHit)
class ApiHitAdmin(admin.ModelAdmin):
    readonly_fields = ('hit_date', 'action', 'code', 'message')
    list_display = ('code', 'hit_date', 'action', 'message')
    change_list_template = 'qrtoolkit_core/apihit/change_list.html'
    list_filter = ('code__department__name',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        cl = self.get_changelist_instance(request)

        hit_data = ApiHitSerializer(instance=cl.get_queryset(request), many=True).data
        extra_context['hits_json'] = JSONRenderer().render(hit_data).decode('utf-8')

        return super(ApiHitAdmin, self).changelist_view(request, extra_context=extra_context)


class LinkUrlInline(admin.StackedInline):
    model = LinkUrl
    extra = 1


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'department',
                    'get_code_url', 'get_code_image_url', 'basic_info')
    list_filter = (('department', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('title', 'department__name', 'basic_info')
    inlines = [LinkUrlInline]
    change_list_template = 'qrtoolkit_core/qrcode/change_list.html'
    actions = ['download_codes_action', ]
    readonly_fields = ('uuid',)

    def get_queryset(self, request):
        qs = super(QRCodeAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(department__in=request.user.departments.all())

    def get_model_perms(self, request):
        return super(QRCodeAdmin, self).get_model_perms(request)

    def get_code_image_url(self, obj):
        return mark_safe(
            f'<span><a href="{settings.REDIRECT_SERVICE_URL}/code/{obj.short_uuid}">/code/{obj.short_uuid}</a></span>')

    def get_code_url(self, obj):
        return mark_safe(
            f'<span><a href="{settings.REDIRECT_SERVICE_URL}/{obj.short_uuid}">/{obj.short_uuid}</a></span>')

    get_code_image_url.short_description = 'Code image'
    get_code_url.short_description = 'Code url'

    def download_codes_action(self, request, queryset):
        """

        :type queryset: django.db.models.query.QuerySet
        :type request: django.http.request.HttpRequest
        """
        pks = [str(x.pk) for x in queryset.all()]
        url = '%s' % (reverse('admin:admin_qr_download'),)
        request.session['codes_to_download'] = pks
        return redirect(url)

    download_codes_action.short_description = 'Download codes'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'department' and not request.user.is_superuser:
            kwargs['queryset'] = request.user.departments.all()
        return super(QRCodeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        return {'department': request.user.departments.first()}

    def get_urls(self):
        urls = super(QRCodeAdmin, self).get_urls()
        custom_urls = [
            path('download/', self.admin_site.admin_view(self.download_codes), name='admin_qr_download'),
            path('scan/', self.admin_site.admin_view(self.scan_view), name='admin_scan_search')
        ]
        return custom_urls + urls

    def scan_view(self, request):
        if request.method == 'POST':
            short_uuid = request.POST['short_uuid']
            try:
                code = _get_qr_code(short_uuid)
                return redirect('admin:qrtoolkit_core_qrcode_change', object_id=code.pk)
            except QRCode.DoesNotExist:
                self.message_user(request, f'Qr code with uuid {short_uuid} not found.', level=messages.WARNING)

        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            # Anything else you want in the context...
            is_nav_sidebar_enabled=False,
            title='Scan qr code'
        )
        return TemplateResponse(request, 'qrtoolkit_core/qrcode/scanner.html', context)

    def download_codes(self, request):
        """
        Downloads specified qr codes in a zip archive. qr code id's are provided by using the 'codes' query parameter

        :type request: django.http.HttpRequest
        """
        if request.method == 'POST':
            download = request.GET['download']
            pks = [int(x) for x in download.split(',')]
            if request.user.is_superuser:
                codes = QRCode.objects.filter(pk__in=pks).all()
            else:
                codes = QRCode.objects.filter(pk__in=pks, department__in=request.user.departments.all()).all()
            form = QrGenerateForm(data=request.POST)
            if form.is_valid():
                zf = generate_qr_zip(codes, form)
                resp = HttpResponse(zf, content_type="application/x-zip-compressed")
                resp[
                    'Content-Disposition'] = f'attachment; filename=generated_codes-{download.replace(",", "_")[:20]}.zip'
                return resp
            else:
                context = dict(
                    self.admin_site.each_context(request),
                    is_nav_sidebar_enabled=False,
                    title="Download Qr codes",
                    codes=codes,
                    form=form
                )
                return render(request, 'qrtoolkit_core/qrcode/download.html', context=context)
        else:
            pks = request.session.get('codes_to_download')
            if request.user.is_superuser:
                codes = QRCode.objects.only('id', 'title').filter(pk__in=pks).all()
            else:
                codes = QRCode.objects.only('id', 'title').filter(pk__in=pks,
                                                                  department__in=request.user.departments.all()).all()
            context = dict(
                self.admin_site.each_context(request),
                is_nav_sidebar_enabled=False,
                title="Download Qr codes",
                codes=codes,
                form=QrGenerateForm()
            )

            return render(request, 'qrtoolkit_core/qrcode/download.html', context=context)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


class HeaderInline(admin.TabularInline):
    model = Header
    extra = 1


@admin.register(ApiCall)
class ApiCallAdmin(admin.ModelAdmin):
    inlines = [HeaderInline]

    def _get_extra_context(self, request, extra_context=None):
        extra_context = dict() if extra_context is None else extra_context
        if not request.user.is_superuser:
            owner_codes = QRCode.objects.only('title').filter(department__in=request.user.departments.all(),
                                                              mode=QRCode.REDIRECT_MODE_CHOICES.API_CALL).all()
        else:
            owner_codes = QRCode.objects.only('title').filter(mode=QRCode.REDIRECT_MODE_CHOICES.API_CALL).all()
        extra_context['owner_codes'] = owner_codes
        return extra_context

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = self._get_extra_context(request, extra_context=extra_context)
        return super(ApiCallAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = self._get_extra_context(request, extra_context=extra_context)
        return super(ApiCallAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)

    def get_field_queryset(self, db, db_field, request):
        if db_field.name == 'link_url':
            if not request.user.is_superuser:
                return db_field.remote_field.model.objects.filter(code__department__in=request.user.departments.all(),
                                                                  code__mode=QRCode.REDIRECT_MODE_CHOICES.API_CALL)
            else:
                return db_field.remote_field.model.objects.filter(code__mode=QRCode.REDIRECT_MODE_CHOICES.API_CALL)
        return super(ApiCallAdmin, self).get_field_queryset(db, db_field, request)


admin.site.site_header = 'Qr Gent Administration'
admin.site.site_title = 'Qr Gent admin'
admin.site.site_url = settings.API_URL


def _get_qr_code(short_uuid):
    try:
        short_uuid = uuid.UUID(short_uuid)
        # short_uuid is a valid uuid object
        return QRCode.objects.get(uuid=short_uuid)
    except ValueError:
        # short_uuid is not a valid uuid object
        return QRCode.objects.get(short_uuid=short_uuid)
