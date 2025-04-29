from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages

class StaffRequiredMixin(UserPassesTestMixin):
    """
    ميكسن للتحقق من أن المستخدم هو عضو في طاقم الإدارة
    """
    def test_func(self):
        return self.request.user.is_staff
        
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            # إذا لم يكن المستخدم مسجل الدخول، قم بتحويله إلى صفحة تسجيل الدخول
            return redirect(reverse_lazy('accounts:login'))
        else:
            # إذا كان المستخدم مسجل دخول ولكن ليس لديه صلاحيات، أظهر خطأ 403
            messages.error(self.request, "You don't have permission to access this page.")
            raise PermissionDenied("You do not have permission to access this page.") 