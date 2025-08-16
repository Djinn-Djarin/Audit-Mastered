from .models import ProductInfo, ProductList

class ProductService:
    @staticmethod
    def bulk_create_products(user, product_ids, platform,product_list):
        """
        Bulk create products for a given ProductList using ForeignKey relation.
        Ensures no duplicates per list.
        """
        # Filter out IDs already in this list
        existing_ids = set(
            ProductInfo.objects.filter(product_list=product_list)
                               .values_list("product_id", flat=True)
        )
        new_ids = [pid for pid in product_ids if pid and pid not in existing_ids]

        # Create ProductInfo with FK to product_list
        product_infos = [
            ProductInfo(user=user, product_list=product_list, product_id=pid)
            for pid in new_ids
        ]

        ProductInfo.objects.bulk_create(product_infos, ignore_conflicts=True)

        print(f"AUDIT: {len(new_ids)} products added to list" )
        return product_list, product_infos
