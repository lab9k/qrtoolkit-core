from rest_framework.viewsets import GenericViewSet

from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, DateTimeFilter, NumberFilter

from .serializers import QRCodeSerializer, ApiHitSerializer, DepartmentSerializer, LinkUrlSerializer
from .models import ApiHit, QRCode, Department, LinkUrl


class CodeViewSet(viewsets.ModelViewSet):
    serializer_class = QRCodeSerializer
    queryset = QRCode.objects.order_by('-last_updated')
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('mode', 'title', 'created', 'last_updated', 'uuid', 'department__name', 'short_uuid')


class ApiHitFilterSet(FilterSet):
    dept = CharFilter(field_name="code__department__name", lookup_expr='icontains', label='Department name')
    dept_id = NumberFilter(field_name='code__department__id', lookup_expr='exact', label='Department id')
    action = CharFilter(field_name='action', lookup_expr='icontains')
    hit_date = DateTimeFilter(field_name='hit_date')


class ApiHitViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ApiHitSerializer
    queryset = ApiHit.objects.all()
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filter_class = ApiHitFilterSet


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class LinkUrlViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    serializer_class = LinkUrlSerializer
    queryset = LinkUrl.objects.all()
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('code',)
