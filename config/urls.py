"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('products/', include('apps.products.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('inquiries/', include('apps.inquiries.urls')),
    
    # إضافة مسار لخدمة ملفات الوسائط في بيئة الإنتاج
    # ملاحظة: هذه ليست الطريقة المثالية وغير موصى بها للإنتاج
    # يفضل استخدام خادم الويب مباشرة لخدمة الملفات الثابتة والوسائط
    path('media/<path:path>', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# إضافة مسارات الوسائط في حالة التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # إضافة شريط التصحيح
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]

"""
ملاحظة مهمة لبيئة الإنتاج على cPanel:
------------------------------------
لتمكين عرض ملفات الوسائط في بيئة الإنتاج، يجب عليك إعداد خادم الويب (Apache/Nginx) لخدمة الملفات مباشرة.
في cPanel، يمكنك:

1. إنشاء رابط رمزي (symlink) للمجلد 'media' في المجلد العام (public_html) أو
2. إضافة التكوين التالي في ملف .htaccess:

# بداية تكوين الوسائط
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteRule ^media/(.*)$ /home/USERNAME/path/to/your/project/media/$1 [L]
</IfModule>
# نهاية تكوين الوسائط

حيث USERNAME هو اسم المستخدم الخاص بك على cPanel، وpath/to/your/project هو المسار إلى مشروعك.

أو بديلاً لذلك:
3. تفعيل DEBUG=True في بيئة الإنتاج (غير آمن ولا ينصح به) عن طريق إزالة شرط if settings.DEBUG أدناه.
"""
