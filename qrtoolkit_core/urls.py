from django.urls import path
from django.urls.conf import include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from . import views
from . import viewsets

router = routers.DefaultRouter()
router.register(r'qrcodes', viewsets.CodeViewSet, basename='api-code')
router.register(r'apihits', viewsets.ApiHitViewSet, basename='api-apihit')
router.register(r'departments', viewsets.DepartmentViewSet, basename='api-department')
router.register(r'urls', viewsets.LinkUrlViewSet, basename='api-url')
# router.register(r'users', viewsets.UserViewSet, basename='api-user')

api_routes = [path('', include(router.urls)),
              path('users/', viewsets.UserViewSet.as_view(), name='api-user'),
              path('openapi/', get_schema_view(
                  title="Qr code Toolkit API",
                  description="Stad Gent qr code toolkit",
                  version="1.0.0",
                  patterns=router.urls,
                  url='/api/'
              ), name='openapi-schema')
              ]


def _get_code_routes():
    redirect_routes = [
        # url that ill be scanned
        path('<slug:short_uuid>/', views.QRCodeDetails.as_view(), name='qrcode-detail')
    ]
    # enable content negotiation on scan url
    redirect_routes = format_suffix_patterns(redirect_routes, allowed=['html', 'json'])
    info_routes = [
        path('code/<slug:short_uuid>/', views.CodeView.as_view(), name='code-detail'),
    ]
    link_url_routes = [
        path('call/<int:pk>/', views.link_url_clicked, name='link_url_clicked')
    ]
    return redirect_routes + info_routes + link_url_routes


code_routes = _get_code_routes()
