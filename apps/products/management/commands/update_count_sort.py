from django.core.management.base import BaseCommand
from apps.products.models import CountOption

class Command(BaseCommand):
    help = 'تحديث قيم الترتيب الرقمي لخيارات العد'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('بدء تحديث قيم الترتيب الرقمي لخيارات العد...')
        
        # الحصول على جميع خيارات العد
        counts = CountOption.objects.all()
        updated_count = 0
        
        for count in counts:
            # تعيين قيمة الترتيب الرقمي
            old_numeric_sort = count.numeric_sort
            count._set_numeric_sort()  # استدعاء الدالة المسؤولة عن استخراج القيمة الرقمية
            
            # إذا تغيرت القيمة، قم بحفظ السجل
            if old_numeric_sort != count.numeric_sort:
                count.save(update_fields=['numeric_sort'])
                updated_count += 1
                self.stdout.write(f'  تم تحديث "{count.value}" - القيمة الرقمية: {count.numeric_sort}')
        
        self.stdout.write(self.style.SUCCESS(f'تم الانتهاء من تحديث {updated_count} من خيارات العد')) 