from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.utils import timezone
from .models import UserActivity, UserAccountStatus, UserLoginAttempt, UserSession
import logging

logger = logging.getLogger('user_management')

@receiver(post_save, sender=User)
def create_user_account_status(sender, instance, created, **kwargs):
    """
    إنشاء حالة حساب عند إنشاء مستخدم جديد
    """
    if created:
        UserAccountStatus.objects.create(user=instance)
        logger.info(f"تم إنشاء حالة حساب للمستخدم {instance.username}")


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    معالجة تسجيل الدخول الناجح
    """
    # تسجيل نشاط تسجيل الدخول
    ip_address = get_client_ip(request)
    UserActivity.objects.create(
        user=user,
        activity_type='login',
        description=f"تسجيل دخول ناجح من {ip_address}",
        ip_address=ip_address
    )
    
    # تسجيل جلسة
    if hasattr(request, 'session'):
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    # تسجيل محاولة تسجيل دخول ناجحة
    UserLoginAttempt.objects.create(
        username=user.username,
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        successful=True
    )
    
    logger.info(f"تسجيل دخول ناجح للمستخدم {user.username} من {ip_address}")


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """
    معالجة تسجيل الخروج
    """
    if user:
        ip_address = get_client_ip(request)
        
        # تسجيل نشاط تسجيل الخروج
        UserActivity.objects.create(
            user=user,
            activity_type='logout',
            description=f"تسجيل خروج من {ip_address}",
            ip_address=ip_address
        )
        
        # تحديث جلسة
        if hasattr(request, 'session'):
            try:
                session = UserSession.objects.get(
                    user=user,
                    session_key=request.session.session_key,
                    is_active=True
                )
                session.logout_time = timezone.now()
                session.is_active = False
                session.save()
            except UserSession.DoesNotExist:
                pass
        
        logger.info(f"تسجيل خروج للمستخدم {user.username} من {ip_address}")


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """
    معالجة فشل تسجيل الدخول
    """
    ip_address = get_client_ip(request)
    
    # تسجيل محاولة تسجيل دخول فاشلة
    UserLoginAttempt.objects.create(
        username=credentials.get('username', ''),
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        successful=False,
        failure_reason='بيانات اعتماد غير صحيحة'
    )
    
    logger.warning(f"محاولة تسجيل دخول فاشلة للمستخدم {credentials.get('username', '')} من {ip_address}")


def get_client_ip(request):
    """
    الحصول على عنوان IP للعميل
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip 