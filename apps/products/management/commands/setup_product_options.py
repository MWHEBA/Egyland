from django.core.management.base import BaseCommand
from apps.products.models import CountOption, SizeOption, PackagingOption

class Command(BaseCommand):
    help = 'إعداد البيانات الأولية لخيارات المنتجات المسبقة التعريف'

    def handle(self, *args, **options):
        self.stdout.write('جاري إعداد خيارات العد...')
        self._setup_count_options()
        
        self.stdout.write('جاري إعداد خيارات الحجم...')
        self._setup_size_options()
        
        self.stdout.write('جاري إعداد خيارات التغليف...')
        self._setup_packaging_options()
        
        self.stdout.write(self.style.SUCCESS('تم إعداد جميع خيارات المنتجات بنجاح!'))
    
    def _setup_count_options(self):
        # حذف الخيارات الموجودة إذا كان هناك أي منها
        CountOption.objects.all().delete()
        
        # إنشاء خيارات العد للمنتجات الطازجة
        fresh_counts = [
            {'name': 'Small', 'value': '8-14', 'unit': 'pc/kg', 'type': 'fresh'},
            {'name': 'Medium', 'value': '14-18', 'unit': 'pc/kg', 'type': 'fresh'},
            {'name': 'Large', 'value': '18-22', 'unit': 'pc/kg', 'type': 'fresh'},
            {'name': 'Extra Large', 'value': '22-28', 'unit': 'pc/kg', 'type': 'fresh'},
        ]
        
        # إنشاء خيارات العد للمنتجات المجمدة
        iqf_counts = [
            {'name': 'Small IQF', 'value': '10-15', 'unit': 'pc/kg', 'type': 'iqf'},
            {'name': 'Medium IQF', 'value': '15-20', 'unit': 'pc/kg', 'type': 'iqf'},
            {'name': 'Large IQF', 'value': '20-25', 'unit': 'pc/kg', 'type': 'iqf'},
        ]
        
        # إضافة كل الخيارات إلى قاعدة البيانات
        for count_data in fresh_counts + iqf_counts:
            CountOption.objects.create(**count_data)
            self.stdout.write(f"  تم إنشاء خيار العد: {count_data['name']}")
    
    def _setup_size_options(self):
        # حذف الخيارات الموجودة إذا كان هناك أي منها
        SizeOption.objects.all().delete()
        
        # إنشاء خيارات الحجم للمنتجات الطازجة
        fresh_sizes = [
            {'name': 'Small Fresh', 'value': '10-20', 'unit': 'mm', 'type': 'fresh'},
            {'name': 'Medium Fresh', 'value': '20-30', 'unit': 'mm', 'type': 'fresh'},
            {'name': 'Large Fresh', 'value': '30-40', 'unit': 'mm', 'type': 'fresh'},
        ]
        
        # إنشاء خيارات الحجم للمنتجات المجمدة
        iqf_sizes = [
            {'name': 'Small IQF', 'value': '10-20', 'unit': 'mm', 'type': 'iqf'},
            {'name': 'Medium IQF', 'value': '20-30', 'unit': 'mm', 'type': 'iqf'},
            {'name': 'Large IQF', 'value': '30-40', 'unit': 'mm', 'type': 'iqf'},
        ]
        
        # إضافة كل الخيارات إلى قاعدة البيانات
        for size_data in fresh_sizes + iqf_sizes:
            SizeOption.objects.create(**size_data)
            self.stdout.write(f"  تم إنشاء خيار الحجم: {size_data['name']}")
    
    def _setup_packaging_options(self):
        # حذف الخيارات الموجودة إذا كان هناك أي منها
        PackagingOption.objects.all().delete()
        
        # إنشاء خيارات التغليف للمنتجات الطازجة
        fresh_packaging = [
            {
                'name': 'Punnet 250g',
                'type': 'fresh',
                'net_weight': 2.0,
                'weight_unit': 'kg',
                'cartons_per_pallet': 120,
                'pallets_per_container': 20,
                'description': '8 Punnet x 250 Gm = 2.00 kg N.W / CRTN'
            },
            {
                'name': 'Punnet 400g',
                'type': 'fresh',
                'net_weight': 4.8,
                'weight_unit': 'kg',
                'cartons_per_pallet': 80,
                'pallets_per_container': 20,
                'description': '12 Punnet x 400 Gm = 4.80 kg N.W / CRTN'
            },
        ]
        
        # إنشاء خيارات التغليف للمنتجات المجمدة
        iqf_packaging = [
            {
                'name': 'Retail Pack',
                'type': 'iqf',
                'net_weight': 10.0,
                'weight_unit': 'kg',
                'cartons_per_pallet': 80,
                'pallets_per_container': 22,
                'description': '10 x 1 kg'
            },
            {
                'name': 'Bulk Pack',
                'type': 'iqf',
                'net_weight': 10.0,
                'weight_unit': 'kg',
                'cartons_per_pallet': 80,
                'pallets_per_container': 22,
                'description': 'Polyethylene bag inside carton box'
            },
        ]
        
        # إضافة كل الخيارات إلى قاعدة البيانات
        for pkg_data in fresh_packaging + iqf_packaging:
            PackagingOption.objects.create(**pkg_data)
            self.stdout.write(f"  تم إنشاء خيار التغليف: {pkg_data['name']}") 