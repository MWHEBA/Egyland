from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'inquiries'

urlpatterns = [
    # Frontend URLs - معطلة لصالح المودال
    path('product-inquiry/', RedirectView.as_view(url='/', permanent=False), name='product_inquiry'),
    path('product-request/', views.ProductRequestFormView.as_view(), name='product_request'),
    
    # API URLs - للاستفسارات عبر AJAX
    path('api/submit-inquiry/', views.submit_inquiry_via_ajax, name='submit_inquiry_api'),
    path('api/products/', views.products_api, name='products_api'),  # API للحصول على قائمة المنتجات
    
    # Dashboard URLs
    path('dashboard/inquiries/', views.InquiryListView.as_view(), name='list'),
    path('dashboard/inquiries/<int:pk>/', views.InquiryDetailView.as_view(), name='detail'),
    path('dashboard/inquiries/<int:pk>/update-status/', views.update_inquiry_status, name='update_status'),
] 