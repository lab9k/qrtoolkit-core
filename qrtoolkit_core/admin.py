from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin
from django.urls import path
from django.shortcuts import render, redirect, reverse

from .generator.forms import QrGenerateForm
from .generator.zip import generate_qr_zip
from .models import ApiHit, Department, LinkUrl, QRCode

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
        pks = [str(x.pk) for x in queryset.all()]
        url = '%s?codes=%s' % (reverse('admin:admin_qr_download'), ','.join(pks))
        return redirect(url)

    download_codes_action.short_description = 'Download codes'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'department' and not request.user.is_superuser:
            kwargs['queryset'] = request.user.departments
        return super(QRCodeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        urls = super(QRCodeAdmin, self).get_urls()
        custom_urls = [
            path('download/', self.admin_site.admin_view(self.download_codes), name='admin_qr_download')
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

    def download_codes(self, request):
        pks = [int(x) for x in request.GET['codes'].split(',')]
        codes = QRCode.objects.filter(pk__in=pks, department__in=request.user.departments.all()).all()
        if request.method == 'POST':
            form = QrGenerateForm(data=request.POST)
            if form.is_valid():
                zf = generate_qr_zip(codes, form)
                resp = HttpResponse(zf, content_type="application/x-zip-compressed")
                resp['Content-Disposition'] = f'attachment; filename=generated_codes.zip'
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


admin.site.site_header = 'Qr Gent Administration'
admin.site.site_title = 'Qr Gent admin'
admin.site.site_url = settings.API_URL
