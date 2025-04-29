# pyright: reportMissingImports=false
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from .models import Product, Seasonality, ProductPackaging, CountOption, SizeOption, PackagingOption, ProductVariety
# type: ignore [import-unresolved]
from .forms import SpecialProductForm
from apps.core.forms import InquiryForm
from django.http import JsonResponse


class ProductListView(ListView):
    """
    Product listing view
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        """
        Override the default queryset to filter only active products.
        """
        queryset = super().get_queryset()
        
        # ترتيب المنتجات حسب حقل الترتيب ثم الاسم
        queryset = queryset.order_by('order', 'name')
        
        # طباعة المنتجات للتحقق منها
        products_list = list(queryset)
        print(f"[DEBUG] Products count: {len(products_list)}")
        for product in products_list:
            print(f"[DEBUG] Product: {product.id} - {product.name} - {product.slug}")
        
        return queryset
    

class ProductDetailView(DetailView):
    """
    Product detail view
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        print(f"[DEBUG] Viewing product: {product.id} - {product.name}")
        
        # تأكد من استخدام استعلام مباشر وغير متأثر بالمستخدم لبيانات الموسمية
        fresh_seasonality = Seasonality.objects.filter(
            product=product, 
            variety__isnull=True,
            type='fresh'
        ).first()
        
        iqf_seasonality = Seasonality.objects.filter(
            product=product, 
            variety__isnull=True,
            type='iqf'
        ).first()
        
        print(f"[DEBUG] Fresh seasonality: {fresh_seasonality}")
        print(f"[DEBUG] IQF seasonality: {iqf_seasonality}")
        
        # إضافة بيانات الموسمية للقالب
        context['fresh_seasonality'] = [fresh_seasonality] if fresh_seasonality else []
        context['iqf_seasonality'] = [iqf_seasonality] if iqf_seasonality else []
        
        # Add old packaging information (for backward compatibility)
        fresh_packaging = product.packaging.filter(type='fresh').first()
        iqf_packaging = product.packaging.filter(type='iqf').first()
        context['fresh_packaging'] = fresh_packaging
        context['iqf_packaging'] = iqf_packaging
        
        # Add new packaging options from PackagingOption model (for backward compatibility)
        if product.has_packaging:
            context['fresh_packaging_options'] = product.available_packaging.filter(type='fresh')
            context['iqf_packaging_options'] = product.available_packaging.filter(type='iqf')
        
        # Add new packaging types from ProductPackagingType model
        context['fresh_packaging_types'] = product.product_packaging_types.filter(type='fresh').order_by('order')
        context['iqf_packaging_types'] = product.product_packaging_types.filter(type='iqf').order_by('order')
        
        # Add new size options
        if product.has_size:
            context['size_options'] = product.available_sizes.all()
        
        # Add new count options
        if product.has_counts:
            context['count_options'] = product.available_counts.all()
            
        # إضافة معلومات الأيقونات للموسمية
        # معالجة أيقونات للمنتجات الطازجة
        if fresh_seasonality:
            # التحقق إذا كان للموسمية أيقونة خاصة
            context['fresh_icon'] = fresh_seasonality.season_icon if fresh_seasonality.season_icon else product.seasonality_icon
        else:
            context['fresh_icon'] = product.seasonality_icon if product.seasonality_icon else product.icon
            
        # معالجة أيقونات للمنتجات المجمدة
        if iqf_seasonality:
            # التحقق إذا كان للموسمية أيقونة خاصة
            context['iqf_icon'] = iqf_seasonality.season_icon if iqf_seasonality.season_icon else product.seasonality_icon
        else:
            context['iqf_icon'] = product.seasonality_icon if product.seasonality_icon else product.iqf_icon if product.iqf_icon else product.icon
            
        return context


class VarietyDetailView(DetailView):
    """
    Product variety detail view
    """
    model = ProductVariety
    template_name = 'products/product_detail.html'
    context_object_name = 'variety'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variety = self.get_object()
        
        print(f"[DEBUG] Viewing variety: {variety.id} - {variety.name}")
        
        # Add product to context for template compatibility
        product = variety.product
        context['product'] = product
        
        # استخدام استعلام مباشر للموسمية الخاصة بالصنف
        fresh_seasonality = Seasonality.objects.filter(
            variety=variety,
            type='fresh'
        ).first()
        
        iqf_seasonality = Seasonality.objects.filter(
            variety=variety,
            type='iqf'
        ).first()
        
        # إذا لم يكن هناك بيانات موسمية للصنف، حاول الحصول عليها من المنتج الأصلي
        if not fresh_seasonality:
            fresh_seasonality = Seasonality.objects.filter(
                product=product,
                variety__isnull=True,
                type='fresh'
            ).first()
            print(f"[DEBUG] Using parent product fresh seasonality")
        
        if not iqf_seasonality:
            iqf_seasonality = Seasonality.objects.filter(
                product=product,
                variety__isnull=True,
                type='iqf'
            ).first()
            print(f"[DEBUG] Using parent product iqf seasonality")
        
        print(f"[DEBUG] Fresh seasonality: {fresh_seasonality}")
        print(f"[DEBUG] IQF seasonality: {iqf_seasonality}")
        
        # إضافة بيانات الموسمية للقالب
        context['fresh_seasonality'] = [fresh_seasonality] if fresh_seasonality else []
        context['iqf_seasonality'] = [iqf_seasonality] if iqf_seasonality else []
        
        # Use product packaging information 
        
        # Add old packaging information (for backward compatibility)
        fresh_packaging = product.packaging.filter(type='fresh').first()
        iqf_packaging = product.packaging.filter(type='iqf').first()
        context['fresh_packaging'] = fresh_packaging
        context['iqf_packaging'] = iqf_packaging
        
        # Add new packaging options from PackagingOption model (for backward compatibility)
        if product.has_packaging:
            context['fresh_packaging_options'] = product.available_packaging.filter(type='fresh')
            context['iqf_packaging_options'] = product.available_packaging.filter(type='iqf')
        
        # Add new packaging types from ProductPackagingType model
        context['fresh_packaging_types'] = product.product_packaging_types.filter(type='fresh').order_by('order')
        context['iqf_packaging_types'] = product.product_packaging_types.filter(type='iqf').order_by('order')
        
        # Add new size options
        if product.has_size:
            context['size_options'] = product.available_sizes.all()
        
        # Add new count options
        if product.has_counts:
            context['count_options'] = product.available_counts.all()
            
        # إضافة معلومات الأيقونات للموسمية مع التحقق من ترتيب الأولوية
        # معالجة أيقونات للفرايتي الطازجة
        if fresh_seasonality:
            # الأولوية 1: أيقونة الموسمية للفرايتي
            # الأولوية 2: أيقونة الفرايتي نفسه
            # الأولوية 3: أيقونة الموسمية للمنتج
            # الأولوية 4: أيقونة المنتج العامة
            if fresh_seasonality.season_icon:
                context['fresh_icon'] = fresh_seasonality.season_icon
            elif variety.image:
                context['fresh_icon'] = variety.image
            elif product.seasonality_icon:
                context['fresh_icon'] = product.seasonality_icon
            else:
                context['fresh_icon'] = product.icon
        else:
            # إذا لم يكن للفرايتي موسمية خاصة
            if variety.image:
                context['fresh_icon'] = variety.image
            elif product.seasonality_icon:
                context['fresh_icon'] = product.seasonality_icon
            else:
                context['fresh_icon'] = product.icon
                
        # معالجة أيقونات للفرايتي المجمدة
        if iqf_seasonality:
            if iqf_seasonality.season_icon:
                context['iqf_icon'] = iqf_seasonality.season_icon
            elif variety.image:
                context['iqf_icon'] = variety.image
            elif product.seasonality_icon:
                context['iqf_icon'] = product.seasonality_icon
            elif product.iqf_icon:
                context['iqf_icon'] = product.iqf_icon
            else:
                context['iqf_icon'] = product.icon
        else:
            # إذا لم يكن للفرايتي موسمية مجمدة خاصة
            if variety.image:
                context['iqf_icon'] = variety.image
            elif product.seasonality_icon:
                context['iqf_icon'] = product.seasonality_icon
            elif product.iqf_icon:
                context['iqf_icon'] = product.iqf_icon
            else:
                context['iqf_icon'] = product.icon
            
        return context


class SpecialProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    إنشاء منتج مخصوص
    """
    model = Product
    form_class = SpecialProductForm
    template_name = 'products/special_product_form.html'
    permission_required = 'products.add_product'
    
    def get_success_url(self):
        messages.success(self.request, 'Special product created successfully!')
        return reverse('dashboard:products')

class SpecialProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    تعديل منتج مخصوص
    """
    model = Product
    form_class = SpecialProductForm
    template_name = 'products/special_product_form.html'
    permission_required = 'products.change_product'
    
    def get_queryset(self):
        # فقط المنتجات المخصوصة
        return Product.objects.filter(is_special=True)
    
    def get_success_url(self):
        messages.success(self.request, 'Special product updated successfully!')
        return reverse('dashboard:products')

def products_list_api(request):
    """
    نقطة نهاية API لجلب قائمة المنتجات
    """
    # طباعة معلومات الطلب للتشخيص
    print(f"[API DEBUG] Received request for products list API at: {request.path}")
    print(f"[API DEBUG] Request method: {request.method}")
    
    # استخدام all() بدلاً من filter(is_active=True) لأن is_active غير موجود
    products = Product.objects.all().order_by('order', 'name')
    
    # طباعة عدد المنتجات التي تم جلبها
    product_count = products.count()
    print(f"[API DEBUG] Retrieved {product_count} products")
    
    products_data = [
        {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
        }
        for product in products
    ]
    
    # السماح بطلبات CORS لأي نطاق (للتطوير فقط، ليس للإنتاج)
    response = JsonResponse(products_data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
    
    return response
