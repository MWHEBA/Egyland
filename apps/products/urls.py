from django.urls import path, re_path
from . import views

app_name = 'products'

urlpatterns = [
    # API مسارات - أكثر من مسار للأمان
    path('api/products/list/', views.products_list_api, name='products_list_api'),
    re_path(r'^products/api/list/?$', views.products_list_api, name='products_list_api_alt'),
    
    # العرض الأساسي
    path('', views.ProductListView.as_view(), name='product_list'),
    path('variety/<int:pk>/', views.VarietyDetailView.as_view(), name='variety_detail'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('special/create/', views.SpecialProductCreateView.as_view(), name='special_product_create'),
    path('special/<slug:slug>/edit/', views.SpecialProductUpdateView.as_view(), name='special_product_edit'),
] 