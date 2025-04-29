from django.contrib import admin
from .models import Branch, MainBranch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """
    إدارة الفروع في واجهة الأدمن
    """
    list_display = ('country_name', 'address', 'phone', 'email', 'display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('country_name', 'address', 'email')
    list_editable = ('display_order', 'is_active')
    ordering = ('display_order',)

@admin.register(MainBranch)
class MainBranchAdmin(admin.ModelAdmin):
    """
    إدارة معلومات الفرع الرئيسي في واجهة الأدمن
    """
    list_display = ('company_name', 'address', 'phone', 'email', 'is_active')
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'logo', 'description', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'fax', 'email', 'website')
        }),
        ('Legal Information', {
            'fields': ('tax_number', 'registration_number')
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'instagram', 'linkedin')
        }),
    )
    def has_add_permission(self, request):
        # Check if a record exists before allowing adding a new one
        if MainBranch.objects.exists():
            return False
        return super().has_add_permission(request)
