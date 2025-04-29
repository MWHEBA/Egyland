from django import forms
from .models import Inquiry
from apps.products.models import Product


class InquiryForm(forms.ModelForm):
    """
    نموذج الاستفسار العام
    """
    name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'})
    )
    company = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'})
    )
    phone = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'})
    )
    country = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'})
    )

    class Meta:
        model = Inquiry
        fields = ['name', 'company', 'email', 'phone', 'country', 'message']

    def save(self, commit=True):
        """
        حفظ النموذج مع تعيين النوع إلى 'contact'
        """
        instance = super().save(commit=False)
        instance.type = 'contact'
        if commit:
            instance.save()
        return instance

    def clean_email(self):
        """
        التحقق من صحة البريد الإلكتروني
        """
        import re
        email = self.cleaned_data['email']
        # استخدام تعبير منتظم بسيط وآمن للتحقق من الإيميل
        email_regex = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        
        if not email_regex.match(email):
            raise forms.ValidationError("Please enter a valid email address")
        
        return email


class ProductInquiryForm(InquiryForm):
    """
    نموذج الاستفسار عن المنتجات
    """
    inquiry_type = forms.ChoiceField(
        choices=[
            ('general', 'General Inquiry'),
            ('product_specific', 'Product Specific Inquiry')
        ],
        widget=forms.RadioSelect(attrs={'class': 'mr-2'}),
        initial='general'
    )
    
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all().order_by('name'),
        widget=forms.SelectMultiple(attrs={'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'}),
        required=False
    )

    class Meta:
        model = Inquiry
        fields = ['name', 'company', 'email', 'phone', 'country', 'inquiry_type', 'products', 'message']

    def clean(self):
        """
        التحقق من وجود منتجات إذا كان نوع الاستفسار خاص بالمنتج
        """
        cleaned_data = super().clean()
        inquiry_type = cleaned_data.get('inquiry_type')
        products = cleaned_data.get('products')
        
        if inquiry_type == 'product_specific' and (not products or len(products) == 0):
            self.add_error('products', 'Please select at least one product for product specific inquiries.')
            
        return cleaned_data

    def save(self, commit=True):
        """
        حفظ النموذج مع تعيين النوع المناسب
        """
        instance = super(InquiryForm, self).save(commit=False)
        
        if self.cleaned_data.get('inquiry_type') == 'product_specific':
            instance.type = 'product_inquiry'
        else:
            instance.type = 'contact'
            
        if commit:
            instance.save()
            # حفظ المنتجات فقط إذا كان الاستفسار خاص بالمنتج
            if instance.type == 'product_inquiry':
                self.save_m2m()
            
        return instance


class ProductRequestForm(ProductInquiryForm):
    """
    نموذج طلب المنتج
    """
    product_quantity = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'}),
        required=False
    )
    
    target_price_range = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'}),
        required=False
    )
    
    preferred_delivery_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'}),
        required=False
    )

    class Meta:
        model = Inquiry
        fields = [
            'name', 'company', 'email', 'phone', 'country', 
            'inquiry_type', 'products', 'product_quantity', 
            'target_price_range', 'preferred_delivery_date', 'message'
        ]

    def save(self, commit=True):
        """
        حفظ النموذج كطلب منتج إذا تم تحديد منتجات
        """
        instance = super(InquiryForm, self).save(commit=False)
        
        if self.cleaned_data.get('inquiry_type') == 'product_specific':
            instance.type = 'product_request'
        else:
            instance.type = 'contact'
            
        if commit:
            instance.save()
            if instance.type == 'product_request':
                self.save_m2m()
                
        return instance 