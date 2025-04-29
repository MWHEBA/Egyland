from django import forms
from apps.core.models import *
from apps.products.models import Inquiry, Product
from django_bleach.forms import BleachField


class InquiryForm(forms.ModelForm):
    """
    نموذج الاتصال العام
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


class QuoteRequestForm(InquiryForm):
    """
    نموذج طلب عرض سعر
    """
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-md shadow-sm block w-full'})
    )

    class Meta:
        model = Inquiry
        fields = ['name', 'company', 'email', 'phone', 'country', 'products', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].label = "Additional Information"
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = 'quote'
        if commit:
            instance.save()
            self.save_m2m()
        return instance 