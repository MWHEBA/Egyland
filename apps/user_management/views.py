from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from datetime import timedelta

from .models import Role, UserRole
from .forms import (
    AdminUserCreationForm, AdminUserEditForm, AdminPasswordChangeForm,
    UserRoleForm
)

import logging
logger = logging.getLogger('user_management')

# Check if user is admin or developer
def is_admin(user):
    """
    Check if user has admin permissions
    """
    # If user is staff or superuser
    if user.is_staff or user.is_superuser:
        return True
    
    # Or has a role with user management permissions
    try:
        return user.user_roles.filter(role__name__in=[Role.DEVELOPER, Role.ADMIN]).exists()
    except:
        return False


# Get client IP address
def get_client_ip(request):
    """
    Get client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


# User Management
@login_required
@user_passes_test(is_admin)
def user_list(request):
    """
    Display list of users
    """
    users_list = User.objects.all().order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users_list, 20)  # 20 users per page
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
    }
    
    return render(request, 'dashboard/user_management/user_list.html', context)


@login_required
@user_passes_test(is_admin)
def create_user(request):
    """
    Create new user
    """
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            logger.info(f"User {user.username} created by {request.user.username}")
            messages.success(request, _('User created successfully!'))
            return redirect('user_management:user_detail', user_id=user.id)
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'dashboard/user_management/user_form.html', {
        'form': form,
        'title': _('Create New User')
    })


@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """
    View user details
    """
    user = get_object_or_404(User, id=user_id)
    
    # Get user roles without using assigned_at
    user_roles_query = UserRole.objects.filter(user=user).select_related('role')
    
    # Create cleaned user_roles list without using assigned_at
    user_roles = []
    for user_role in user_roles_query:
        user_roles.append({
            'role': user_role.role,
            'role_name': user_role.role.name if hasattr(user_role.role, 'name') else ''
        })
    
    context = {
        'user_profile': user,
        'user_roles': user_roles,
    }
    
    return render(request, 'dashboard/user_management/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    """
    Edit user
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_form = AdminUserEditForm(request.POST, instance=user)
        password_form = AdminPasswordChangeForm(request.POST)
        
        if 'update_info' in request.POST and user_form.is_valid():
            user_form.save()
            
            messages.success(request, _('User information updated successfully!'))
            return redirect('user_management:user_detail', user_id=user.id)
            
        elif 'change_password' in request.POST and password_form.is_valid():
            user.password = make_password(password_form.cleaned_data['password1'])
            user.save()
            
            messages.success(request, _('Password changed successfully!'))
            return redirect('user_management:user_detail', user_id=user.id)
    else:
        user_form = AdminUserEditForm(instance=user)
        password_form = AdminPasswordChangeForm()
    
    return render(request, 'dashboard/user_management/user_edit.html', {
        'user_form': user_form,
        'password_form': password_form,
        'user_profile': user,
    })


@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    """
    Delete user
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        
        logger.info(f"User {username} deleted by {request.user.username}")
        messages.success(request, _('User deleted successfully!'))
        return redirect('user_management:user_list')
    
    return render(request, 'dashboard/user_management/user_confirm_delete.html', {
        'user_profile': user,
    })


@login_required
@user_passes_test(is_admin)
def assign_role(request, user_id):
    """
    Assign roles to user
    """
    user = get_object_or_404(User, id=user_id)
    
    # Get current user roles
    current_roles = Role.objects.filter(user_roles__user=user)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST)
        if form.is_valid():
            selected_roles = form.cleaned_data['roles']
            
            # Delete current roles
            UserRole.objects.filter(user=user).delete()
            
            # Add selected roles without assigned_at (it's auto-added by auto_now_add)
            for role in selected_roles:
                # UserRole.objects.create() will automatically set assigned_at with auto_now_add=True
                # Don't specify assigned_at explicitly
                UserRole.objects.create(
                    user=user,
                    role=role,
                    assigned_by=request.user
                )
            
            messages.success(request, _('User roles updated successfully!'))
            return redirect('user_management:user_detail', user_id=user.id)
    else:
        form = UserRoleForm(initial={'roles': current_roles})
    
    return render(request, 'dashboard/user_management/assign_role.html', {
        'form': form,
        'user_profile': user,
    })


# داله للتحقق إذا كان المستخدم يمكنه إدارة الأدوار
def can_manage_roles(user):
    """
    التحقق من صلاحيات إدارة الأدوار
    """
    if user.is_superuser:
        return True
    
    try:
        # عدم استخدام assigned_at هنا
        return user.user_roles.filter(role__name=Role.DEVELOPER).exists()
    except:
        return False


# إدارة الأدوار
@login_required
@user_passes_test(can_manage_roles)
def role_list(request):
    """
    Display list of roles
    """
    roles_list = Role.objects.annotate(
        user_count=Count('user_roles')
    ).order_by('name')
    
    # Pagination
    paginator = Paginator(roles_list, 20)  # 20 roles per page
    page = request.GET.get('page')
    roles = paginator.get_page(page)
    
    context = {
        'roles': roles
    }
    
    return render(request, 'dashboard/user_management/role_list.html', context)


@login_required
@user_passes_test(can_manage_roles)
def role_detail(request, role_id):
    """
    عرض تفاصيل الدور
    """
    role = get_object_or_404(Role, id=role_id)
    
    # تجنب استخدام حقل assigned_at نهائيًا
    # استخدام values() لتحديد الحقول المطلوبة فقط
    users_query = UserRole.objects.filter(role=role).select_related('user').only('user')
    
    # إنشاء قائمة جديدة تحتوي فقط على المستخدمين
    users = []
    for user_role in users_query:
        users.append({
            'user': user_role.user
        })
    
    context = {
        'role': role,
        'users': users,
    }
    
    return render(request, 'dashboard/user_management/role_detail.html', context)
