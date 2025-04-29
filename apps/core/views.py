from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
import requests
from django.conf import settings
from apps.products.models import Product, Office
from .forms import QuoteRequestForm
from apps.branches.models import Branch, MainBranch
from apps.inquiries.views import ContactFormView


class HomeView(TemplateView):
    """
    الصفحة الرئيسية للموقع
    تعرض صفحة under construction للزوار عندما يكون الإعداد UNDER_CONSTRUCTION مفعل
    أو للزوار غير المسجلين حسب الحالة السابقة
    """
    template_name = 'core/home.html'
    
    def get_template_names(self):
        """
        تحديد القالب المناسب بناءً على حالة تسجيل دخول المستخدم وإعداد UNDER_CONSTRUCTION
        """
        # عرض صفحة البناء فقط إذا كان الإعداد مفعل وليس مستخدم مسجل دخوله
        under_construction = getattr(settings, 'UNDER_CONSTRUCTION', True)
        if under_construction and not self.request.user.is_authenticated:
            return ['core/under_construction.html']
        return [self.template_name]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add featured products
        context['featured_products'] = Product.objects.filter(is_featured=True)[:4]
        # Add products for slider
        context['slider_products'] = Product.objects.filter(is_in_slider=True)[:4]
        return context


class AboutView(TemplateView):
    """
    صفحة حول الشركة
    """
    template_name = 'core/about.html'


# Use ContactFormView from inquiries app
ContactView = ContactFormView


class QuoteRequestView(FormView):
    """
    صفحة طلب عرض سعر
    """
    template_name = 'core/quote_request.html'
    form_class = QuoteRequestForm
    success_url = reverse_lazy('core:thank_you')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Thank you for your quote request. We will get back to you with a detailed quote soon.')
        return super().form_valid(form)


class ThankYouView(TemplateView):
    """
    صفحة الشكر بعد إرسال النموذج
    """
    template_name = 'core/thank_you.html'


def ip_lookup_proxy(request):
    """
    خدمة وسيطة للتحقق من عنوان IP والحصول على رمز الدولة
    تستخدم لحل مشكلة CORS عند الطلب من ipapi.co
    """
    try:
        # Try to get IP data from service
        response = requests.get('https://ipapi.co/json/', timeout=3)
        
        # Check if request is successful
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data)
        else:
            # Return Egypt as default country in case of error
            return JsonResponse({'country_code': 'eg'})
    except Exception:
        # Return Egypt as default country in case of exception
        return JsonResponse({'country_code': 'eg'})
