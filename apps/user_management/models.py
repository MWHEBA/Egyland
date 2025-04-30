from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    """
    نموذج للأدوار والصلاحيات
    """
    # خيارات الأدوار الثابتة
    DEVELOPER = 'developer'
    ADMIN = 'admin'
    EDITOR = 'editor'
    
    ROLE_CHOICES = [
        (DEVELOPER, 'Developer'),
        (ADMIN, 'Admin'),
        (EDITOR, 'Editor'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    can_manage_users = models.BooleanField(default=False)
    can_manage_roles = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # تعيين الصلاحيات بناءً على نوع الدور
        if self.name == self.DEVELOPER:
            self.can_manage_users = True
            self.can_manage_roles = True
        elif self.name == self.ADMIN:
            self.can_manage_users = True
            self.can_manage_roles = False
        elif self.name == self.EDITOR:
            self.can_manage_users = False
            self.can_manage_roles = False
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.get_name_display()


class UserRole(models.Model):
    """
    نموذج لربط المستخدمين بالأدوار
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_roles')
    
    class Meta:
        unique_together = ('user', 'role')
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
