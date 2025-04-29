from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import Profile

class Command(BaseCommand):
    help = 'إنشاء ملفات شخصية للمستخدمين الذين لا يمتلكون ملفًا شخصيًا'

    def handle(self, *args, **options):
        users_without_profile = []
        
        # البحث عن المستخدمين الذين ليس لديهم ملف شخصي
        for user in User.objects.all():
            try:
                # محاولة الوصول إلى الملف الشخصي للتحقق من وجوده
                user.profile
            except Profile.DoesNotExist:
                users_without_profile.append(user)
        
        # إنشاء ملفات شخصية للمستخدمين المفقودين
        for user in users_without_profile:
            Profile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'تم إنشاء ملف شخصي للمستخدم: {user.username}'))
        
        # طباعة إحصائيات
        if users_without_profile:
            self.stdout.write(self.style.SUCCESS(f'تم إنشاء {len(users_without_profile)} ملف شخصي مفقود'))
        else:
            self.stdout.write(self.style.SUCCESS('لا يوجد مستخدمين بدون ملفات شخصية')) 