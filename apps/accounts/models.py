from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class Profile(models.Model):
    """
    نموذج الملف الشخصي للمستخدم
    يرتبط مع المستخدم الافتراضي في جانغو
    """
    ACCOUNT_TYPES = (
        ('personal', _('شخصي')),
        ('business', _('أعمال')),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='personal', verbose_name=_('نوع الحساب'))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم الهاتف'))
    address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))
    company_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('اسم الشركة'))
    bio = models.TextField(blank=True, null=True, verbose_name=_('نبذة'))
    profile_picture = models.ImageField(upload_to='profile_pics', default='profile_pics/default.jpg', verbose_name=_('الصورة الشخصية'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الانضمام'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('آخر تحديث'))
    
    class Meta:
        verbose_name = _('الملف الشخصي')
        verbose_name_plural = _('الملفات الشخصية')
        
    def __str__(self):
        return f"{self.user.username} - {self.get_account_type_display()}"


class Address(models.Model):
    """
    نموذج عناوين المستخدم
    """
    LOCATION_TYPES = (
        ('home', _('منزل')),
        ('work', _('عمل')),
        ('other', _('آخر')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name=_('المستخدم'))
    title = models.CharField(max_length=100, verbose_name=_('العنوان المختصر'))
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='home', verbose_name=_('نوع العنوان'))
    street_address = models.TextField(verbose_name=_('العنوان التفصيلي'))
    city = models.CharField(max_length=100, verbose_name=_('المدينة'))
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المحافظة/الولاية'))
    country = models.CharField(max_length=100, verbose_name=_('البلد'))
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الرمز البريدي'))
    is_default = models.BooleanField(default=False, verbose_name=_('العنوان الافتراضي'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('العنوان')
        verbose_name_plural = _('العناوين')
        ordering = ['-is_default', '-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    إنشاء ملف شخصي تلقائياً عند إنشاء مستخدم جديد
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    حفظ الملف الشخصي عند حفظ المستخدم
    """
    instance.profile.save()
