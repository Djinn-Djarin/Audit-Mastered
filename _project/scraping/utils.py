from django.http import HttpResponse
from .models import ProductList
import pandas as pd


class JsonToExcel:
    def __init__(self, json_data):
        self.json_data = json_data

    def convert(self, output_file):
        import pandas as pd

        df = pd.DataFrame(self.json_data)
        df.to_excel(output_file, index=False)

        # send this excel file as a response in your view
        return output_file


class ProductListExcelExporter:
    """
    Handles the logic for exporting product list items to Excel.
    Single Responsibility: Only handles export logic.
    """

    @staticmethod
    def export(product_list: ProductList):
        product_items = product_list.products_list.all()
        data = [
            {
                "Product ID": item.product_id,
                "Title": item.title,
                "Price": item.price,
                "MRP": item.mrp,
                "Availability": item.availability,
                "Status": item.status,
                "Reviews": item.reviews,
                "Ratings": item.ratings,
                "deal": item.deal,
                "Brand": item.brand_name,
                "Browsr Node": item.browse_node,
                "Variations": item.variations,
                "Seller": item.seller,
                "Variations": item.variations,
                "Main Image": item.main_img_url,
            }
            for item in product_items
        ]
        df = pd.DataFrame(data)
        return df


# === Export Excel ===
class ExcelExport:
    @staticmethod
    def export(df, filename):
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        
        import urllib.parse

        safe_filename = urllib.parse.quote(f"{filename}.xlsx")
        response["Content-Disposition"] = f'attachment; filename="{safe_filename}"'
        with pd.ExcelWriter(response, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Products")
        return response


# Ping Celery
from rest_framework.response import Response
from rest_framework import status
from celery import current_app


def ping_celery(timeout=1):
    try:
        result = current_app.control.ping(timeout=timeout)
        return bool(result)  # True if at least one worker responded
    except Exception:
        return False


