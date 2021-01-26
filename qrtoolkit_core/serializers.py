from rest_framework import serializers
from .models import Department, LinkUrl, QRCode, ApiHit


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class LinkUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkUrl
        fields = '__all__'


class QRCodeSerializer(serializers.ModelSerializer):
    urls = LinkUrlSerializer(many=True, read_only=True)
    department = DepartmentSerializer(read_only=True)

    # image_url = serializers.SerializerMethodField(method_name='get_image_url', read_only=True)
    # download_url = serializers.SerializerMethodField(method_name='get_dl_url', read_only=True)

    def create(self, validated_data):
        validated_dept = validated_data.pop('department')
        dept, created = Department.objects.get_or_create(name=validated_dept['name'])
        code = QRCode.objects.create(**validated_data, department=dept)
        return code

    # def get_image_url(self, obj):
    #     path = reverse('code-detail', kwargs={'short_uuid': obj.short_uuid})
    #     url = self.context['request'].build_absolute_uri(path)
    #     return url
    #
    # def get_dl_url(self, obj):
    #     path = reverse('code-dl', kwargs={'short_uuid': obj.short_uuid})
    #     url = self.context['request'].build_absolute_uri(path)
    #     return url

    class Meta:
        model = QRCode
        fields = '__all__'
        read_only_fields = ['created', 'last_updated']


class ApiHitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiHit
        fields = '__all__'
