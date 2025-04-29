from django import forms
from .models import Branch, MainBranch

class BranchForm(forms.ModelForm):
    """
    نموذج إدارة الفروع
    """
    class Meta:
        model = Branch
        fields = ['country_name', 'flag_image', 'address', 'phone', 'email', 'display_order', 'is_active']
        widgets = {
            'country_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter country name'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Enter branch address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Enter email address'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'})
        }

class MainBranchForm(forms.ModelForm):
    """
    نموذج إدارة معلومات الفرع الرئيسي
    تم تعديله ليحتوي فقط على المعلومات الأساسية المطلوبة
    """
    class Meta:
        model = MainBranch
        # تم الاحتفاظ فقط بالحقول المطلوبة: اسم المكتب والشعار والعنوان ورقم الهاتف والبريد الإلكتروني
        fields = [
            'company_name', 'logo', 'address', 'phone', 'email', 'is_active'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter office name'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Enter office address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Enter email address'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'})
        } 