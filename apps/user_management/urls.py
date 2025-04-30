from django.urls import path
from . import views

app_name = 'dashboard_user_management'

urlpatterns = [
    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/roles/', views.assign_role, name='assign_role'),
    
    # Role management - الأدوار ثابتة ولا يمكن إضافتها أو تعديلها أو حذفها
    path('roles/', views.role_list, name='role_list'),
    path('roles/<int:role_id>/', views.role_detail, name='role_detail'),
] 