# Generated by Django 4.2.7 on 2025-04-19 13:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.CharField(choices=[('buyer', 'مشتري'), ('seller', 'بائع'), ('both', 'مشتري وبائع')], default='buyer', max_length=10, verbose_name='نوع الحساب')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='رقم الهاتف')),
                ('address', models.TextField(blank=True, null=True, verbose_name='العنوان')),
                ('company_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='اسم الشركة')),
                ('bio', models.TextField(blank=True, null=True, verbose_name='نبذة مختصرة')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/', verbose_name='الصورة الشخصية')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ملف شخصي',
                'verbose_name_plural': 'الملفات الشخصية',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='العنوان المختصر')),
                ('location_type', models.CharField(choices=[('home', 'المنزل'), ('work', 'العمل'), ('other', 'آخر')], default='home', max_length=10, verbose_name='نوع المكان')),
                ('street_address', models.CharField(max_length=255, verbose_name='عنوان الشارع')),
                ('city', models.CharField(max_length=100, verbose_name='المدينة')),
                ('state', models.CharField(max_length=100, verbose_name='المحافظة')),
                ('country', models.CharField(default='مصر', max_length=100, verbose_name='الدولة')),
                ('postal_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='الرمز البريدي')),
                ('is_default', models.BooleanField(default=False, verbose_name='العنوان الافتراضي')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'عنوان',
                'verbose_name_plural': 'العناوين',
            },
        ),
    ]
