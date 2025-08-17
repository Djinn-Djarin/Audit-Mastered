from rest_framework.serializers import ModelSerializer
from .models import ProductList, ProductInfo


class ProductListSerializer(ModelSerializer):
    class Meta:
        model = ProductList
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ProductInfoSerializer(ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
