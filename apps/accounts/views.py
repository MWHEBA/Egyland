from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, AddressForm
from .models import Address


def register(request):
    """
    عرض تسجيل المستخدمين الجدد
    """
    if request.user.is_authenticated:
        return redirect('core:home')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('تم إنشاء حسابك بنجاح!'))
            return redirect('core:home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """
    عرض الملف الشخصي للمستخدم
    """
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()
    
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'addresses': addresses,
        'default_address': default_address,
    }
    
    return render(request, 'dashboard/user_profile.html', context)


@login_required
def edit_profile(request):
    """
    عرض تحديث الملف الشخصي
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('تم تحديث الملف الشخصي بنجاح!'))
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def address_list(request):
    """
    عرض قائمة العناوين
    """
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def add_address(request):
    """
    عرض إضافة عنوان جديد
    """
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, _('تم إضافة العنوان بنجاح!'))
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/address_form.html', {'form': form, 'title': _('إضافة عنوان جديد')})


@login_required
def edit_address(request, address_id):
    """
    عرض تحديث عنوان
    """
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث العنوان بنجاح!'))
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/address_form.html', {'form': form, 'title': _('تعديل العنوان')})


@login_required
def delete_address(request, address_id):
    """
    عرض حذف عنوان
    """
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, _('تم حذف العنوان بنجاح!'))
        return redirect('accounts:address_list')
    
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


@login_required
def set_default_address(request, address_id):
    """
    عرض تعيين العنوان الافتراضي
    """
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # إلغاء تحديد العناوين الافتراضية الأخرى
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # تعيين العنوان الحالي كافتراضي
    address.is_default = True
    address.save()
    
    messages.success(request, _('تم تعيين العنوان كافتراضي!'))
    return redirect('accounts:address_list')
