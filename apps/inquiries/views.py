from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import json

from .models import Inquiry
from .forms import InquiryForm, ProductInquiryForm, ProductRequestForm
from apps.dashboard.mixins import StaffRequiredMixin
from apps.branches.models import Branch, MainBranch
from apps.user_management.models import Role

# فحص ما إذا كان المستخدم لديه دور Developer
def is_developer(user):
    """
    التحقق مما إذا كان المستخدم يمتلك صلاحية Developer
    """
    # طباعة لمساعدتنا في تشخيص المشكلة
    print(f"DEBUG: Checking if user {user.username} is developer")
    print(f"DEBUG: is_superuser = {user.is_superuser}")
    
    # إذا كان المستخدم سوبر يوزر
    if user.is_superuser:
        print("DEBUG: User is superuser, returning True")
        return True
    
    # محاولة التحقق من الأدوار
    try:
        # فحص جميع الأدوار بشكل مباشر
        user_roles = user.user_roles.all()
        print(f"DEBUG: User roles: {[ur.role.name for ur in user_roles]}")
        
        # فحص إذا كان لديه دور developer بأي طريقة
        has_developer = user.user_roles.filter(role__name=Role.DEVELOPER).exists()
        print(f"DEBUG: has_developer role = {has_developer}")
        
        # البحث يدوياً عن دور developer
        for user_role in user_roles:
            if user_role.role.name == Role.DEVELOPER:
                print(f"DEBUG: Found developer role, returning True")
                return True
                
        # إذا وصلنا إلى هنا، فلا يوجد دور developer
        print(f"DEBUG: Developer role not found, returning {has_developer}")
        return has_developer
    except Exception as e:
        print(f"DEBUG: Exception occurred: {str(e)}")
        return False


class ContactFormView(FormView):
    """
    عرض وإرسال نموذج الاتصال العام
    """
    template_name = 'core/contact.html'
    form_class = InquiryForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # إضافة معلومات الفروع والمقر الرئيسي للصفحة
        context['branches'] = Branch.objects.filter(is_active=True).order_by('display_order')
        context['main_branch'] = MainBranch.get_main_branch()
        return context
    
    def form_valid(self, form):
        """
        معالجة النموذج عند نجاح التحقق
        """
        inquiry = form.save()
        
        # إرسال بريد إلكتروني للشركة
        self._send_notification_email(inquiry)
        
        # التحقق مما إذا كان الطلب AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your message. We will get back to you soon.'
            })
            
        messages.success(self.request, 'Thank you for your message. We will get back to you soon.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        معالجة النموذج عند فشل التحقق
        """
        # التحقق مما إذا كان الطلب AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': form.errors
            }, status=400)
            
        return super().form_invalid(form)
    
    def _send_notification_email(self, inquiry):
        """
        إرسال إشعار بريد إلكتروني للشركة
        """
        subject = f'New Contact Message from {inquiry.name}'
        message = f"""
You have received a new contact message:

Name: {inquiry.name}
Company: {inquiry.company}
Email: {inquiry.email}
Phone: {inquiry.phone}
Country: {inquiry.country}

Message:
{inquiry.message}

Date: {inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.CONTACT_EMAIL]
        
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            # Log the error but don't break the user experience
            print(f"Error sending email notification: {str(e)}")


class ProductInquiryFormView(FormView):
    """
    عرض وإرسال نموذج الاستفسار عن المنتجات - معطلة لصالح المودال
    يتم تحويل جميع الطلبات للصفحة الرئيسية
    """
    template_name = 'inquiries/product_inquiry_form.html'
    form_class = ProductInquiryForm
    success_url = reverse_lazy('core:thank_you')
    
    def dispatch(self, request, *args, **kwargs):
        """
        تحويل جميع الطلبات للصفحة الرئيسية
        """
        return redirect('/')
    
    def get_initial(self):
        """
        تهيئة النموذج مع البيانات الأولية
        """
        initial = super().get_initial()
        
        # إذا تم تمرير معرف المنتج، يتم تعيينه في النموذج
        product_id = self.request.GET.get('product_id') or self.request.POST.get('product_id')
        if product_id:
            initial['inquiry_type'] = 'product_specific'
            initial['products'] = [product_id]
            
        return initial
    
    def form_valid(self, form):
        """
        معالجة النموذج عند نجاح التحقق
        """
        inquiry = form.save()
        
        # إرسال بريد إلكتروني للشركة
        self._send_notification_email(inquiry)
        
        # التحقق مما إذا كان الطلب AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your inquiry. We will get back to you soon.'
            })
        
        messages.success(self.request, 'Thank you for your inquiry. We will get back to you soon.')
        return super().form_valid(form)
        
    def form_invalid(self, form):
        """
        معالجة النموذج عند فشل التحقق
        """
        # التحقق مما إذا كان الطلب AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': form.errors
            }, status=400)
        
        return super().form_invalid(form)
    
    def _send_notification_email(self, inquiry):
        """
        إرسال إشعار بريد إلكتروني للشركة
        """
        subject = f'New Product Inquiry from {inquiry.name}'
        
        # إعداد محتوى البريد
        message = f"""
You have received a new product inquiry:

Name: {inquiry.name}
Company: {inquiry.company}
Email: {inquiry.email}
Phone: {inquiry.phone}
Country: {inquiry.country}

"""
        
        # إضافة تفاصيل المنتجات إذا كان الاستفسار متعلق بمنتج
        if inquiry.is_product_related:
            message += "Products of interest:\n"
            for product in inquiry.products.all():
                message += f"- {product.name}\n"
            message += "\n"
            
        message += f"""
Message:
{inquiry.message}

Date: {inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.CONTACT_EMAIL]
        
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            # Log the error but don't break the user experience
            print(f"Error sending email notification: {str(e)}")


class ProductRequestFormView(FormView):
    """
    عرض وإرسال نموذج طلب المنتج
    """
    template_name = 'inquiries/product_request_form.html'
    form_class = ProductRequestForm
    success_url = reverse_lazy('core:thank_you')
    
    def get_initial(self):
        """
        تهيئة النموذج مع البيانات الأولية
        """
        initial = super().get_initial()
        
        # إذا تم تمرير معرف المنتج، يتم تعيينه في النموذج
        product_id = self.request.GET.get('product_id')
        if product_id:
            initial['inquiry_type'] = 'product_specific'
            initial['products'] = [product_id]
            
        return initial
    
    def form_valid(self, form):
        """
        معالجة النموذج عند نجاح التحقق
        """
        inquiry = form.save()
        
        # إرسال بريد إلكتروني للشركة
        self._send_notification_email(inquiry)
        
        messages.success(self.request, 'Thank you for your product request. We will get back to you soon.')
        return super().form_valid(form)
    
    def _send_notification_email(self, inquiry):
        """
        إرسال إشعار بريد إلكتروني للشركة
        """
        subject = f'New Product Request from {inquiry.name}'
        
        # إعداد محتوى البريد
        message = f"""
You have received a new product request:

Name: {inquiry.name}
Company: {inquiry.company}
Email: {inquiry.email}
Phone: {inquiry.phone}
Country: {inquiry.country}

"""
        
        # إضافة تفاصيل المنتجات والكميات
        if inquiry.is_product_related:
            message += "Products requested:\n"
            for product in inquiry.products.all():
                message += f"- {product.name}\n"
            message += "\n"
            
            if inquiry.product_quantity:
                message += f"Requested Quantity: {inquiry.product_quantity}\n"
            if inquiry.target_price_range:
                message += f"Target Price Range: {inquiry.target_price_range}\n"
            if inquiry.preferred_delivery_date:
                message += f"Preferred Delivery Date: {inquiry.preferred_delivery_date}\n"
            message += "\n"
            
        message += f"""
Additional information:
{inquiry.message}

Date: {inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.CONTACT_EMAIL]
        
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            # Log the error but don't break the user experience
            print(f"Error sending email notification: {str(e)}")


# -------- Dashboard Views -------- #

class InquiryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    عرض قائمة الاستفسارات في لوحة التحكم
    """
    model = Inquiry
    template_name = 'dashboard/inquiries/list.html'
    context_object_name = 'inquiries'
    paginate_by = 15
    
    def get_queryset(self):
        """
        الحصول على استعلام الاستفسارات مع تطبيق التصفية
        """
        queryset = super().get_queryset()
        
        # تطبيق التصفية من معلمات GET
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        inquiry_type = self.request.GET.get('type')
        if inquiry_type:
            queryset = queryset.filter(type=inquiry_type)
            
        is_responded = self.request.GET.get('is_responded')
        if is_responded == 'true':
            queryset = queryset.filter(is_responded=True)
        elif is_responded == 'false':
            queryset = queryset.filter(is_responded=False)
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(email__icontains=search) |
                Q(company__icontains=search) |
                Q(message__icontains=search)
            )
            
        # تطبيق الترتيب
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        إضافة بيانات إضافية للسياق
        """
        context = super().get_context_data(**kwargs)
        
        context['status_choices'] = dict(Inquiry.INQUIRY_STATUS_CHOICES)
        context['type_choices'] = dict(Inquiry.INQUIRY_TYPE_CHOICES)
        
        # الحفاظ على معلمات GET للصفحات
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        
        return context


class InquiryDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """
    عرض تفاصيل الاستفسار
    """
    model = Inquiry
    template_name = 'dashboard/inquiries/detail.html'
    context_object_name = 'inquiry'
    
    def get_context_data(self, **kwargs):
        """
        إضافة بيانات إضافية للسياق
        """
        context = super().get_context_data(**kwargs)
        context['status_choices'] = dict(Inquiry.INQUIRY_STATUS_CHOICES)
        
        # تصحيح التحقق من صلاحية المستخدم لحذف الاستفسارات
        is_developer_result = is_developer(self.request.user)
        print(f"DEBUG: is_developer result = {is_developer_result}")
        
        # التأكد من صلاحية الحذف - إذا كان سوبر يوزر أو لديه دور Developer
        can_delete = is_developer_result or self.request.user.is_superuser
        print(f"DEBUG: can_delete final result = {can_delete}")
        
        context['can_delete_inquiry'] = can_delete
        
        # إضافة قيمة الثابت Role.DEVELOPER للقالب للتصحيح
        context['role_developer_constant'] = Role.DEVELOPER
        
        return context


@login_required
@csrf_exempt
def update_inquiry_status(request, pk):
    """
    تحديث حالة الاستفسار عبر AJAX
    """
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            is_responded = data.get('is_responded', None)
            admin_notes = data.get('admin_notes', None)
            
            inquiry = get_object_or_404(Inquiry, pk=pk)
            
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


@csrf_exempt
def submit_inquiry_via_ajax(request):
    """
    معالجة استفسارات المنتجات المرسلة عبر AJAX (من المودال)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    form = ProductInquiryForm(request.POST)
    
    if form.is_valid():
        inquiry = form.save()
        
        # إرسال بريد إلكتروني للشركة
        subject = f'New Product Inquiry from {inquiry.name}'
        
        # إعداد محتوى البريد
        message = f"""
You have received a new product inquiry:

Name: {inquiry.name}
Company: {inquiry.company}
Email: {inquiry.email}
Phone: {inquiry.phone}
Country: {inquiry.country}

"""
        
        # إضافة تفاصيل المنتجات إذا كان الاستفسار متعلق بمنتج
        if inquiry.is_product_related:
            message += "Products of interest:\n"
            for product in inquiry.products.all():
                message += f"- {product.name}\n"
            message += "\n"
            
        message += f"""
Message:
{inquiry.message}

Date: {inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.CONTACT_EMAIL]
        
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            # Log the error but don't break the user experience
            print(f"Error sending email notification: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your inquiry. We will get back to you soon.'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Please correct the errors below.',
            'errors': form.errors
        }, status=400)


@csrf_exempt
def products_api(request):
    """
    وظيفة API للحصول على قائمة المنتجات للاستخدام في مودال الاستفسارات
    """
    try:
        from apps.products.models import Product
        
        # استدعاء كل المنتجات بدون فلترة is_active (غير موجود في النموذج)
        products = Product.objects.all().order_by('order', 'name')
        
        products_data = [
            {
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
            }
            for product in products
        ]
        
        # رسالة تشخيصية
        print(f"[API DEBUG] Returned {len(products_data)} products for modal API")
        
        response = JsonResponse(products_data, safe=False)
        # السماح بوصول CORS
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
        
        return response
    except Exception as e:
        print(f"[API ERROR] Error in products_api: {str(e)}")
        # في حالة حدوث خطأ، إرجاع قائمة ثابتة للمنتجات
        fallback_products = [
            {'id': 1, 'name': 'Oranges', 'slug': 'oranges'},
            {'id': 2, 'name': 'Strawberry', 'slug': 'strawberry'},
            {'id': 3, 'name': 'Mango', 'slug': 'mango'},
            {'id': 4, 'name': 'Pomegranate', 'slug': 'pomegranate'},
            {'id': 5, 'name': 'Guava', 'slug': 'guava'},
            {'id': 6, 'name': 'Lemon', 'slug': 'lemon'},
            {'id': 7, 'name': 'Grapes', 'slug': 'grapes'},
            {'id': 8, 'name': 'Apple', 'slug': 'apple'},
            {'id': 9, 'name': 'Banana', 'slug': 'banana'},
            {'id': 10, 'name': 'Pineapple', 'slug': 'pineapple'},
            {'id': 11, 'name': 'Kiwi', 'slug': 'kiwi'}
        ]
        
        response = JsonResponse(fallback_products, safe=False)
        # السماح بوصول CORS
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
        
        return response 


@login_required
@user_passes_test(is_developer)
def delete_inquiry(request, pk):
    """
    حذف الاستفسار - متاح فقط للمستخدمين بصلاحية Developer
    """
    inquiry = get_object_or_404(Inquiry, pk=pk)
    
    if request.method == 'POST':
        inquiry.delete()
        messages.success(request, 'تم حذف الاستفسار بنجاح')
        return redirect('dashboard:inquiries')
    
    return render(request, 'dashboard/inquiries/delete_confirmation.html', {
        'inquiry': inquiry
    }) 