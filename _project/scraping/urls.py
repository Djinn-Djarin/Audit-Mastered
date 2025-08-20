from django.urls import path
from . import views

urlpatterns = [
    path(
        "create_product_list/",
        views.CreateProductList.as_view(),
        name="create_product_list",
    ),
    path(
        "get_all_lists/",
        views.GetAllProductLists.as_view(),
        name="get_all_lists",
    ),
    path(
        "get_product_list_info/<int:list_id>/",
        views.GetProductListItems.as_view(),
        name="get_product_list_info",
    ),
    path(
        "add_items_to_product_list/",
        views.AddItemsToProductList.as_view(),
        name="add_items_to_product_list",
    ),
    path("run_audit/", views.RunAudit.as_view(), name="create_product_list"),
    path("stop_audit/", views.StopCeleryTask.as_view(), name="stop_celery_task"),
    path(
        "delete_list/<int:pk>/", views.DeleteProductList.as_view(), name="delete_list"
    ),
    path(
        "audit_task_status/", views.AuditTaskStatus.as_view(), name="audit_task_status"
    ),
    # === Audit Streaming ===
    path('tasks_sse/<str:task_id>/', views.AuditStreamingSSR.as_view(), name='task-progress-sse'),
    # === GET SSE Streaming of ALL Tasks === 
    path('all_tasks/', views.GlobalProgressBar.as_view(), name='task-progress-sse'), 
    # === get celery task ids for a user ===
    path('all_task_ids/', views.RunningAudits.as_view(), name='all_task_ids'), 


    path("export-audit/", views.GetProductListItemsExcel.as_view(), name="export_audit"),

    # === Check Celery Worker ===
    path(
        "check_celery_service/",
        views.CheckCeleryConnection.as_view(),
        name="check_celery_worker",
    ),

    path('backend_ip/', views.GetPublicIP.as_view(), name='backend_ip'),
]
