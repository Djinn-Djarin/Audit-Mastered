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
        product_items = product_list.products.all()
        data = [
            {
                "Product ID": item.product_info.product_id,
                "Title": item.product_info.title,
                "Price": item.product_info.price,
                "Status": item.product_info.status,
                "Brand": item.product_info.brand_name,
            }
            for item in product_items
        ]
        df = pd.DataFrame(data)
        return df
    

# === Export Excel ===
class ExcelExport:
    @staticmethod
    def export( df, filename):
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Products')
        return response
