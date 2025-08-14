from django.urls import path
from . import views

urlpatterns = [
    path('create_product_list/', views.CreateProductList.as_view(), name='create_product_list'),
    path('get_all_product_list/', views.GetAllProductLists.as_view(), name='create_product_list'),
    path('run_audit/', views.RunAudit.as_view(), name='create_product_list'),

]
