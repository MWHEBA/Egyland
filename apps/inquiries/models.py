from django.db import models
from apps.products.models import Product
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Inquiry(models.Model):
    """
    نموذج موحد للاستفسارات والرسائل واتصالات العملاء
    """
    INQUIRY_TYPE_CHOICES = (
        ('contact', 'Contact Message'),
        ('product_inquiry', 'Product Inquiry'),
        ('product_request', 'Product Request'),
    )
    
    INQUIRY_STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Basic information
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    message = models.TextField()
    
    # Inquiry type and status
    type = models.CharField(max_length=20, choices=INQUIRY_TYPE_CHOICES, default='contact')
    status = models.CharField(max_length=15, choices=INQUIRY_STATUS_CHOICES, default='new')
    
    # Related products (for product inquiries and requests)
    products = models.ManyToManyField(Product, blank=True, related_name='inquiries')
    
    # For product requests
    product_quantity = models.CharField(max_length=50, blank=True)
    target_price_range = models.CharField(max_length=100, blank=True)
    preferred_delivery_date = models.DateField(null=True, blank=True)
    
    # For admin use
    admin_notes = models.TextField(blank=True, help_text="Internal notes (not visible to customers)")
    is_responded = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inquiry"
        verbose_name_plural = "Inquiries"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_type_display()} ({self.get_status_display()})"
    
    @property
    def is_product_related(self):
        """
        التحقق مما إذا كان الاستفسار متعلق بمنتج
        """
        return self.type in ['product_inquiry', 'product_request']
    
    @property
    def days_since_creation(self):
        """
        حساب عدد الأيام منذ إنشاء الاستفسار
        """
        from django.utils import timezone
        import datetime
        
        now = timezone.now()
        diff = now - self.created_at
        
        return diff.days


class InquiryNote(models.Model):
    """
    نموذج لتخزين ملاحظات الاستفسارات
    """
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='inquiry_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Inquiry Note"
        verbose_name_plural = "Inquiry Notes"
        ordering = ['-created_at']
    
    def __str__(self):
        if self.created_by:
            user_name = self.created_by.get_full_name() or self.created_by.username
        else:
            user_name = "Unknown"
        return f"Note by {user_name} on {self.created_at.strftime('%Y-%m-%d %H:%M')}" 