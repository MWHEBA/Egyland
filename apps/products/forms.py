from django import forms
from .models import Product, PRODUCT_TYPE_CHOICES, SizeOption, CountOption
from colorfield.widgets import ColorWidget

class SpecialProductForm(forms.ModelForm):
    """
    نموذج خاص بإنشاء وتعديل المنتج المخصوص
    """
    class Meta:
        model = Product
        fields = [
            'name', 
            'order', 
            'description', 
            'bg_image', 
            'list_image', 
            'button_color'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display Order'}),
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 8, 'class': 'form-input'}),
            'button_color': ColorWidget(),
        }
        labels = {
            'name': 'Product Name',
            'order': 'Display Order',
            'description': 'Description',
            'bg_image': 'Background Image',
            'list_image': 'List Image',
            'button_color': 'Button Color',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # جعل حقل اسم المنتج إجباري
        self.fields['name'].required = True
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        # تعيين المنتج على أنه مخصوص
        instance.is_special = True
        # تعيين نوع المنتج على general بشكل افتراضي
        instance.product_type = 'general'
        
        if commit:
            instance.save()
        
        return instance 

class ProductForm(forms.ModelForm):
    """
    نموذج إنشاء وتعديل المنتج العادي
    """
    # إضافة حقول العلاقات المتعددة للمقاسات والكميات
    available_sizes = forms.ModelMultipleChoiceField(
        queryset=SizeOption.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'hidden'}),
    )
    
    available_counts = forms.ModelMultipleChoiceField(
        queryset=CountOption.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'hidden'}),
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 
            'slug',
            'product_type',
            'order',
            'description', 
            'fresh_description',
            'iqf_description',
            'fresh_image',
            'iqf_image',
            'background_left',
            'background_right',
            'icon',
            'iqf_icon',
            'seasonality_icon',
            'list_image',
            'bg_image',
            'fresh_packaging_image',
            'iqf_packaging_image',
            'button_color',
            'has_varieties',
            'has_counts',
            'has_size',
            'has_packaging',
            'available_sizes',
            'available_counts',
            'is_featured',
            'is_popular',
            'is_in_slider',
            'is_special',
            'meta_title',
            'meta_description',
            'meta_keywords',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Product Name'}),
            'slug': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'product-slug'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'step': 1}),
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 8, 'class': 'form-input'}),
            'fresh_description': forms.Textarea(attrs={'cols': 80, 'rows': 8, 'class': 'form-input'}),
            'iqf_description': forms.Textarea(attrs={'cols': 80, 'rows': 8, 'class': 'form-input'}),
            'button_color': ColorWidget(),
            'meta_title': forms.TextInput(attrs={'class': 'form-input'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # جعل حقل اسم المنتج إجباري
        self.fields['name'].required = True
        # جعل slug اختياري حيث سيتم إنشاؤه تلقائيًا إذا كان فارغًا
        self.fields['slug'].required = False 
        
        # تحديث الاستعلام للمقاسات والكميات
        self.fields['available_sizes'].queryset = SizeOption.objects.all().order_by('value')
        self.fields['available_counts'].queryset = CountOption.objects.all().order_by('value') 