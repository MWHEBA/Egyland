from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from apps.branches.views import BranchListView, BranchCreateView, BranchUpdateView, BranchDeleteView, MainBranchUpdateView, BranchDetailAPIView

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    
    # Products Management
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Product Attributes Management
    path('products/varieties/', views.VarietyListView.as_view(), name='varieties'),
    path('products/varieties/add/', views.VarietyCreateView.as_view(), name='variety_add'),
    path('products/varieties/<int:pk>/edit/', views.VarietyUpdateView.as_view(), name='variety_edit'),
    path('products/varieties/<int:pk>/delete/', views.VarietyDeleteView.as_view(), name='variety_delete'),
    
    # Variety API for modal editing
    path('api/varieties/<int:pk>/', views.variety_detail_api, name='variety_detail_api'),
    
    path('products/seasonality/', views.SeasonalityListView.as_view(), name='seasonality'),
    path('products/seasonality/add/', views.SeasonalityCreateView.as_view(), name='seasonality_add'),
    path('products/seasonality/<int:pk>/edit/', views.SeasonalityUpdateView.as_view(), name='seasonality_edit'),
    path('products/seasonality/<int:pk>/delete/', views.SeasonalityDeleteView.as_view(), name='seasonality_delete'),
    
    path('products/sizes/', views.SizeListView.as_view(), name='sizes'),
    path('products/sizes/add/', views.SizeCreateView.as_view(), name='size_add'),
    path('products/sizes/<int:pk>/edit/', views.SizeUpdateView.as_view(), name='size_edit'),
    path('products/sizes/<int:pk>/delete/', views.SizeDeleteView.as_view(), name='size_delete'),
    
    path('products/counts/', views.CountListView.as_view(), name='counts'),
    path('products/counts/add/', views.CountCreateView.as_view(), name='count_add'),
    path('products/counts/<int:pk>/edit/', views.CountUpdateView.as_view(), name='count_edit'),
    path('products/counts/<int:pk>/delete/', views.CountDeleteView.as_view(), name='count_delete'),
    
    # أنواع التغليف الجديدة
    path('products/packaging-types/', views.PackagingTypeListView.as_view(), name='packaging_types'),
    path('products/packaging-types/add/', views.PackagingTypeCreateView.as_view(), name='packaging_type_add'),
    path('products/packaging-types/<int:pk>/edit/', views.PackagingTypeUpdateView.as_view(), name='packaging_type_edit'),
    path('products/packaging-types/<int:pk>/delete/', views.PackagingTypeDeleteView.as_view(), name='packaging_type_delete'),
    
    # أنواع التغليف المودال
    path('products/packaging-types/modal/add/', views.packaging_type_create_modal, name='packaging_type_modal_add'),
    path('products/packaging-types/modal/<int:pk>/edit/', views.packaging_type_update_modal, name='packaging_type_modal_edit'),
    path('products/packaging-types/modal/<int:pk>/delete/', views.packaging_type_delete_modal, name='packaging_type_modal_delete'),
    
    # ربط المنتجات بأنواع التغليف
    path('products/product-packaging-types/', views.ProductPackagingTypeListView.as_view(), name='product_packaging_types'),
    path('products/product-packaging-types/add/', views.ProductPackagingTypeCreateView.as_view(), name='product_packaging_type_add'),
    path('products/product-packaging-types/<int:pk>/edit/', views.ProductPackagingTypeUpdateView.as_view(), name='product_packaging_type_edit'),
    path('products/product-packaging-types/<int:pk>/delete/', views.ProductPackagingTypeDeleteView.as_view(), name='product_packaging_type_delete'),
    
    # Season Icons
    path('season-icons/', views.SeasonIconListView.as_view(), name='season_icons'),
    path('season-icons/add/', views.SeasonIconCreateView.as_view(), name='season_icon_add'),
    path('season-icons/<int:pk>/edit/', views.SeasonIconUpdateView.as_view(), name='season_icon_edit'),
    path('season-icons/<int:pk>/delete/', views.SeasonIconDeleteView.as_view(), name='season_icon_delete'),
    path('season-icons/<int:pk>/', views.season_icon_detail_api, name='season_icon_detail_api'),
    
    # Inquiries / Contact Messages
    path('inquiries/', views.InquiryListView.as_view(), name='inquiries'),
    path('inquiries/<int:pk>/', views.InquiryDetailView.as_view(), name='inquiry_detail'),
    path('inquiries/<int:pk>/update-status/', views.update_inquiry_status, name='update_inquiry_status'),
    path('inquiries/<int:pk>/add-note/', views.add_inquiry_note, name='add_inquiry_note'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/change-password/', auth_views.PasswordChangeView.as_view(
        template_name='dashboard/password_change.html',
        success_url=reverse_lazy('dashboard:password_change_success')
    ), name='password_change'),
    path('profile/change-password/success/', views.password_change_success, name='password_change_success'),
    
    # Branches Management
    path('branches/', BranchListView.as_view(), name='branches'),
    path('branches/add/', BranchCreateView.as_view(), name='branch_add'),
    path('branches/<int:pk>/edit/', BranchUpdateView.as_view(), name='branch_edit'),
    path('branches/<int:pk>/delete/', BranchDeleteView.as_view(), name='branch_delete'),
    path('branches/<int:pk>/get-data/', BranchDetailAPIView.as_view(), name='branch_detail_api'),
    path('branches/main/', MainBranchUpdateView.as_view(), name='main_branch'),
    
    # تبديل وضع تحت الإنشاء
    path('toggle-construction/', views.toggle_construction_mode, name='toggle_construction'),
]
