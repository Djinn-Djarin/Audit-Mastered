from django.urls import path
from . import views

urlpatterns = [
    path('create_product_list/', views.CreateProductList.as_view(), name='create_product_list'),
    path('get_all_product_list/', views.GetAllProductLists.as_view(), name='get_all_product_list'),
    path('get_product_list_info/<int:list_id>/', views.GetProductListItems.as_view(), name='get_product_list_info'),
    path('add_items_to_product_list/', views.AddItemsToProductList.as_view(), name='add_items_to_product_list'),
    path('run_audit/', views.RunAudit.as_view(), name='create_product_list'),
    path('delete_list/<int:pk>/', views.DeleteProductList.as_view(), name='delete_list'),
    path('audit_task_status/', views.AuditTaskStatus.as_view(), name='audit_task_status'),

]
