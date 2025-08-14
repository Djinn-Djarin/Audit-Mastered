from django.contrib import admin
from .models import ProductInfo, ProductList, ProductListItem

# --- ProductInfo Admin ---
@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'user', 'title', 'price', 'status']
    search_fields = ['product_id', 'title', 'user__username']
    list_filter = ['status', 'brand_name']

# --- ProductList Admin (shows grouped ProductListItems) ---
@admin.register(ProductList)
class ProductListAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'product_ids']
    search_fields = ['name', 'user__username']

    def product_ids(self, obj):
        # Join all product IDs for this list in one string
        items = obj.items.select_related('product_info').all()
        return ", ".join([item.product_info.product_id for item in items])
    
    product_ids.short_description = "Products in List"

# --- ProductListItem Admin (optional, raw view) ---
@admin.register(ProductListItem)
class ProductListItemAdmin(admin.ModelAdmin):
    list_display = ['product_list', 'product_info']
    search_fields = ['product_list__name', 'product_info__product_id']
    list_filter = ['product_list__user']
