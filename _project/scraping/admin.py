from django.contrib import admin
from .models import ProductInfo, ProductList


# --- ProductInfo Admin ---
@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ["product_id", "user", "title", "price", "status"]
    search_fields = ["product_id", "title", "user__username"]
    list_filter = ["status", "brand_name"]


@admin.register(ProductList)
class ProductListAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "created_at", "product_ids"]
    search_fields = ["name", "user__username"]

    def product_ids(self, obj):
        return obj.products_list.count()

    product_ids.short_description = "Products in List"
