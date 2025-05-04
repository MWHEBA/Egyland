import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.db.models import Count, Q
from django.conf import settings
from pathlib import Path
from django import forms
from django.utils.text import slugify
from django.contrib.auth.models import User
from apps.products.models import (
    Product, PackagingType, ProductPackagingType,
    CountOption, SizeOption, Inquiry as ProductInquiry, ProductVariety, SeasonIcon,
    Seasonality, ProductRequest
)
from apps.products.forms import ProductForm
from .mixins import StaffRequiredMixin
from apps.inquiries.models import Inquiry as InquiriesInquiry, InquiryNote
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class DashboardHomeView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    """
    Dashboard home page showing key metrics and recent activities
    """
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        
        # Key metrics
        context['total_products'] = Product.objects.count()
        context['total_inquiries'] = InquiriesInquiry.objects.count()
        context['new_inquiries'] = InquiriesInquiry.objects.filter(status='new').count()
        context['in_progress_inquiries'] = InquiriesInquiry.objects.filter(status='in_progress').count()
        context['completed_inquiries'] = InquiriesInquiry.objects.filter(status='completed').count()
        
        # إحصائيات طلبات المنتجات (باستخدام الاستفسارات ذات النوع product_request)
        product_requests = InquiriesInquiry.objects.filter(type='product_request')
        context['total_product_requests'] = product_requests.count()
        context['new_product_requests'] = product_requests.filter(status='new').count()
        context['in_progress_product_requests'] = product_requests.filter(status='in_progress').count()
        context['completed_product_requests'] = product_requests.filter(status='completed').count()
        
        # Recent inquiries (أحدث الاستفسارات)
        context['recent_inquiries'] = InquiriesInquiry.objects.filter(type__in=['contact', 'product_inquiry']).order_by('-created_at')[:5]
        
        # Recent product requests (أحدث طلبات المنتجات)
        context['recent_product_requests'] = InquiriesInquiry.objects.filter(type='product_request').order_by('-created_at')[:5]
        
        # Product statistics
        context['product_types'] = Product.objects.values('product_type').annotate(count=Count('id'))
        context['featured_products'] = Product.objects.filter(is_featured=True).count()
        context['popular_products'] = Product.objects.filter(is_popular=True).count()
        context['special_products'] = Product.objects.filter(is_special=True).count()
        
        # إحصائيات متقدمة للمنتجات
        context['products_with_varieties'] = Product.objects.filter(has_varieties=True).count()
        context['total_varieties'] = ProductVariety.objects.count()
        
        # الإحصائيات حسب أنواع المنتجات 
        context['fresh_products'] = Product.objects.filter(product_type__in=['fresh', 'both']).count()
        context['iqf_products'] = Product.objects.filter(product_type__in=['iqf', 'both']).count()
        
        # آخر المنتجات المضافة أو المعدلة
        context['latest_updated_products'] = Product.objects.order_by('-updated_at')[:5]
        
        # ربط إحصائيات التغليف
        context['total_packaging_types'] = PackagingType.objects.count()
        context['product_packaging_count'] = ProductPackagingType.objects.count()
        
        # بيانات عدد المنتجات لكل فصل (بناءً على بيانات الموسمية)
        seasons_data = {
            'winter': Seasonality.objects.filter(Q(dec=True) | Q(jan=True) | Q(feb=True)).distinct().count(),
            'spring': Seasonality.objects.filter(Q(mar=True) | Q(apr=True) | Q(may=True)).distinct().count(),
            'summer': Seasonality.objects.filter(Q(jun=True) | Q(jul=True) | Q(aug=True)).distinct().count(),
            'autumn': Seasonality.objects.filter(Q(sep=True) | Q(oct=True) | Q(nov=True)).distinct().count(),
        }
        context['seasons_data'] = seasons_data
        
        # إحصائيات مقارنة الشهر الحالي
        current_month = timezone.now().month
        last_month = current_month - 1 if current_month > 1 else 12
        
        # استفسارات الشهر الحالي والشهر السابق
        current_month_inquiries = InquiriesInquiry.objects.filter(
            created_at__month=current_month, 
            created_at__year=timezone.now().year
        ).count()
        
        last_month_inquiries = InquiriesInquiry.objects.filter(
            created_at__month=last_month,
            created_at__year=timezone.now().year if last_month != 12 else timezone.now().year - 1
        ).count()
        
        context['current_month_inquiries'] = current_month_inquiries
        context['last_month_inquiries'] = last_month_inquiries
        context['inquiry_change_percent'] = self._calculate_percent_change(last_month_inquiries, current_month_inquiries)
        
        return context
    
    def _calculate_percent_change(self, old_value, new_value):
        """حساب نسبة التغيير بين قيمتين"""
        if old_value == 0:
            return 100 if new_value > 0 else 0
        
        change = ((new_value - old_value) / old_value) * 100
        return round(change, 1)

class ProductListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    List all products with filtering and sorting
    """
    model = Product
    template_name = 'dashboard/product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters from GET parameters
        product_type = self.request.GET.get('type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)
            
        featured = self.request.GET.get('featured')
        if featured:
            queryset = queryset.filter(is_featured=(featured == 'yes'))
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
            
        # Apply sorting
        sort = self.request.GET.get('sort', 'order')
        direction = self.request.GET.get('dir', 'asc')
        
        if sort in ['name', 'created_at', 'product_type', 'order']:
            if direction == 'desc':
                sort = f'-{sort}'
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by('order', 'name')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_types'] = dict(Product.objects.model._meta.get_field('product_type').choices)
        
        return context

class ProductCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Create a new product
    """
    model = Product
    template_name = 'dashboard/product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('dashboard:products')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def form_valid(self, form):
        # حفظ النموذج أولاً
        response = super().form_valid(form)
        
        # معالجة أيقونة الموسمية إذا تم تمريرها
        if 'season_icon' in self.request.FILES:
            from apps.products.models import Seasonality
            season_icon = self.request.FILES['season_icon']
            # إنشاء أو تحديث الموسمية للمنتج
            seasonality, created = Seasonality.objects.get_or_create(
                product=form.instance,
                variety=None,
                type='fresh',  # افتراضي
                defaults={'season_icon': season_icon}
            )
            if not created:
                seasonality.season_icon = season_icon
                seasonality.save()
        
        messages.success(self.request, f"Product '{form.instance.name}' created successfully.")
        return response

class ProductUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Update an existing product
    """
    model = Product
    template_name = 'dashboard/product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('dashboard:products')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get selected season icon if available
        product = self.object
        if hasattr(product, 'seasonality') and product.seasonality.exists():
            main_seasonality = product.seasonality.first()
            if main_seasonality and main_seasonality.season_icon:
                context['selected_season_icon'] = main_seasonality
        
        return context
    
    def form_valid(self, form):
        # حفظ النموذج أولاً
        response = super().form_valid(form)
        
        # معالجة أيقونة الموسمية إذا تم تمريرها
        if 'season_icon' in self.request.FILES:
            from apps.products.models import Seasonality
            season_icon = self.request.FILES['season_icon']
            # إنشاء أو تحديث الموسمية للمنتج
            seasonality, created = Seasonality.objects.get_or_create(
                product=form.instance,
                variety=None,
                type='fresh',  # افتراضي
                defaults={'season_icon': season_icon}
            )
            if not created:
                seasonality.season_icon = season_icon
                seasonality.save()
        
        messages.success(self.request, f"Product '{form.instance.name}' updated successfully.")
        return response

class ProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Delete a product
    """
    model = Product
    template_name = 'dashboard/product_confirm_delete.html'
    success_url = reverse_lazy('dashboard:products')
    
    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        messages.success(request, f"Product '{product.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

class InquiryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    List all inquiries with filtering and sorting
    """
    model = InquiriesInquiry
    template_name = 'dashboard/inquiries/list.html'
    context_object_name = 'inquiries'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters from GET parameters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        inquiry_type = self.request.GET.get('type')
        if inquiry_type:
            queryset = queryset.filter(type=inquiry_type)
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(email__icontains=search) |
                Q(company__icontains=search) |
                Q(message__icontains=search)
            )
            
        # Apply sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['status_choices'] = dict(InquiriesInquiry.INQUIRY_STATUS_CHOICES)
        context['type_choices'] = dict(InquiriesInquiry.INQUIRY_TYPE_CHOICES)
        
        # Preserve GET parameters for pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        
        return context

class InquiryDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """
    View inquiry details
    """
    model = InquiriesInquiry
    template_name = 'dashboard/inquiries/detail.html'
    context_object_name = 'inquiry'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = dict(InquiriesInquiry.INQUIRY_STATUS_CHOICES)
        # إضافة ملاحظات الاستفسار إلى السياق
        context['notes'] = self.object.notes.all().select_related('created_by')
        return context

@login_required
@csrf_exempt
def update_inquiry_status(request, pk):
    """
    Update inquiry status via AJAX
    """
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            is_responded = data.get('is_responded', None)
            admin_notes = data.get('admin_notes', None)
            
            inquiry = get_object_or_404(InquiriesInquiry, pk=pk)
            
            if new_status:
                inquiry.status = new_status
                
            if is_responded is not None:
                inquiry.is_responded = is_responded
                
            if admin_notes is not None:
                inquiry.admin_notes = admin_notes
                
            inquiry.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Inquiry updated successfully',
                'inquiry_status': inquiry.get_status_display(),
                'is_responded': inquiry.is_responded
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def add_inquiry_note(request, pk):
    """
    Add a note to an inquiry via AJAX
    """
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')
            
            if not content or not content.strip():
                return JsonResponse({'status': 'error', 'message': 'Note content is required'}, status=400)
                
            inquiry = get_object_or_404(InquiriesInquiry, pk=pk)
            
            # إنشاء ملاحظة جديدة باستخدام نموذج InquiryNote
            note = InquiryNote.objects.create(
                inquiry=inquiry,
                content=content,
                created_by=request.user
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Note added successfully',
                'username': request.user.get_full_name() or request.user.username,
                'content': content,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

class UserProfileView(LoginRequiredMixin, UpdateView):
    """
    Allow users to update their profile information
    """
    model = User
    template_name = 'dashboard/user_profile.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('dashboard:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # معالجة صورة البروفايل إذا تم رفعها
        if 'avatar' in self.request.FILES:
            user_profile = self.request.user.profile
            user_profile.profile_picture = self.request.FILES['avatar']
            user_profile.save()
            
        messages.success(self.request, "Profile updated successfully.")
        return response

@login_required
def password_change_success(request):
    """
    عرض رسالة تأكيد تغيير كلمة المرور بنجاح
    """
    messages.success(request, "Password changed successfully!")
    return redirect('dashboard:profile')

# Product Varieties Views
class VarietyListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    List all product varieties
    """
    model = ProductVariety
    template_name = 'dashboard/product/variety_list.html'
    context_object_name = 'varieties'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters and search
        product_id = self.request.GET.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(product__name__icontains=search)
            )
        
        return queryset.select_related('product')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(has_varieties=True)
        
        # Preserve GET parameters for pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        
        return context

class VarietyCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Create a new product variety
    """
    model = ProductVariety
    template_name = 'dashboard/product/variety_form.html'
    fields = ['product', 'name', 'image']
    success_url = reverse_lazy('dashboard:varieties')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only show products that have 'has_varieties' set to True
        form.fields['product'].queryset = Product.objects.filter(has_varieties=True)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Variety '{form.instance.name}' created successfully.")
        return super().form_valid(form)

class VarietyUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Update an existing product variety
    """
    model = ProductVariety
    template_name = 'dashboard/product/variety_form.html'
    fields = ['product', 'name', 'image']
    success_url = reverse_lazy('dashboard:varieties')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only show products that have 'has_varieties' set to True
        form.fields['product'].queryset = Product.objects.filter(has_varieties=True)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Variety '{form.instance.name}' updated successfully.")
        return super().form_valid(form)

class VarietyDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Delete a product variety
    """
    model = ProductVariety
    template_name = 'dashboard/product/variety_confirm_delete.html'
    success_url = reverse_lazy('dashboard:varieties')
    
    def delete(self, request, *args, **kwargs):
        variety = self.get_object()
        messages.success(request, f"Variety '{variety.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

# Seasonality Views
class SeasonalityListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    List all product seasonality entries
    """
    model = Seasonality
    template_name = 'dashboard/product/seasonality_list.html'
    context_object_name = 'seasonality_entries'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        product_id = self.request.GET.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id, variety__isnull=True)
        
        variety_id = self.request.GET.get('variety')
        if variety_id:
            queryset = queryset.filter(variety_id=variety_id)
        
        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        return queryset.select_related('product', 'variety')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Data for filters and modals
        context['products'] = Product.objects.all()
        context['varieties'] = ProductVariety.objects.select_related('product')
        context['type_choices'] = dict(Product.objects.model._meta.get_field('product_type').choices[:2])
        
        # Group entries by product/variety for better display
        entries_by_product = {}
        for entry in self.object_list:
            if entry.product:
                key = f"product_{entry.product.id}_{entry.type}"
                if key not in entries_by_product:
                    entries_by_product[key] = {
                        'name': f"{entry.product.name} ({entry.get_type_display()})",
                        'type': 'product',
                        'id': entry.product.id,
                        'product_type': entry.type,
                        'entry': entry,
                    }
            elif entry.variety:
                key = f"variety_{entry.variety.id}_{entry.type}"
                if key not in entries_by_product:
                    entries_by_product[key] = {
                        'name': f"{entry.variety.product.name} - {entry.variety.name} ({entry.get_type_display()})",
                        'type': 'variety',
                        'id': entry.variety.id,
                        'product_type': entry.type,
                        'entry': entry,
                    }
        
        context['entries_by_product'] = entries_by_product
        
        # Preserve GET parameters for pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        
        return context

class SeasonalityCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Create a new seasonality entry
    """
    model = Seasonality
    template_name = 'dashboard/product/seasonality_form.html'
    fields = [
        'product', 'variety', 'type', 'season_icon',
        'jan', 'feb', 'mar', 'apr', 'may', 'jun',
        'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
    ]
    success_url = reverse_lazy('dashboard:seasonality')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Configure form for better UX
        form.fields['product'].required = False
        form.fields['variety'].required = False
        return form
    
    def form_valid(self, form):
        # Validate that either product or variety is specified
        if not form.cleaned_data.get('product') and not form.cleaned_data.get('variety'):
            form.add_error(None, "Either product or variety must be specified.")
            return self.form_invalid(form)
        
        # Set proper success message
        if form.instance.product:
            messages.success(self.request, f"Seasonality for '{form.instance.product.name}' created successfully.")
        else:
            messages.success(self.request, f"Seasonality for '{form.instance.variety.name}' created successfully.")
        
        response = super().form_valid(form)
        
        # Handle AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import HttpResponse
            return HttpResponse()
            
        return response
        
    def form_invalid(self, form):
        # Handle AJAX requests for form errors
        response = super().form_invalid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return response
        return response

class SeasonalityUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Update an existing seasonality entry
    """
    model = Seasonality
    template_name = 'dashboard/product/seasonality_form.html'
    fields = [
        'product', 'variety', 'type', 'season_icon',
        'jan', 'feb', 'mar', 'apr', 'may', 'jun',
        'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
    ]
    success_url = reverse_lazy('dashboard:seasonality')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Configure form for better UX
        form.fields['product'].required = False
        form.fields['variety'].required = False
        
        # طباعة بيانات تشخيصية لتتبع المشكلة
        obj = self.get_object()
        print(f"Current object: Product ID={obj.product.pk if obj.product else None}, Variety ID={obj.variety.pk if obj.variety else None}, Type={obj.type}")
        
        # تحديد القيم الأولية بشكل صريح
        if not form.initial:
            form.initial = {
                'product': obj.product.pk if obj.product else None,
                'variety': obj.variety.pk if obj.variety else None,
                'type': obj.type,
                'season_icon': obj.season_icon,
                'jan': obj.jan,
                'feb': obj.feb,
                'mar': obj.mar,
                'apr': obj.apr,
                'may': obj.may,
                'jun': obj.jun,
                'jul': obj.jul,
                'aug': obj.aug,
                'sep': obj.sep,
                'oct': obj.oct,
                'nov': obj.nov,
                'dec': obj.dec,
            }
        print(f"Form initial data: {form.initial}")
        print(f"Form fields: {[f for f in form.fields]}")
                
        return form
    
    def form_valid(self, form):
        # Validate that either product or variety is specified
        if not form.cleaned_data.get('product') and not form.cleaned_data.get('variety'):
            form.add_error(None, "Either product or variety must be specified.")
            return self.form_invalid(form)
        
        # Set proper success message
        if form.instance.product:
            messages.success(self.request, f"Seasonality for '{form.instance.product.name}' updated successfully.")
        elif form.instance.variety:
            messages.success(self.request, f"Seasonality for '{form.instance.variety.name}' updated successfully.")
        else:
            messages.success(self.request, "Seasonality updated successfully.")
        
        response = super().form_valid(form)
        
        # Handle AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import HttpResponse
            return HttpResponse()
            
        return response
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Return JSON data if requested
        if request.GET.get('format') == 'json':
            from django.http import JsonResponse
            
            data = {
                'id': self.object.id,
                'product_id': self.object.product_id if self.object.product else None,
                'variety_id': self.object.variety_id if self.object.variety else None,
                'type': self.object.type,
                'jan': self.object.jan,
                'feb': self.object.feb,
                'mar': self.object.mar,
                'apr': self.object.apr,
                'may': self.object.may,
                'jun': self.object.jun, 
                'jul': self.object.jul,
                'aug': self.object.aug,
                'sep': self.object.sep,
                'oct': self.object.oct,
                'nov': self.object.nov,
                'dec': self.object.dec,
            }
            
            return JsonResponse(data)
        
        return super().get(request, *args, **kwargs)

class SeasonalityDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Delete a seasonality entry
    """
    model = Seasonality
    template_name = 'dashboard/product/seasonality_confirm_delete.html'
    success_url = reverse_lazy('dashboard:seasonality')
    
    def delete(self, request, *args, **kwargs):
        seasonality = self.get_object()
        
        if seasonality.product:
            messages.success(request, f"Seasonality for '{seasonality.product.name}' deleted successfully.")
        elif seasonality.variety:
            messages.success(request, f"Seasonality for '{seasonality.variety.name}' deleted successfully.")
        else:
            messages.success(request, "Seasonality deleted successfully.")
        
        response = super().delete(request, *args, **kwargs)
        
        # Handle AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import HttpResponse
            return HttpResponse()
            
        return response

# Size Views
class SizeListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    List all size options
    """
    model = SizeOption
    template_name = 'dashboard/product/size_list.html'
    context_object_name = 'sizes'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(value__icontains=search)
        
        # الحصول على القيم كقائمة للترتيب الرقمي المخصص
        size_list = list(queryset)
        
        # محاولة الترتيب بناءً على قيم رقمية أولاً، ثم أبجديًا إذا لم تكن القيم رقمية
        def size_sorting_key(size):
            # محاولة تحويل القيمة إلى رقم للترتيب
            try:
                # إزالة أي وحدات قياس (مثل: cm, mm) للتركيز على الرقم فقط
                value = size.value.split()[0]  # الحصول على الجزء الأول قبل المسافة
                # تنظيف القيمة من الأحرف غير الرقمية
                numeric_part = ''.join(c for c in value if c.isdigit() or c == '.')
                if numeric_part:
                    return float(numeric_part)  # محاولة تحويل إلى رقم
            except (ValueError, IndexError):
                pass
            
            # إذا فشل التحويل إلى رقم، استخدم القيمة كما هي للترتيب الأبجدي
            return size.value
        
        # فرز القائمة بناءً على المفتاح المخصص
        size_list.sort(key=size_sorting_key)
        
        return size_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Size options count
        context['size_options_count'] = SizeOption.objects.count()
        
        # Preserve GET parameters for pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        
        return context

class SizeCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Create a new size option
    """
    model = SizeOption
    template_name = 'dashboard/product/size_form.html'
    fields = ['value']
    success_url = reverse_lazy('dashboard:sizes')
    
    def form_valid(self, form):
        """Process a valid form."""
        response = super().form_valid(form)

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # إذا تم الطلب عبر AJAX، أرجع استجابة JSON مع البيانات اللازمة
            data = {
                'success': True,
                'message': 'Size option created successfully!',
                'id': form.instance.id,
                'value': form.instance.value,
            }
            return JsonResponse(data)
        
        # إذا لم يكن AJAX، استمر بطريقة العرض العادية
        messages.success(self.request, 'Size option created successfully!')
        return response
        
    def form_invalid(self, form):
        """Process an invalid form."""
        # إذا كان الطلب AJAX، أرجع استجابة JSON تحتوي على الأخطاء
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                # استخراج أول خطأ لكل حقل
                errors[field] = str(error_list[0])
            
            # تجميع الأخطاء في رسالة واحدة للعرض
            error_message = "فشل إنشاء خيار الحجم. "
            if "__all__" in errors:
                error_message += errors["__all__"]
            elif "value" in errors:
                error_message += errors["value"]
            else:
                error_message += "يرجى التحقق من البيانات المدخلة."
                
            return JsonResponse({
                'success': False,
                'message': error_message,
                'errors': errors
            }, status=400)
            
        # في حالة الطلب العادي، استخدم السلوك الافتراضي
        return super().form_invalid(form)

class SizeUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Update an existing size option
    """
    model = SizeOption
    template_name = 'dashboard/product/size_form.html'
    fields = ['value']
    success_url = reverse_lazy('dashboard:sizes')
    
    def form_valid(self, form):
        messages.success(self.request, f"Size option '{form.instance.value}' updated successfully.")
        
        # إذا كان الطلب AJAX، نرجع استجابة مختلفة
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
            
        return super().form_valid(form)
        
    def form_invalid(self, form):
        # إذا كان الطلب AJAX، نرجع الفورم مع الأخطاء
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.render_to_response(self.get_context_data(form=form))
            
        return super().form_invalid(form)
        
    def get(self, request, *args, **kwargs):
        # إذا كان الطلب AJAX، نرجع بيانات العنصر كـ JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            return JsonResponse({
                'id': self.object.id,
                'value': self.object.value
            })
        # إعادة توجيه لصفحة القائمة لطلبات GET العادية
        return HttpResponseRedirect(reverse_lazy('dashboard:sizes'))
    
    def post(self, request, *args, **kwargs):
        # إذا كان الطلب AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            form = self.get_form()
            if form.is_valid():
                self.object = form.save()
                return JsonResponse({
                    'success': True,
                    'id': self.object.id,
                    'value': self.object.value
                })
            else:
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list[0]
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
        # الطلب العادي (غير AJAX)
        return super().post(request, *args, **kwargs)

class SizeDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Delete a size option
    """
    model = SizeOption
    template_name = 'dashboard/product/size_confirm_delete.html'
    success_url = reverse_lazy('dashboard:sizes')
    
    def delete(self, request, *args, **kwargs):
        size = self.get_object()
        messages.success(request, f"Size option '{size.value}' deleted successfully.")
        
        # إذا كان الطلب AJAX، نرجع استجابة مختلفة
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            size.delete()
            return JsonResponse({'success': True})
            
        return super().delete(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # إعادة توجيه لصفحة القائمة بدلاً من عرض صفحة تأكيد الحذف
        return HttpResponseRedirect(reverse_lazy('dashboard:sizes'))
        
    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

# Packaging Type Views
class PackagingTypeListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    Display list of packaging types
    """
    model = PackagingType
    template_name = 'dashboard/product/packaging_type_list.html'
    context_object_name = 'packaging_types'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by("-created_at")
        
        # Apply search filter
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(key_word__icontains=search_query)
            )
            
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_packaging_types"] = self.get_queryset().count()
        
        # Add search parameter to pagination links
        if "search" in self.request.GET:
            context["search"] = self.request.GET.get("search", "")
            
        # Add form for modal
        context["form"] = PackagingTypeForm()
            
        return context

class PackagingTypeCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Add a new packaging type
    """
    model = PackagingType
    template_name = 'dashboard/product/packaging_type_form.html'
    fields = ['name', 'description', 'image', 'key_word', 'is_fresh', 'is_iqf']
    success_url = reverse_lazy('dashboard:packaging_types')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Set default values for optional fields to False
        form.fields['is_fresh'].initial = False
        form.fields['is_iqf'].initial = False
        
        # تقليل ارتفاع حقل الوصف
        form.fields['description'].widget.attrs.update({
            'rows': 2,
            'style': 'height: 5rem;'
        })
        
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Packaging type '{form.instance.name}' created successfully.")
        return super().form_valid(form)

class PackagingTypeUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Update an existing packaging type
    """
    model = PackagingType
    template_name = 'dashboard/product/packaging_type_form.html'
    fields = ['name', 'description', 'image', 'key_word', 'is_fresh', 'is_iqf']
    success_url = reverse_lazy('dashboard:packaging_types')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # تقليل ارتفاع حقل الوصف
        form.fields['description'].widget.attrs.update({
            'rows': 2,
            'style': 'height: 2.5rem;'
        })
        
        # طباعة بيانات تشخيصية لتتبع المشكلة
        obj = self.get_object()
        print(f"Current object: Product ID={obj.product.pk}, Variety ID={obj.variety.pk}, Type={obj.type}")
        
        # تحديد القيم الأولية بشكل صريح
        if not form.initial:
            form.initial = {
                'product': obj.product.pk,
                'variety': obj.variety.pk,
                'type': obj.type,
                'season_icon': obj.season_icon,
                'jan': obj.jan,
                'feb': obj.feb,
                'mar': obj.mar,
                'apr': obj.apr,
                'may': obj.may,
                'jun': obj.jun,
                'jul': obj.jul,
                'aug': obj.aug,
                'sep': obj.sep,
                'oct': obj.oct,
                'nov': obj.nov,
                'dec': obj.dec,
            }
        print(f"Form initial data: {form.initial}")
        
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f"Packaging type '{form.instance.name}' updated successfully.")
        return super().form_valid(form)

class PackagingTypeDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Delete a packaging type
    """
    model = PackagingType
    template_name = 'dashboard/product/packaging_type_confirm_delete.html'
    success_url = reverse_lazy('dashboard:packaging_types')
    
    def delete(self, request, *args, **kwargs):
        packaging_type = self.get_object()
        messages.success(request, f"Packaging type '{packaging_type.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)
        
# أجاكس Modal Views لأنواع التغليف
class PackagingTypeForm(forms.ModelForm):
    """
    نموذج نوع التغليف للمودال
    """
    class Meta:
        model = PackagingType
        fields = ['name', 'description', 'image', 'key_word', 'is_fresh', 'is_iqf']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'style': 'height: 5rem;'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        is_fresh = cleaned_data.get('is_fresh')
        key_word = cleaned_data.get('key_word')
        
        # إذا تم اختيار Fresh Products ولم يتم تقديم key_word
        if is_fresh and not key_word:
            self.add_error('key_word', 'This field is required when Fresh Products is selected')
        
        return cleaned_data

@login_required
def packaging_type_create_modal(request):
    """
    إضافة نوع تغليف جديد عبر مودال
    """
    # التحقق من أن المستخدم staff
    if not request.user.is_staff:
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        # عمل نسخة معدلة من POST
        post_data = request.POST.copy()
        
        # تحديد ما إذا كان حقل key_word إجباري أم لا
        is_key_word_required = post_data.get('is_key_word_required') == 'true'
        is_fresh_selected = post_data.get('is_fresh') == 'on'
        
        # إذا تم إلغاء اختيار Fresh Products أو تم تعيين key_word غير إجباري
        if not is_fresh_selected or not is_key_word_required:
            # تعيين حقل key_word كفارغ إذا لم يكن مدخلاً
            if not post_data.get('key_word'):
                post_data['key_word'] = ''
        
        form = PackagingTypeForm(post_data, request.FILES)
        
        # إذا كان Fresh Products غير مختار، إلغاء التحقق من إجبارية key_word
        if not is_fresh_selected or not is_key_word_required:
            form.fields['key_word'].required = False
        
        if form.is_valid():
            packaging_type = form.save()
            messages.success(request, f"Packaging type '{packaging_type.name}' created successfully.")
            return redirect('dashboard:packaging_types')
        else:
            # إذا كان الطلب AJAX، نرجع ملف فورم HTML
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'dashboard/product/packaging_type_modal_form.html', {'form': form})
            return render(request, 'dashboard/product/packaging_type_modal_form.html', {'form': form})
    else:
        form = PackagingTypeForm()
    
    return render(request, 'dashboard/product/packaging_type_modal_form.html', {'form': form})

@login_required
def packaging_type_update_modal(request, pk):
    """
    تعديل نوع تغليف عبر مودال
    """
    # التحقق من أن المستخدم staff
    if not request.user.is_staff:
        return redirect('dashboard:home')
        
    packaging_type = get_object_or_404(PackagingType, pk=pk)
    
    if request.method == 'POST':
        # عمل نسخة معدلة من POST
        post_data = request.POST.copy()
        
        # تحديد ما إذا كان حقل key_word إجباري أم لا
        is_key_word_required = post_data.get('is_key_word_required') == 'true'
        is_fresh_selected = post_data.get('is_fresh') == 'on'
        
        # إذا تم إلغاء اختيار Fresh Products أو تم تعيين key_word غير إجباري
        if not is_fresh_selected or not is_key_word_required:
            # تعيين حقل key_word كفارغ إذا لم يكن مدخلاً
            if not post_data.get('key_word'):
                post_data['key_word'] = ''
                
        form = PackagingTypeForm(post_data, request.FILES, instance=packaging_type)
        
        # إذا كان Fresh Products غير مختار، إلغاء التحقق من إجبارية key_word
        if not is_fresh_selected or not is_key_word_required:
            form.fields['key_word'].required = False
            
        if form.is_valid():
            form.save()
            messages.success(request, f"Packaging type '{packaging_type.name}' updated successfully.")
            return redirect('dashboard:packaging_types')
        else:
            # عرض الفورم مع الأخطاء
            return render(request, 'dashboard/product/packaging_type_modal_form.html', {
                'form': form, 
                'object': packaging_type
            })
    else:
        form = PackagingTypeForm(instance=packaging_type)
    
    # عرض فورم التعديل
    return render(request, 'dashboard/product/packaging_type_modal_form.html', {
        'form': form, 
        'object': packaging_type
    })

@login_required
def packaging_type_delete_modal(request, pk):
    """
    حذف نوع تغليف عبر مودال
    """
    # التحقق من أن المستخدم staff
    if not request.user.is_staff:
        return redirect('dashboard:home')
        
    packaging_type = get_object_or_404(PackagingType, pk=pk)
    product_count = ProductPackagingType.objects.filter(packaging_type=packaging_type).count()
    
    if request.method == 'POST':
        packaging_type.delete()
        messages.success(request, f"Packaging type '{packaging_type.name}' deleted successfully.")
        return redirect('dashboard:packaging_types')
    
    context = {
        'object': packaging_type,
        'has_products': product_count > 0,
        'product_count': product_count,
    }
    
    return render(request, 'dashboard/product/packaging_type_modal_delete.html', context)

class ProductPackagingTypeListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    Display list of product packaging type relationships
    """
    model = ProductPackagingType
    template_name = 'dashboard/product/product_packaging_type_list.html'
    context_object_name = 'product_packaging_types'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters from GET parameters
        product_id = self.request.GET.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
            
        type_id = self.request.GET.get('packaging_type')
        if type_id:
            queryset = queryset.filter(packaging_type_id=type_id)
            
        product_type = self.request.GET.get('product_type')
        if product_type:
            queryset = queryset.filter(type=product_type)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_products'] = Product.objects.all()
        context['all_packaging_types'] = PackagingType.objects.all()
        context['product_types'] = dict(ProductPackagingType.objects.model._meta.get_field('type').choices)
        
        # Preserve GET parameters for pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        
        return context

class ProductPackagingTypeCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Add a new product packaging type relationship
    """
    model = ProductPackagingType
    template_name = 'dashboard/product/product_packaging_type_form.html'
    fields = [
        'product', 'packaging_type', 'type', 'pallets_per_container',
        'items_per_pallet', 'show_fresh_label'
    ]
    success_url = reverse_lazy('dashboard:product_packaging_types')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['product'].queryset = Product.objects.all().order_by('name')
        form.fields['packaging_type'].queryset = PackagingType.objects.all().order_by('name')
        for field_name, field in form.fields.items():
            if field_name in ['product', 'packaging_type', 'type']:
                field.required = True
        return form
    
    def post(self, request, *args, **kwargs):
        """
        Custom post handling to ensure data is saved correctly
        """
        self.object = None
        
        print(f"POST data: {request.POST}")
        
        # Ensure required data is present
        product_id = request.POST.get('product')
        packaging_type_id = request.POST.get('packaging_type')
        type_val = request.POST.get('type', 'fresh')
        
        # If essential data is missing, return to form with error message
        if not product_id or not packaging_type_id:
            form = self.get_form()
            if not product_id:
                form.add_error('product', 'Product selection is required')
            if not packaging_type_id:
                form.add_error('packaging_type', 'Packaging type selection is required')
            return self.form_invalid(form)
        
        try:
            # Get objects from database
            product = Product.objects.get(id=product_id)
            packaging_type = PackagingType.objects.get(id=packaging_type_id)
            
            # Check if relationship already exists
            existing = ProductPackagingType.objects.filter(
                product=product,
                packaging_type=packaging_type,
                type=type_val
            )
            
            if existing.exists():
                form = self.get_form()
                form.add_error(None, 'A record for this product with the same packaging type and product type already exists')
                return self.form_invalid(form)
                
            # Create new instance and populate data
            instance = ProductPackagingType(
                product=product,
                packaging_type=packaging_type,
                type=type_val
            )
            
            # معالجة القيم الرقمية مع التحقق من صحتها
            try:
                pallets_per_container = request.POST.get('pallets_per_container', '0')
                instance.pallets_per_container = int(pallets_per_container) if pallets_per_container.strip() else 0
            except (ValueError, TypeError):
                instance.pallets_per_container = 0
                
            try:
                items_per_pallet = request.POST.get('items_per_pallet', '0')
                instance.items_per_pallet = int(items_per_pallet) if items_per_pallet.strip() else 0
            except (ValueError, TypeError):
                instance.items_per_pallet = 0
                
            # تعيين قيم افتراضية لحقول الوزن
            instance.net_weight = 1
            instance.weight_unit = 'kg'
            
            # معالجة حقل boolean
            instance.show_fresh_label = 'show_fresh_label' in request.POST
            
            # Save the instance
            instance.save()
            
            messages.success(self.request, f"Packaging type '{instance.packaging_type.name}' added to product '{instance.product.name}' successfully.")
            return redirect(self.success_url)
            
        except Product.DoesNotExist:
            form = self.get_form()
            form.add_error('product', 'Selected product does not exist')
            return self.form_invalid(form)
        except PackagingType.DoesNotExist:
            form = self.get_form()
            form.add_error('packaging_type', 'Selected packaging type does not exist')
            return self.form_invalid(form)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            form = self.get_form()
            form.add_error(None, f'An error occurred while saving: {str(e)}')
            return self.form_invalid(form)
            
    def form_invalid(self, form):
        print(f"Form errors: {form.errors}")
        return super().form_invalid(form)

class ProductPackagingTypeUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Update an existing product packaging type relationship
    """
    model = ProductPackagingType
    template_name = 'dashboard/product/product_packaging_type_form.html'
    fields = [
        'product', 'packaging_type', 'type', 'pallets_per_container',
        'items_per_pallet', 'show_fresh_label'
    ]
    success_url = reverse_lazy('dashboard:product_packaging_types')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['product'].queryset = Product.objects.all().order_by('name')
        form.fields['packaging_type'].queryset = PackagingType.objects.all().order_by('name')
        for field_name, field in form.fields.items():
            if field_name in ['product', 'packaging_type', 'type']:
                field.required = True
                
        # طباعة بيانات تشخيصية لتتبع المشكلة
        obj = self.get_object()
        print(f"Current object: Product ID={obj.product.pk}, Packaging Type ID={obj.packaging_type.pk}, Type={obj.type}")
        
        # تحديد القيم الأولية بشكل صريح
        if not form.initial:
            form.initial = {
                'product': obj.product.pk,
                'packaging_type': obj.packaging_type.pk,
                'type': obj.type,
                'pallets_per_container': obj.pallets_per_container,
                'items_per_pallet': obj.items_per_pallet,
                'show_fresh_label': obj.show_fresh_label
            }
        print(f"Form initial data: {form.initial}")
        
        return form
    
    def post(self, request, *args, **kwargs):
        """
        Custom post handling to ensure data is updated correctly
        """
        self.object = self.get_object()
        
        print(f"UPDATE POST data: {request.POST}")
        print(f"Current object before update: Product ID={self.object.product.pk}, Packaging Type ID={self.object.packaging_type.pk}, Type={self.object.type}")
        
        # Ensure required data is present
        product_id = request.POST.get('product')
        packaging_type_id = request.POST.get('packaging_type')
        type_val = request.POST.get('type', 'fresh')
        
        print(f"Submitted values: product_id={product_id}, packaging_type_id={packaging_type_id}, type={type_val}")
        
        # If essential data is missing, return to form with error message
        if not product_id or not packaging_type_id:
            form = self.get_form()
            if not product_id:
                form.add_error('product', 'Product selection is required')
            if not packaging_type_id:
                form.add_error('packaging_type', 'Packaging type selection is required')
            return self.form_invalid(form)
        
        try:
            # Get objects from database
            product = Product.objects.get(id=product_id)
            packaging_type = PackagingType.objects.get(id=packaging_type_id)
            
            print(f"Retrieved objects: Product={product.name} (ID={product.pk}), Packaging Type={packaging_type.name} (ID={packaging_type.pk})")
            
            # Check if relationship already exists for the same data except the current instance
            existing = ProductPackagingType.objects.filter(
                product=product,
                packaging_type=packaging_type,
                type=type_val
            ).exclude(pk=self.object.pk)
            
            if existing.exists():
                form = self.get_form()
                form.add_error(None, 'A record for this product with the same packaging type and product type already exists')
                return self.form_invalid(form)
                
            # Update the current instance
            self.object.product = product
            self.object.packaging_type = packaging_type
            self.object.type = type_val
            
            # معالجة القيم الرقمية مع التحقق من صحتها
            try:
                pallets_per_container = request.POST.get('pallets_per_container', '0')
                self.object.pallets_per_container = int(pallets_per_container) if pallets_per_container.strip() else 0
            except (ValueError, TypeError):
                self.object.pallets_per_container = 0
                
            try:
                items_per_pallet = request.POST.get('items_per_pallet', '0')
                self.object.items_per_pallet = int(items_per_pallet) if items_per_pallet.strip() else 0
            except (ValueError, TypeError):
                self.object.items_per_pallet = 0
            
            # Handle boolean field
            self.object.show_fresh_label = 'show_fresh_label' in request.POST
            
            # Save the changes
            self.object.save()
            
            messages.success(self.request, f"Packaging type '{self.object.packaging_type.name}' updated for product '{self.object.product.name}' successfully.")
            return redirect(self.success_url)
            
        except Product.DoesNotExist:
            form = self.get_form()
            form.add_error('product', 'Selected product does not exist')
            return self.form_invalid(form)
        except PackagingType.DoesNotExist:
            form = self.get_form()
            form.add_error('packaging_type', 'Selected packaging type does not exist')
            return self.form_invalid(form)
        except Exception as e:
            print(f"Unexpected error occurred during update: {str(e)}")
            form = self.get_form()
            form.add_error(None, f'An error occurred during update: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print(f"Update form errors: {form.errors}")
        return super().form_invalid(form)

class ProductPackagingTypeDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Delete a product packaging type relationship
    """
    model = ProductPackagingType
    template_name = 'dashboard/product/product_packaging_type_confirm_delete.html'
    success_url = reverse_lazy('dashboard:product_packaging_types')
    
    def delete(self, request, *args, **kwargs):
        product_packaging_type = self.get_object()
        messages.success(request, f"Product packaging type for '{product_packaging_type.product.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

# Season Icon Views
class SeasonIconListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    List all season icons
    """
    model = SeasonIcon
    template_name = 'dashboard/product/season_icon_list.html'
    context_object_name = 'season_icons'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('display_order', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Preserve GET parameters for pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        
        return context

class SeasonIconCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Create a new season icon
    """
    model = SeasonIcon
    template_name = 'dashboard/product/season_icon_form.html'
    fields = ['name', 'description', 'icon', 'color_code', 'display_order']
    success_url = reverse_lazy('dashboard:season_icons')
    
    def form_valid(self, form):
        messages.success(self.request, f"Season icon '{form.instance.name}' created successfully.")
        return super().form_valid(form)

class SeasonIconUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Update an existing season icon
    """
    model = SeasonIcon
    template_name = 'dashboard/product/season_icon_form.html'
    fields = ['name', 'description', 'icon', 'color_code', 'display_order']
    success_url = reverse_lazy('dashboard:season_icons')
    
    def form_valid(self, form):
        messages.success(self.request, f"Season icon '{form.instance.name}' updated successfully.")
        return super().form_valid(form)

class SeasonIconDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Delete a season icon
    """
    model = SeasonIcon
    template_name = 'dashboard/product/season_icon_confirm_delete.html'
    success_url = reverse_lazy('dashboard:season_icons')
    
    def delete(self, request, *args, **kwargs):
        season_icon = self.get_object()
        messages.success(request, f"Season icon '{season_icon.name}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

# Product Request Views
class ProductRequestListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    List all product requests
    """
    model = ProductRequest
    template_name = 'dashboard/product_request_list.html'
    context_object_name = 'requests'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Apply search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(company__icontains=search) |
                Q(email__icontains=search) |
                Q(product_name__icontains=search) |
                Q(product_description__icontains=search)
            )
            
        # Apply sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['status_choices'] = dict(ProductRequest.REQUEST_STATUS_CHOICES)
        
        # Preserve GET parameters for pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        
        return context

class ProductRequestDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """
    View product request details
    """
    model = ProductRequest
    template_name = 'dashboard/product_request_detail.html'
    context_object_name = 'request'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = dict(ProductRequest.REQUEST_STATUS_CHOICES)
        return context

@login_required
@csrf_exempt
def update_product_request_status(request, pk):
    """
    Update product request status via AJAX
    """
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            admin_notes = data.get('admin_notes', '')
            
            product_request = get_object_or_404(ProductRequest, pk=pk)
            
            # Update the status
            product_request.status = new_status
            
            # Update admin notes if provided
            if admin_notes:
                product_request.admin_notes = admin_notes
                
            product_request.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Status updated to {product_request.get_status_display()}'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def variety_detail_api(request, pk):
    """
    API endpoint to get variety details for modal editing
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        variety = get_object_or_404(ProductVariety, pk=pk)
        data = {
            'id': variety.id,
            'name': variety.name,
            'product_id': variety.product.id,
            'image': variety.image.url if variety.image else None
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Count Views
class CountListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    Display list of count options
    """
    model = CountOption
    template_name = 'dashboard/product/count_list.html'
    context_object_name = 'counts'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(value__icontains=search)
        
        # دع الترتيب يعتمد على حقل numeric_sort (القيم الرقمية أولاً)
        # ثم قم بترتيب القيم غير الرقمية أبجدياً
        return queryset.order_by('numeric_sort', 'value')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Number of count options
        context['count_options_count'] = CountOption.objects.count()
        
        # Preserve GET parameters for pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        
        return context

class CountCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Add a new count option
    """
    model = CountOption
    fields = ['value']
    success_url = reverse_lazy('dashboard:counts')
    
    def form_valid(self, form):
        messages.success(self.request, f"Count option '{form.instance.value}' added successfully.")
        return super().form_valid(form)
        
    def form_invalid(self, form):
        # إذا كان الطلب AJAX، أرجع رد JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
        # إذا كان طلب عادي، إعادة توجيه للقائمة مع رسالة خطأ
        for error in form.errors.values():
            messages.error(self.request, error[0])
        return HttpResponseRedirect(self.success_url)
    
    def get(self, request, *args, **kwargs):
        # إعادة توجيه لصفحة القائمة لجميع طلبات GET
        return HttpResponseRedirect(reverse_lazy('dashboard:counts'))
    
    def post(self, request, *args, **kwargs):
        # إذا كان الطلب AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            if form.is_valid():
                self.object = form.save()
                return JsonResponse({
                    'success': True,
                    'id': self.object.id,
                    'value': self.object.value
                })
            else:
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list[0]
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
        # الطلب العادي (غير AJAX)
        return super().post(request, *args, **kwargs)

class CountUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    Update an existing count option
    """
    model = CountOption
    fields = ['value']
    success_url = reverse_lazy('dashboard:counts')
    
    def form_valid(self, form):
        messages.success(self.request, f"Count option '{form.instance.value}' updated successfully.")
        return super().form_valid(form)
        
    def form_invalid(self, form):
        # إذا كان الطلب AJAX، أرجع رد JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
        # إذا كان طلب عادي، إعادة توجيه للقائمة مع رسالة خطأ
        for error in form.errors.values():
            messages.error(self.request, error[0])
        return HttpResponseRedirect(self.success_url)
    
    def get(self, request, *args, **kwargs):
        # إذا كان الطلب AJAX، نرجع بيانات العنصر كـ JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            return JsonResponse({
                'id': self.object.id,
                'value': self.object.value
            })
        # إعادة توجيه لصفحة القائمة لطلبات GET العادية
        return HttpResponseRedirect(reverse_lazy('dashboard:counts'))
    
    def post(self, request, *args, **kwargs):
        # إذا كان الطلب AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            form = self.get_form()
            if form.is_valid():
                self.object = form.save()
                return JsonResponse({
                    'success': True,
                    'id': self.object.id,
                    'value': self.object.value
                })
            else:
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list[0]
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
        # الطلب العادي (غير AJAX)
        return super().post(request, *args, **kwargs)

class CountDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    Delete a count option
    """
    model = CountOption
    success_url = reverse_lazy('dashboard:counts')
    
    def delete(self, request, *args, **kwargs):
        count = self.get_object()
        count_value = count.value
        count.delete()
        messages.success(request, f"Count option '{count_value}' deleted successfully.")
        
        # إذا كان الطلب AJAX، نرجع رد JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True
            })
        
        return HttpResponseRedirect(self.success_url)
    
    def get(self, request, *args, **kwargs):
        # إعادة توجيه لصفحة القائمة بدلاً من عرض صفحة تأكيد الحذف
        return HttpResponseRedirect(reverse_lazy('dashboard:counts'))
        
    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

@login_required
def season_icon_detail_api(request, pk):
    """
    Return season icon details in JSON format for AJAX requests
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        from apps.products.models import SeasonIcon
        icon = SeasonIcon.objects.get(pk=pk)
        
        data = {
            'id': icon.id,
            'name': icon.name,
            'description': icon.description,
            'icon': icon.icon.url if icon.icon else None,
            'color_code': icon.color_code,
            'display_order': icon.display_order
        }
        
        return JsonResponse(data)
    except SeasonIcon.DoesNotExist:
        return JsonResponse({'error': 'Season icon not found'}, status=404)
