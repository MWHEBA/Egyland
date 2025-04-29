from django.contrib import admin
from .models import Inquiry


class InquiryAdmin(admin.ModelAdmin):
    """
    إدارة الاستفسارات في لوحة الإدارة
    """
    list_display = ['name', 'company', 'email', 'type', 'status', 'created_at', 'is_responded']
    list_filter = ['type', 'status', 'created_at', 'is_responded']
    search_fields = ['name', 'company', 'email', 'message']
    readonly_fields = ['created_at', 'updated_at']
    
    # Products as filter_horizontal for easier selection
    filter_horizontal = ['products']
    
    fieldsets = [
        ('Contact Information', {
            'fields': ('name', 'company', 'email', 'phone', 'country')
        }),
        ('Inquiry Details', {
            'fields': ('type', 'message', 'products', 'status')
        }),
        ('Product Request Information', {
            'fields': ('product_quantity', 'target_price_range', 'preferred_delivery_date'),
            'classes': ('collapse',)
        }),
        ('Admin Information', {
            'fields': ('admin_notes', 'is_responded', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    def get_queryset(self, request):
        """
        تحسين الاستعلام بإضافة prefetch_related للمنتجات
        """
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('products')


admin.site.register(Inquiry, InquiryAdmin) 