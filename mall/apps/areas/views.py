from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Area
from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import AreaSerializer,SubAreaSerializer
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class AreaViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """
    行政区信息
    list: GET /areas/
    retrieve: GET /areas/(?P<pk>\d+)/
    """
    pagination_class = None  # 区划信息不分页

    def get_queryset(self):
        """
        提供数据集

        """
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """
        提供序列化器

        """
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer
