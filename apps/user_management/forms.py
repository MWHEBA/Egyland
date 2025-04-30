from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Role


class AdminUserCreationForm(UserCreationForm):
    """
    Form for admin to create new users
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    is_staff = forms.BooleanField(required=False, initial=False, 
                                 help_text=_("Designates whether the user can log into this admin site."))
    is_active = forms.BooleanField(required=False, initial=True,
                                  help_text=_("Designates whether this user should be treated as active."))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = self.cleaned_data['is_staff']
        user.is_active = self.cleaned_data['is_active']
        
        if commit:
            user.save()
        
        return user


class AdminUserEditForm(forms.ModelForm):
    """
    Form for admin to edit existing users
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    is_staff = forms.BooleanField(required=False, 
                                 help_text=_("Designates whether the user can log into this admin site."))
    is_active = forms.BooleanField(required=False,
                                  help_text=_("Designates whether this user should be treated as active."))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')


class AdminPasswordChangeForm(forms.Form):
    """
    Form for admin to change user's password
    """
    password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirm new password"), widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("The two password fields didn't match."))
        
        return cleaned_data


class UserRoleForm(forms.Form):
    """
    Form for assigning roles to a user
    """
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    ) 