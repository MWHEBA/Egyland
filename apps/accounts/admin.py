from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Address

# تعريف إدارة الملف الشخصي كخيار إضافي لنموذج المستخدم
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'
    
    def get_queryset(self, request):
        # تجاوز هذه المشكلة بإظهار فقط الملفات الشخصية الموجودة
        return super().get_queryset(request).filter(user__isnull=False)

# تعريف إدارة العناوين
class AddressAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'location_type', 'city', 'is_default')
    list_filter = ('location_type', 'city', 'country', 'is_default')
    search_fields = ('title', 'user__username', 'street_address', 'city')
    list_per_page = 25

# توسيع نموذج إدارة المستخدم الافتراضي
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_account_type')
    
    def get_account_type(self, obj):
        try:
            return obj.profile.get_account_type_display()
        except Profile.DoesNotExist:
            return "لا يوجد ملف شخصي"
    
    get_account_type.short_description = 'نوع الحساب'

# إعادة تسجيل نموذج المستخدم
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)
