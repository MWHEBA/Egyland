from django import forms
from apps.products.models import Product, PRODUCT_TYPE_CHOICES
from colorfield.widgets import ColorWidget

class ProductForm(forms.ModelForm):
    """
    نموذج إنشاء وتعديل المنتج
    """
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
            'button_color': ColorWidget(attrs={'class': 'form-input'}),
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