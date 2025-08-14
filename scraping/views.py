import redis
import pandas as pd

from django.http import HttpResponse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError


from .bulk_create_product import ProductService
from .file_parsing import FileParser

from .tasks import run_audit_task
from .Audit.audit import RunAudit
from .models import ProductList, ProductInfo, ProductListItem
from .utils import ProductListExcelExporter, ExcelExport




r = redis.Redis(host='localhost', port=6379, db=0)

# === Add a new Product List for Audit === 
class CreateProductList(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        column_name = request.data.get("column_name")
        audit_platform = request.data.get("audit_platform")

        if not file or not column_name or not audit_platform:
            raise ValidationError({"detail": "File and column_name are required"})
        
        file_validator  = FileParser(file)
        try:
            cleaned_dataframe = file_validator.parse()

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        admin_user = User.objects.get(username='admin')
        products = ProductService.bulk_create_products(
            user= admin_user,
            product_ids=cleaned_dataframe[column_name].tolist(),
            audit_platform=audit_platform
        )

        return Response(
            {"message": f"{len(products)} products created successfully", "products": [str(p) for p in products]},
            status=status.HTTP_201_CREATED
        )
    
# === Delete a Product List ===
class DeleteProductList(APIView):
    permission_classes = []
    def delete(self, request, *args, **kwargs):
        product_list_id = request.data.get("product_list_id")
        if not product_list_id:
            return Response({"detail": "Product list ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_list = ProductList.objects.get(id=product_list_id)
            product_list.delete()
            return Response({"message": "Product list deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProductList.DoesNotExist:
            return Response({"detail": "Product list not found"}, status=status.HTTP_404_NOT_FOUND)
        

# === Get all created list from a user ===          
class GetAllProductLists(APIView):
    permission_classes = []
    def get(self, request, *args, **kwargs):
        admin_user = User.objects.get(username='admin')
        product_lists = ProductList.objects.filter(user=admin_user)
        data = [{"id": pl.id, "name": pl.name} for pl in product_lists]
        return Response(data, status=status.HTTP_200_OK)


# === Get Excel Sheet of all the product under a list after Audit  === 
class GetProductListItemsExcel(APIView):
    permission_classes = []

    def get(self, request):
        # user = request.user
        user = User.objects.get(username='admin')
        product_list_id = request.query_params.get('product_list')

        if not product_list_id:
            return HttpResponse("Product list ID is required", status=400)

        product_list = self._get_product_list(product_list_id, user)
        if not product_list:
            return HttpResponse("Product list not found", status=404)

        df = ProductListExcelExporter.export(product_list)
        response = self._build_excel_response(df, product_list.name,product_list_id)
        return response

    def _get_product_list(self, product_list_id, user):
        try:
            return ProductList.objects.get(id=product_list_id, user=user)
        except ProductList.DoesNotExist:
            return None

    def _build_excel_response(self, df, filename, product_list_id):  
        response  = ExcelExport.export(df, filename, sheet_name = product_list_id)
        return response

# === Run Audit for a Product List ===
class RunAudit(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        product_list_id = request.data.get("product_list_id")
        if not product_list_id:
            return Response({"detail": "Product list ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username='admin')
            product_list = ProductList.objects.get(id=product_list_id, user=user)

            AUDIT_INSTANCE_COUNTER = 'AUDIT_INSTANCES_'
            r.incr(AUDIT_INSTANCE_COUNTER)
            try:
                run_audit_task.delay(product_list.id)
            finally:
                r.decr(AUDIT_INSTANCE_COUNTER)

        except ProductList.DoesNotExist:
            return Response({"detail": "Product list not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": f"Audit started for {product_list.name}"}, status=status.HTTP_200_OK)

# === Streaming of an Audit over SSR ===
class AuditStreamingSSR:
    pass

# === Global counter for a distributed product list ===
class ProductListGloabalCounter(APIView):
    pass

# == Get Reaudit of incomplete audits ===
class ReauditIncompleteAudits(APIView):
    pass


# === High Prority Audit ===
class HighPriorityAudit(APIView):
    pass


### ============================================================ SYSTEM LEVEL VIEWS ====================================================== ###

# === Audit Speed of the system ===
class AuditSpeed(APIView):
    pass

# === Current Running Audits ===
class CurrentRunningAudits(APIView):
    pass


# === Test the Audit Health ===
class AuditHealthCheckAmazon(APIView):
    def title(self, request):
        pass
    def price(self, request):
        pass
    def review(self, request):
        pass


class AuditHealthCheckFlipkart(APIView):
    def title(self, request):
        pass
    def price(self, request):
        pass
    def review(self, request):
        pass

class AuditHealthCheckMyntra(APIView):
    def title(self, request):
        pass
    def price(self, request):
        pass
    def review(self, request):
        pass


# === IP Health Check ===
class IPHealthCheck(APIView):
    pass


# === Check Internet Connection ===
class CheckInternet:
    pass

# === check Redis connection ===
class CheckRedisConnection(APIView):
    def get(self, request):
        try:
            r.ping()
            return Response({"status": "Redis is connected"}, status=status.HTTP_200_OK)
        except redis.ConnectionError as e:
            return Response({"status": "Redis is not connected", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# === Check Celery Connection ===
class CheckCeleryConnection(APIView):

    def get(self, request):
        try:
            from celery import current_app
            if current_app.control.ping(timeout=1):
                return Response({"status": "Celery is connected"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "Celery is not connected", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# === User and Product stats ===
class UserProductStats(APIView):
    def get_all_users(self, request):
        users = User.objects.all()
        data = [{"id": user.id, "username": user.username} for user in users]
        return Response(data, status=status.HTTP_200_OK)
    
    def get_user_product_stats(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            product_lists = ProductList.objects.filter(user=user)
            stats = {
                "user_id": user.id,
                "username": user.username,
                "product_list_count": product_lists.count(),
                "product_count": ProductListItem.objects.filter(product_list__in=product_lists).count()
            }
            return Response(stats, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
