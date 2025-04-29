from django.db import models

class Branch(models.Model):
    """
    نموذج للفروع (المكاتب) في مختلف الدول
    """
    country_name = models.CharField(max_length=100, verbose_name="Country Name")
    flag_image = models.ImageField(upload_to='flags/', blank=True, null=True, verbose_name="Country Flag")
    address = models.TextField(verbose_name="Address")
    phone = models.CharField(max_length=50, verbose_name="Phone Number")
    email = models.EmailField(verbose_name="Email")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        ordering = ['display_order']
    
    def __str__(self):
        return self.country_name

class MainBranch(models.Model):
    """
    نموذج لتخزين معلومات الفرع الرئيسي (المقر الرئيسي) للشركة
    """
    company_name = models.CharField(max_length=150, verbose_name="Company Name")
    logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name="Company Logo")
    address = models.TextField(verbose_name="Headquarters Address")
    phone = models.CharField(max_length=50, verbose_name="Phone Number")
    fax = models.CharField(max_length=50, blank=True, null=True, verbose_name="Fax Number")
    email = models.EmailField(verbose_name="Email")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    description = models.TextField(blank=True, null=True, verbose_name="Company Description")
    
    # معلومات إضافية (Additional Information)
    tax_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tax Number")
    registration_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Commercial Registration Number")
    
    # وسائل التواصل الاجتماعي (Social Media)
    facebook = models.URLField(blank=True, null=True, verbose_name="Facebook")
    twitter = models.URLField(blank=True, null=True, verbose_name="Twitter")
    instagram = models.URLField(blank=True, null=True, verbose_name="Instagram")
    linkedin = models.URLField(blank=True, null=True, verbose_name="LinkedIn")
    
    # للتأكد من وجود سجل واحد فقط (To ensure only one record exists)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    class Meta:
        verbose_name = "Main Branch"
        verbose_name_plural = "Main Branch"
    
    def __str__(self):
        return self.company_name
    
    def save(self, *args, **kwargs):
        """
        التأكد من وجود سجل واحد فقط للفرع الرئيسي
        """
        if self.pk is None:  # If this is a new record
            # Disable all other records
            MainBranch.objects.all().update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_main_branch(cls):
        """
        الحصول على معلومات الفرع الرئيسي
        """
        main_branch = cls.objects.filter(is_active=True).first()
        if not main_branch:
            main_branch = cls.objects.first()  # If no active record, get the first one
        return main_branch
