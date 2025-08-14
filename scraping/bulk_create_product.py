from .models import ProductInfo, ProductList, ProductListItem
from django.utils import timezone

class ProductService:
    @staticmethod
    def bulk_create_products(user, product_ids, audit_platform):
        # 1️⃣ Create a ProductList for this batch
        product_list = ProductList.objects.create(user=user)

        # 2️⃣ Prepare ProductInfo objects
        product_infos = []
        for pid in product_ids:
            if pid:  # skip empty
                product_infos.append(ProductInfo(
                    user=user,
                    product_id=pid
                ))

        # 3️⃣ Bulk create ProductInfo, ignoring conflicts (unique_together)
        ProductInfo.objects.bulk_create(product_infos, ignore_conflicts=True)

        # 4️⃣ Fetch all ProductInfo objects for these IDs (in case some already existed)
        created_products = ProductInfo.objects.filter(user=user, product_id__in=product_ids)

        # 5️⃣ Create ProductListItem links
        product_list_items = [
            ProductListItem(product_list=product_list, product_info=pi)
            for pi in created_products
        ]
        ProductListItem.objects.bulk_create(product_list_items, ignore_conflicts=True)

        print(f"AUDIT: {len(product_ids)} products added to list '{product_list.name}' for {user.username} via {audit_platform}")
        return product_list, created_products
