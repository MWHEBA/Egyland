from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Profile, Address


class UserRegisterForm(UserCreationForm):
    """
    نموذج لتسجيل المستخدمين الجدد
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label=_('الاسم الأول'))
    last_name = forms.CharField(max_length=30, required=True, label=_('الاسم الأخير'))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('هذا البريد الإلكتروني مستخدم بالفعل'))
        return email


class UserUpdateForm(forms.ModelForm):
    """
    نموذج لتحديث معلومات المستخدم الأساسية
    """
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('هذا البريد الإلكتروني مستخدم بالفعل'))
        return email


class ProfileUpdateForm(forms.ModelForm):
    """
    نموذج لتحديث معلومات الملف الشخصي
    """
    class Meta:
        model = Profile
        fields = ['account_type', 'phone_number', 'address', 'company_name', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class AddressForm(forms.ModelForm):
    """
    نموذج للعناوين
    """
    class Meta:
        model = Address
        fields = ['title', 'location_type', 'street_address', 'city', 'state', 'country', 'postal_code', 'is_default']
        widgets = {
            'street_address': forms.Textarea(attrs={'rows': 2}),
        } 