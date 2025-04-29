from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_bleach.models import BleachField
from django.core.exceptions import ValidationError
from colorfield.fields import ColorField
import uuid

# خيارات نوع المنتج
PRODUCT_TYPE_CHOICES = (
    ('fresh', 'Fresh'),
    ('iqf', 'IQF'),
    ('both', 'Both Fresh & IQF'),
    ('general', 'General'),
)

class Product(models.Model):
    """
    نموذج المنتج الرئيسي
    """
    name = models.CharField(max_length=100, verbose_name="Product Name")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = BleachField(verbose_name="Description", blank=True, null=True)
    fresh_description = BleachField(verbose_name="Fresh Description", blank=True, null=True, help_text="وصف خاص بالمنتج الطازج فقط")
    iqf_description = BleachField(verbose_name="IQF Description", blank=True, null=True, help_text="وصف خاص بالمنتج المجمد فقط")
    
    # صور المنتج
    fresh_image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    iqf_image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    
    # صور الخلفية
    background_left = models.ImageField(upload_to='products/backgrounds/', blank=True, null=True)
    background_right = models.ImageField(upload_to='products/backgrounds/', blank=True, null=True)
    # صورة خلفية كاملة للمنتج المخصوص
    bg_image = models.ImageField(upload_to='products/backgrounds/', blank=True, null=True, verbose_name="Background Image", help_text="صورة خلفية كاملة للمنتج المخصوص")
    
    # صور التغليف (الباكدج)
    fresh_packaging_image = models.ImageField(upload_to='products/packaging/', blank=True, null=True)
    iqf_packaging_image = models.ImageField(upload_to='products/packaging/', blank=True, null=True)
    
    # أيقونة المنتج المستخدمة في جدول الموسمية
    icon = models.ImageField(upload_to='products/icons/', blank=True, null=True)
    iqf_icon = models.ImageField(upload_to='products/icons/', blank=True, null=True)
    
    # أيقونة الموسمية
    seasonality_icon = models.ImageField(upload_to='products/seasonality_icons/', blank=True, null=True, verbose_name="Seasonality Icon")
    
    # صورة قائمة المنتجات (الصورة الخارجية)
    list_image = models.ImageField(upload_to='products/list/', blank=True, null=True)
    
    # لون زر المنتج
    button_color = ColorField(max_length=18, verbose_name="Button Color", help_text="Choose a color for the product button", blank=True, default='#5cbcaa')
    
    # نوع المنتج
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default='both')
    
    # خصائص المنتج
    has_varieties = models.BooleanField(default=False)
    has_counts = models.BooleanField(default=False)
    has_size = models.BooleanField(default=False)
    has_packaging = models.BooleanField(default=True)
    
    # ربط مع الكميات والأحجام والتعبئة المسبقة التعريف
    available_counts = models.ManyToManyField('CountOption', blank=True, related_name='products_with_count')
    available_sizes = models.ManyToManyField('SizeOption', blank=True, related_name='products_with_size')
    available_packaging = models.ManyToManyField('PackagingOption', blank=True, related_name='products_with_packaging')
    
    # خصائص العرض
    is_featured = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_in_slider = models.BooleanField(default=False)
    is_special = models.BooleanField(default=False, verbose_name="Special Product", help_text="حدد هذا الخيار إذا كان المنتج مخصوصًا بتصميم مختلف")
    
    # بيانات تحسين محركات البحث
    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    # تواريخ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # اضافة حقل الترتيب للمنتجات
    order = models.IntegerField(default=0, help_text="Order of the product on the product page (lower numbers appear first)")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Product"
        verbose_name_plural = "Products"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # إنشاء slug تلقائيًا إذا كان فارغًا
        if not self.slug:
            # التأكد من إنشاء slug حتى لو كان الاسم بالعربية
            base_slug = slugify(self.name)
            
            # إذا كان الاسم بالعربية أو slugify أعطى سلسلة فارغة
            if not base_slug:
                # استخدام معرف فريد
                base_slug = str(uuid.uuid4())[:8]
            
            # التحقق من أن الـ slug فريد
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})


class CountOption(models.Model):
    """
    Simple count options - similar to tags
    """
    value = models.CharField(max_length=50, unique=True)
    # حقل لتخزين القيمة الرقمية للترتيب
    numeric_sort = models.IntegerField(null=True, blank=True, help_text="قيمة رقمية للترتيب")
    
    class Meta:
        verbose_name = "Count Option"
        verbose_name_plural = "Count Options"
        ordering = ['numeric_sort', 'value']  # ترتيب حسب الحقل الرقمي أولاً
    
    def __str__(self):
        return self.value
    
    def save(self, *args, **kwargs):
        # أي دائماً يحاول استخراج قيمة رقمية عند الحفظ
        self._set_numeric_sort()
        super().save(*args, **kwargs)
    
    def _set_numeric_sort(self):
        """استخراج القيمة الرقمية من حقل value وتخزينها في numeric_sort"""
        try:
            # نبحث عن أول قيمة رقمية في النص
            import re
            matches = re.findall(r'\d+', self.value)
            if matches:
                # نستخدم أول قيمة رقمية كاملة
                self.numeric_sort = int(matches[0])
            else:
                self.numeric_sort = None
        except:
            self.numeric_sort = None
    
    @property
    def display_value(self):
        """
        عرض القيمة بدون علامة عشرية إذا كانت رقم صحيح
        """
        try:
            # تحقق مما إذا كانت القيمة رقمية
            if self.value.replace('.', '', 1).isdigit():
                # تحويل إلى عدد عشري
                float_value = float(self.value)
                
                # إذا كان رقم صحيح (بدون جزء عشري)
                if float_value.is_integer():
                    return str(int(float_value))  # إرجاع كرقم صحيح
                    
                return self.value  # إرجاع كما هي إذا كانت تحتوي على جزء عشري
        except:
            pass
            
        return self.value  # إرجاع كما هي إذا لم تكن رقمية
    
    @property
    def numeric_value(self):
        """
        الحصول على القيمة العددية للترتيب
        """
        # إرجاع قيمة الترتيب المخزنة إذا كانت موجودة
        if self.numeric_sort is not None:
            return self.numeric_sort
            
        # محاولة استخراج قيمة رقمية إذا لم تكن قيمة الترتيب المخزنة موجودة
        try:
            # تحقق مما إذا كانت القيمة رقمية
            if self.value.replace('.', '', 1).isdigit():
                # إرجاع كقيمة عددية
                return float(self.value)
        except:
            pass
            
        # إرجاع قيمة كبيرة للقيم غير الرقمية
        return float('inf')


class SizeOption(models.Model):
    """
    Simple size options - similar to tags
    """
    value = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Size Option"
        verbose_name_plural = "Size Options"
        ordering = ['value']
    
    def __str__(self):
        return self.value
    
    @property
    def numeric_value(self):
        """
        الحصول على القيمة العددية للترتيب
        """
        try:
            # محاولة استخراج الرقم من القيمة
            import re
            matches = re.findall(r'-?\d+\.?\d*', self.value)
            if matches:
                # إرجاع أول قيمة عددية تم العثور عليها
                return float(matches[0])
        except:
            pass
            
        # إرجاع قيمة كبيرة للقيم غير الرقمية
        return float('inf')


class PackagingOption(models.Model):
    """
    خيارات التعبئة المسبقة التعريف
    """
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES[:2], default='fresh')
    net_weight = models.DecimalField(max_digits=10, decimal_places=2)
    weight_unit = models.CharField(max_length=10, default='kg')
    cartons_per_pallet = models.PositiveIntegerField(default=0)
    pallets_per_container = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/packaging_options/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Packaging Option"
        verbose_name_plural = "Packaging Options"
        ordering = ['name']
        unique_together = ['name', 'type', 'net_weight', 'weight_unit']
    
    def __str__(self):
        return f"{self.name} - {self.net_weight} {self.weight_unit} ({self.get_type_display()})"


class PackagingType(models.Model):
    """
    أنواع التغليف مع الصور والوصف
    """
    name = models.CharField(max_length=100, verbose_name="Packaging Name")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='products/packaging_types/', blank=True, null=True, verbose_name="Packaging Image")
    key_word = models.CharField(max_length=50, verbose_name="Key Word", help_text="المصطلح المميز مثل 'boxes', 'cartons' إلخ")
    is_fresh = models.BooleanField(default=True, verbose_name="For Fresh Products")
    is_iqf = models.BooleanField(default=True, verbose_name="For IQF Products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Packaging Type"
        verbose_name_plural = "Packaging Types"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProductPackagingType(models.Model):
    """
    ربط المنتج بنوع التغليف مع إضافة التفاصيل الخاصة
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_packaging_types')
    packaging_type = models.ForeignKey(PackagingType, on_delete=models.CASCADE, related_name='product_packaging_types')
    type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES[:2], default='fresh', verbose_name="Product Type")
    pallets_per_container = models.PositiveIntegerField(default=0, verbose_name="Pallets per Container")
    items_per_pallet = models.PositiveIntegerField(default=0, verbose_name="Items per Pallet")
    show_fresh_label = models.BooleanField(default=True, verbose_name="Show Fresh Label", help_text="عرض عنوان Fresh فوق مربع التغليف (فقط للمنتجات الطازجة)")
    order = models.PositiveIntegerField(default=0, verbose_name="Display Order", help_text="ترتيب ظهور نوع التغليف في الصفحة (الأرقام الأصغر تظهر أولاً)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Packaging Type"
        verbose_name_plural = "Product Packaging Types"
        ordering = ['type', 'order', 'product', 'packaging_type']
        unique_together = ['product', 'packaging_type', 'type']
    
    def __str__(self):
        return f"{self.product.name} - {self.packaging_type.name} ({self.get_type_display()})"
        
    def clean(self):
        """
        التحقق من صحة البيانات قبل الحفظ
        """
        # التحقق من تحديد المنتج ونوع التغليف
        if not self.product:
            raise ValidationError({'product': 'يجب تحديد المنتج'})
            
        if not self.packaging_type:
            raise ValidationError({'packaging_type': 'يجب تحديد نوع التغليف'})
            
        # التحقق من توافق النوع مع نوع التغليف
        if self.type == 'fresh' and not self.packaging_type.is_fresh:
            raise ValidationError({
                'type': 'هذا النوع من التغليف غير متاح للمنتجات الطازجة'
            })
            
        if self.type == 'iqf' and not self.packaging_type.is_iqf:
            raise ValidationError({
                'type': 'هذا النوع من التغليف غير متاح لمنتجات IQF'
            })
            
        # التحقق من البيانات الرقمية
        if self.items_per_pallet is not None and self.items_per_pallet < 0:
            raise ValidationError({
                'items_per_pallet': 'لا يمكن أن يكون عدد العناصر بالسالب'
            })
            
        if self.pallets_per_container is not None and self.pallets_per_container < 0:
            raise ValidationError({
                'pallets_per_container': 'لا يمكن أن يكون عدد المنصات بالسالب'
            })
        
        # التحقق من عدم وجود تكرار
        try:
            existing = ProductPackagingType.objects.filter(
                product=self.product,
                packaging_type=self.packaging_type,
                type=self.type
            )
            
            # استثناء الكائن الحالي في حالة التعديل
            if self.pk:
                existing = existing.exclude(pk=self.pk)
                
            if existing.exists():
                raise ValidationError(
                    'يوجد بالفعل تسجيل لهذا المنتج مع نفس نوع التغليف ونفس النوع'
                )
        except Exception as e:
            print(f"Error during validation: {str(e)}")
        
    def save(self, *args, **kwargs):
        """
        تنظيف البيانات قبل الحفظ
        """
        self.clean()
        super().save(*args, **kwargs)


class ProductVariety(models.Model):
    """
    أصناف المنتجات المختلفة
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='varieties')
    name = models.CharField(max_length=100)
    description = BleachField(blank=True)
    image = models.ImageField(upload_to='products/varieties/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Product Variety"
        verbose_name_plural = "Product Varieties"
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
        
    def get_seasonality(self, type='fresh'):
        """
        الحصول على بيانات الموسمية الخاصة بهذا الصنف من نوع محدد
        """
        return Seasonality.objects.filter(variety=self, type=type).first()
        
    def get_display_icon(self, type='fresh'):
        """
        الحصول على أيقونة الموسمية المناسبة للعرض بناءً على تسلسل الأولوية
        """
        # الحصول على موسمية الفرايتي
        variety_seasonality = self.get_seasonality(type)
        
        # 1- أيقونة الموسمية للفرايتي
        if variety_seasonality and variety_seasonality.season_icon:
            return variety_seasonality.season_icon
            
        # 2- صورة الفرايتي
        if self.image:
            return self.image
            
        # 3- أيقونة الموسمية للمنتج
        if self.product.seasonality_icon:
            return self.product.seasonality_icon
            
        # 4- أيقونة المنتج العامة
        if type == 'iqf' and self.product.iqf_icon:
            return self.product.iqf_icon
        
        # 5- أيقونة المنتج الافتراضية
        return self.product.icon
    
    # وظائف للتحقق من توفر المنتج في كل شهر
    def is_available_jan_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.jan:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.jan if product_seasonality else False
        
    def is_available_feb_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.feb:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.feb if product_seasonality else False
        
    def is_available_mar_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.mar:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.mar if product_seasonality else False
        
    def is_available_apr_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.apr:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.apr if product_seasonality else False
        
    def is_available_may_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.may:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.may if product_seasonality else False
        
    def is_available_jun_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.jun:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.jun if product_seasonality else False
        
    def is_available_jul_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.jul:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.jul if product_seasonality else False
        
    def is_available_aug_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.aug:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.aug if product_seasonality else False
        
    def is_available_sep_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.sep:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.sep if product_seasonality else False
        
    def is_available_oct_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.oct:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.oct if product_seasonality else False
        
    def is_available_nov_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.nov:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.nov if product_seasonality else False
        
    def is_available_dec_fresh(self):
        variety_seasonality = self.get_seasonality('fresh')
        if variety_seasonality and variety_seasonality.dec:
            return True
        product_seasonality = Seasonality.objects.filter(product=self.product, variety__isnull=True, type='fresh').first()
        return product_seasonality.dec if product_seasonality else False


class Seasonality(models.Model):
    """
    موسمية المنتج أو الصنف
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='seasonality', null=True, blank=True)
    variety = models.ForeignKey(ProductVariety, on_delete=models.CASCADE, related_name='seasonality', null=True, blank=True)
    type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES[:2], default='fresh')
    season_icon = models.ImageField(upload_to='products/seasonality_icons/', blank=True, null=True, verbose_name="Seasonality Icon")
    
    # أشهر التوفر
    jan = models.BooleanField(default=False, verbose_name="January")
    feb = models.BooleanField(default=False, verbose_name="February")
    mar = models.BooleanField(default=False, verbose_name="March")
    apr = models.BooleanField(default=False, verbose_name="April")
    may = models.BooleanField(default=False, verbose_name="May")
    jun = models.BooleanField(default=False, verbose_name="June")
    jul = models.BooleanField(default=False, verbose_name="July")
    aug = models.BooleanField(default=False, verbose_name="August")
    sep = models.BooleanField(default=False, verbose_name="September")
    oct = models.BooleanField(default=False, verbose_name="October")
    nov = models.BooleanField(default=False, verbose_name="November")
    dec = models.BooleanField(default=False, verbose_name="December")
    
    class Meta:
        verbose_name = "Seasonality"
        verbose_name_plural = "Seasonalities"
        constraints = [
            models.CheckConstraint(
                check=models.Q(product__isnull=False) | models.Q(variety__isnull=False),
                name="seasonality_product_or_variety"
            )
        ]
    
    def __str__(self):
        if self.product:
            product_name = getattr(self.product, 'name', 'Unknown')
            return f"{product_name} ({self.type}) Seasonality"
        elif self.variety:
            variety_name = getattr(self.variety, 'name', 'Unknown')
            return f"{variety_name} ({self.type}) Seasonality"
        return f"Unknown ({self.type}) Seasonality"


# الكلاسات التالية يمكن استخدامها للمنتجات القديمة، ولكن من الآن فصاعدًا سنستخدم الخيارات المسبقة التعريف

class ProductSize(models.Model):
    """
    أحجام المنتج
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    value = models.CharField(max_length=50)
    unit = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES[:2], default='fresh')
    
    class Meta:
        verbose_name = "Product Size"
        verbose_name_plural = "Product Sizes"
    
    def __str__(self):
        return f"{self.product.name} - {self.value} {self.unit} ({self.type})"


class ProductPackaging(models.Model):
    """
    معلومات تعبئة المنتج
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='packaging')
    type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES[:2], default='fresh')
    net_weight = models.DecimalField(max_digits=10, decimal_places=2)
    weight_unit = models.CharField(max_length=10, default='kg')
    cartons_per_pallet = models.PositiveIntegerField(default=0)
    pallets_per_container = models.PositiveIntegerField(default=0)
    note = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Product Packaging"
        verbose_name_plural = "Product Packaging"
    
    def __str__(self):
        return f"{self.product.name} - {self.net_weight} {self.weight_unit} ({self.type})"


class Office(models.Model):
    """
    مكاتب الشركة الدولية
    """
    country = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    flag_image = models.ImageField(upload_to='offices/flags/')
    
    class Meta:
        verbose_name = "Office"
        verbose_name_plural = "Offices"
    
    def __str__(self):
        return f"Office in {self.country}"


class Inquiry(models.Model):
    """
    استفسارات واستعلامات العملاء
    """
    INQUIRY_TYPE_CHOICES = (
        ('contact', 'Contact Message'),
        ('quote', 'Quote Request'),
    )
    
    INQUIRY_STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    message = models.TextField()
    
    # نوع الاستفسار
    type = models.CharField(max_length=10, choices=INQUIRY_TYPE_CHOICES, default='contact')
    products = models.ManyToManyField(Product, blank=True, related_name='product_inquiries')
    
    # حالة الاستفسار
    status = models.CharField(max_length=15, choices=INQUIRY_STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inquiry"
        verbose_name_plural = "Inquiries"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_type_display()} ({self.get_status_display()})"


class ProductRequest(models.Model):
    """
    Customer product requests
    """
    REQUEST_STATUS_CHOICES = (
        ('new', 'New'),
        ('reviewing', 'Reviewing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    
    product_name = models.CharField(max_length=100)
    product_description = models.TextField()
    product_quantity = models.CharField(max_length=50)
    requested_specifications = models.TextField(blank=True)
    target_price_range = models.CharField(max_length=100, blank=True)
    preferred_delivery_date = models.DateField(null=True, blank=True)
    
    attachments = models.FileField(upload_to='product_requests/attachments/', blank=True, null=True)
    additional_notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=15, choices=REQUEST_STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, help_text="Internal notes (not visible to customers)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Request"
        verbose_name_plural = "Product Requests"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.product_name}"


class SeasonIcon(models.Model):
    """
    Icons representing seasons for the seasonality table
    """
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='products/season_icons/')
    color_code = models.CharField(max_length=7, help_text="Hex color code", blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        verbose_name = "Season Icon"
        verbose_name_plural = "Season Icons"
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
