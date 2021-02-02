import requests
import io
import zipfile

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin
from django.urls import path

from .models import ApiHit, Department, LinkUrl, QRCode


@admin.register(ApiHit)
class ApiHitAdmin(admin.ModelAdmin):
    readonly_fields = ('hit_date', 'action', 'code', 'message')
    list_display = ('code', 'hit_date', 'action', 'message')
    change_list_template = 'qrtoolkit_core/apihit/change_list.html'
    list_filter = ('code__department__name',)

    def get_list_display(self, request):
        return super(ApiHitAdmin, self).get_list_display(request)


class LinkUrlInline(admin.StackedInline):
    model = LinkUrl
    extra = 1


@admin.register(QRCode)
class QRCodeAdmin(VersionAdmin):
    list_display = ('title', 'department',
                    'get_code_url', 'get_code_image_url')
    list_filter = (('department', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('title', 'department__name')
    inlines = [LinkUrlInline]
    change_list_template = 'qrtoolkit_core/qrcode/change_list.html'
    actions = ['download_codes', ]
    readonly_fields = ('uuid',)

    def get_queryset(self, request):
        qs = super(QRCodeAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(department=request.user.department)

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

    def download_codes(self, request, queryset):
        zip_filename = 'archive.zip'
        s = io.BytesIO()

        zf = zipfile.ZipFile(s, mode='w', compression=zipfile.ZIP_DEFLATED)

        downloaded_files = []
        for code in queryset.all():
            url = settings.REDIRECT_SERVICE_URL + f'/code/{code.short_uuid}/dl/'
            res = requests.get(url)
            zf.writestr(f'{code.title}-{code.uuid}.svg', res.content)
            downloaded_files.append(code.title)

        zf.close()

        resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = f'attachment; filename={zip_filename}'

        message = f'Downloaded zip with files: {", ".join(downloaded_files)}'
        self.message_user(request, message=message)
        return resp

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'department' and not request.user.is_superuser:
            kwargs['queryset'] = Department.objects.filter(name__exact=request.user.department.name)
        return super(QRCodeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        urls = super(QRCodeAdmin, self).get_urls()
        custom_urls = [
            path('scan/', self.admin_site.admin_view(self.scan_view))
        ]
        return custom_urls + urls

    def scan_view(self, request):
        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            # Anything else you want in the context...
            is_nav_sidebar_enabled=False,
            title='Scan qr code'
        )

        return TemplateResponse(request, 'qrtoolkit_core/qrcode/scanner.html', context)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


admin.site.site_header = 'Qr Gent Administration'
admin.site.site_title = 'Qr Gent admin'
admin.site.site_url = settings.API_URL
