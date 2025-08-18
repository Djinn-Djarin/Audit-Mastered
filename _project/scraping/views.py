import json
import redis
import requests
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from celery.result import AsyncResult

from .bulk_create_product import ProductService
from .file_parsing import FileParser

from .tasks import run_audit_task
from .models import ProductList, ProductInfo
from .utils import ProductListExcelExporter, ExcelExport, ping_celery
from .Audit.utils import TaskProgress


r = redis.Redis(host="localhost", port=6379, db=0)
from django.contrib.auth import get_user_model
User = get_user_model()

# === Create a ProductList  ===
class CreateProductList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("list_name")
        platform = request.data.get("platform")

        check_product_list = ProductList.objects.filter(
            user=request.user, name=name, platform=platform
        ).first()
        if check_product_list:
            return Response(
                {"status": "error", "message": "Product list already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product_list = ProductList.objects.create(user=request.user, name=name, platform=platform)
        return Response(
            {
                "status": "success",
                "message": f"Product list created {product_list.id} {product_list.name}",
            },
            status=status.HTTP_201_CREATED,
        )


# === Delete a ProductList  ===
class DeleteProductList(APIView):
    permission_classes = []

    def delete(self, request, pk):
        """Delete a product list by ID."""
        try:
            product_list = ProductList.objects.get(id=pk, user=request.user)
            product_list.delete()
            return Response(
                {"message": "Product list deleted"}, status=status.HTTP_200_OK
            )
        except ProductList.DoesNotExist:
            return Response(
                {"error": "Product list not found"}, status=status.HTTP_404_NOT_FOUND
            )


# === Get all ProductLists of a user ===
class GetAllProductLists(APIView):
    permission_classes = []

    def get(
        self,
        request,
    ):
        try:
            product_list = ProductList.objects.filter(user=request.user)
            if product_list.count() == 0:
                return Response(
                    {"message": "No product lists found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            data = [
                {
                    "id": pl.id,
                    "name": pl.name,
                    "created_at": pl.created_at,
                    "product_count": pl.products_list.count(),
                }
                for pl in product_list
            ]
            return Response(
                {"data": data, "message": "success"}, status=status.HTTP_200_OK
            )
        except ProductList.DoesNotExist:
            return Response(
                {"error": "Product list not found"}, status=status.HTTP_404_NOT_FOUND
            )


# === Add Products to a ProductList ===
class AddItemsToProductList(APIView):
    permission_classes = []

    def post(self, request):
        file = request.FILES.get("file")
        list_id = request.data.get("list_id")
        request.user = User.objects.get(username="admin")

        if not file:
            raise ValidationError({"detail": "File is required"})

        # Parse the file into a cleaned dataframe

        # Get the target product list for the current user
        try:
            product_list = ProductList.objects.get(id=list_id, user=request.user)
            platform = product_list.platform
        except ProductList.DoesNotExist:
            return Response(
                {"error": "Product list not found"}, status=status.HTTP_404_NOT_FOUND
            )

        file_validator = FileParser(file, platform)
        try:
            cleaned_dataframe = file_validator.parse()
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        product_ids = cleaned_dataframe[product_list.platform].to_list()
        # Use the platform from the existing list
        _, created_products = ProductService.bulk_create_products(
            user=request.user,
            product_ids=product_ids,
            platform=platform,
            product_list=product_list,
        )

        return Response(
            {
                "status": "success",
                "message": f"{len(created_products)} products added to list '{product_list.name}'",
                "products": [str(p) for p in created_products],
            },
            status=status.HTTP_201_CREATED,
        )


# === All items of a ProductList ===
class GetProductListItems(APIView):
    permission_classes = []

    def get(self, request, list_id):
        try:
            product_list = ProductList.objects.get(id=list_id, user=request.user)
            products = product_list.products_list.all()  # related_name from ProductInfo

            data = []
            for product in products:
                product_data = {}
                for field in product._meta.fields:
                    value = getattr(product, field.name)
                    # Convert foreign keys to string or ID
                    if field.many_to_one:  # i.e., ForeignKey
                        if field.name == "user":
                            value = value.username  # show username instead of object
                        elif field.name == "product_list":
                            value = value.name  # show product list name
                        else:
                            value = value.id  # fallback to id
                    product_data[field.name] = value
                data.append(product_data)

            return Response(
                {"data": data, "message": "success"}, status=status.HTTP_200_OK
            )

        except ProductList.DoesNotExist:
            return Response(
                {"error": "Product list not found"}, status=status.HTTP_404_NOT_FOUND
            )


# === Get Excel Sheet of all the product under a list after Audit  ===
class GetProductListItemsExcel(APIView):
    permission_classes = []

    def get(self, request):
        # user = request.user
        user = User.objects.get(username="admin")
        product_list_id = request.query_params.get("product_list")

        if not product_list_id:
            return HttpResponse("Product list ID is required", status=400)

        product_list = self._get_product_list(product_list_id, user)
        if not product_list:
            return HttpResponse("Product list not found", status=404)

        df = ProductListExcelExporter.export(product_list)
        response = self._build_excel_response(df, product_list.name, product_list_id)
        return response

    def _get_product_list(self, product_list_id, user):
        try:
            return ProductList.objects.get(id=product_list_id, user=user)
        except ProductList.DoesNotExist:
            return None

    def _build_excel_response(self, df, filename, product_list_id):
        response = ExcelExport.export(df, filename, sheet_name=product_list_id)
        return response


# === Run Audit for a Product List ===
class RunAudit(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        if not ping_celery():
            return Response(
                {"detail": "Celery Service is Down"}, status=status.HTTP_400_BAD_REQUEST
            )
        product_list_id = request.data.get("product_list_id")
        
        reaudit = False
        if request.data.get("reaudit"):
            reaudit = request.data.get("reaudit").lower() == True

        product_list_id = request.data.get("product_list_id")
        if not product_list_id:
            return Response(
                {"detail": "Product list ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(username="admin")
            product_list = ProductList.objects.get(id=product_list_id, user=user)

            AUDIT_INSTANCE_COUNTER = "AUDIT_INSTANCES_"
            r.incr(AUDIT_INSTANCE_COUNTER)
            try:
                task = run_audit_task.delay(product_list.id, reaudit)
                return Response(
                    {
                        "message": f"Audit started for {product_list.name}",
                        "task_id": task.id,
                    },
                    status=status.HTTP_202_ACCEPTED,
                )
            finally:
                r.decr(AUDIT_INSTANCE_COUNTER)

        except ProductList.DoesNotExist:
            return Response(
                {"detail": "Product list not found"}, status=status.HTTP_404_NOT_FOUND
            )


# === Check Audit Status ===
class AuditTaskStatus(APIView):
    def post(self, request):
        task_id = request.data.get("task_id")
        if not task_id:
            return Response(
                {"error": "task_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = AsyncResult(task_id)

        # Make sure result.result is JSON-safe
        safe_result = None
        if result.ready():
            try:
                safe_result = str(result.result)
            except Exception as e:
                safe_result = f"Unserializable result: {e}"

        return Response(
            {
                "task_id": task_id,
                "status": result.status,  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
                "result": safe_result,
            },
            status=status.HTTP_200_OK,
        )


# === Progress Bar of an Audit over SSR ===
class AuditStreamingSSR(APIView):
    permission_classes = []

    def get(self, request, task_id):

        pubsub = r.pubsub()
        pubsub.subscribe(f"task_updates:{task_id}")  # subscribe to this task's channel

        def event_stream():
            for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                progress = json.loads(message["data"])
                if not progress:
                    yield b"event: error\ndata: Task not found\n\n"
                    break

                user_id = progress.get("user_id")
                if request.user.id != user_id and not request.user.is_staff:
                    yield b"event: error\ndata: Unauthorized\n\n"
                    break

                processed = progress.get("count", 0)
                total = progress.get("total", 0)

                yield f"data: {json.dumps(progress)}\n\n".encode("utf-8")

                if total > 0 and processed >= total:
                    yield f"event: complete\ndata: {json.dumps(progress)}\n\n".encode("utf-8")
                    break

        return StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )


# === Progress Bar of All Aduit over == 
class GlobalProgressBar(APIView):
    permission_classes = []

    def get(self, request):
        pubsub = r.pubsub()
        # pattern subscribe to all task channels
        pubsub.psubscribe("task_updates:*")

        def event_stream():
            for message in pubsub.listen():
                # pattern subscription messages have type 'pmessage'
                if message['type'] != 'pmessage':
                    continue

                data = json.loads(message['data'])
                # you can also include the task_id from message['channel']
                task_channel = message['channel']
                task_id = task_channel.split(":")[1]
                data['task_id'] = task_id

                yield f"data: {json.dumps(data)}\n\n"

        return StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream',
            headers={"Cache-Control": "no-cache"}
        )


# === High Prority Audit ===
class HighPriorityAudit(APIView):
    pass


### ============================================================ SYSTEM LEVEL VIEWS ====================================================== ###


# === Audit Speed of the system ===
class AuditSpeed(APIView):
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

# === Get Public IP ===
class GetPublicIP(APIView):
    permission_classes = []

    def get(self, request):
        """
        Get the public IP address of the server.
        """
        try:
            response = requests.get("https://api.ipify.org?format=json")
            response.raise_for_status()
            ip_data = response.json()
            return Response(
                {"public_ip": ip_data["ip"]}, status=status.HTTP_200_OK
            )
        except requests.RequestException as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# === Check Internet Connection ===
class CheckInternetConnection(APIView):
    def get(self, request):
        try:
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                return Response(
                    {"status": "Internet is connected"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "Internet is not connected"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
        except requests.ConnectionError:
            return Response(
                {"status": "Internet is not connected"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

# === check Redis connection ===
class CheckRedisConnection(APIView):
    def get(self, request):
        try:
            r.ping()
            return Response({"status": "Redis is connected"}, status=status.HTTP_200_OK)
        except redis.ConnectionError as e:
            return Response(
                {"status": "Redis is not connected", "error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


# === Check Celery Connection ===
class CheckCeleryConnection(APIView):
    def get(self, request):
        from celery import current_app

        try:
            result = current_app.control.ping(timeout=1)
            if result:
                return Response(
                    {"status": "Celery is connected"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"status": "No Celery workers responded"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
        except Exception as e:
            return Response(
                {"status": "Celery is not connected", "error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


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
            product_count = sum(pl.products.count() for pl in product_lists)
            stats = {
                "user_id": user.id,
                "username": user.username,
                "product_list_count": product_lists.count(),
                "product_count": product_count,
            }
            return Response(stats, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
