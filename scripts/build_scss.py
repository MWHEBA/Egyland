#!/usr/bin/env python
"""
سكريبت بسيط لتحويل ملفات SCSS إلى CSS
استخدم هذا السكريبت في حالة عدم توفر npm أو sass
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

# المسارات الرئيسية
BASE_DIR = Path(__file__).resolve().parent.parent
SCSS_DIR = BASE_DIR / 'static' / 'scss'
CSS_DIR = BASE_DIR / 'static' / 'css'

def ensure_directory(directory):
    """تأكد من وجود المجلد"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def copy_scss_to_css():
    """نسخ محتوى ملف SCSS إلى CSS مع تطبيق التغييرات الأساسية"""
    ensure_directory(CSS_DIR)
    
    # البحث عن جميع ملفات SCSS
    scss_files = list(SCSS_DIR.glob('*.scss'))
    
    if not scss_files:
        print("لم يتم العثور على ملفات SCSS للتحويل.")
        return
    
    for scss_file in scss_files:
        css_file = CSS_DIR / f"{scss_file.stem}.css"
        
        # محاولة استخدام sass إذا كان متاحاً
        try:
            subprocess.run(['sass', '--style=compressed', '--no-source-map', str(scss_file), str(css_file)], 
                          check=True, stderr=subprocess.PIPE)
            print(f"تم تحويل {scss_file.name} إلى {css_file.name} باستخدام sass")
            continue
        except (subprocess.SubprocessError, FileNotFoundError):
            print("sass غير متاح. سيتم استخدام التحويل الأساسي...")
        
        # التحويل الأساسي (تحويل بسيط للمتغيرات والخلط)
        with open(scss_file, 'r', encoding='utf-8') as f:
            scss_content = f.read()
        
        # استخراج المتغيرات
        variables = {}
        var_matches = re.findall(r'\$([\w-]+):\s*([^;]+);', scss_content)
        for name, value in var_matches:
            variables[f'${name}'] = value.strip()
        
        # استبدال المتغيرات
        css_content = scss_content
        for var_name, var_value in variables.items():
            css_content = css_content.replace(var_name, var_value)
        
        # إزالة الأسطر التي تحتوي على تعريفات المتغيرات
        css_content = re.sub(r'\$([\w-]+):\s*[^;]+;', '', css_content)
        
        # إزالة تعريفات mixins و includes
        css_content = re.sub(r'@mixin\s+[\w-]+\([^)]*\)\s*{[^}]*}', '', css_content)
        css_content = re.sub(r'@include\s+[\w-]+(\([^)]*\))?;', '', css_content)
        
        # تحويل تضمين الميديا
        css_content = re.sub(r'@include\s+for-mobile\s*{([^}]*)}', r'@media (max-width: 768px) {\1}', css_content)
        css_content = re.sub(r'@include\s+for-small-mobile\s*{([^}]*)}', 
                            r'@media (max-width: 768px) and (max-height: 900px) {\1}', css_content)
        
        # كتابة الملف النهائي
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"تم تحويل {scss_file.name} إلى {css_file.name}")

def copy_mobile_home_scss():
    """نسخ ملف mobile_home.scss إلى CSS مباشرة نظراً لبساطته"""
    scss_file = SCSS_DIR / 'mobile_home.scss'
    css_file = CSS_DIR / 'mobile_home.css'
    
    if not scss_file.exists():
        # نسخ من ملف CSS الموجود إذا كان SCSS غير موجود
        mobile_css_file = CSS_DIR / 'mobile_home.css'
        if mobile_css_file.exists():
            shutil.copy(mobile_css_file, scss_file)
            print(f"تم إنشاء {scss_file} من {mobile_css_file}")
        else:
            print(f"لم يتم العثور على {scss_file}")
            return
    
    # نسخ المحتوى مباشرة مع إجراء التعديلات البسيطة
    with open(scss_file, 'r', encoding='utf-8') as f:
        scss_content = f.read()
    
    # التعديلات البسيطة للمتغيرات
    scss_content = scss_content.replace('$primary-color', '#27ae60')
    scss_content = scss_content.replace('$breakpoint-mobile', '768px')
    scss_content = scss_content.replace('$small-screen-height', '900px')
    
    # استبدال mixins
    scss_content = re.sub(r'@include\s+for-mobile\s*{([^}]*)}', r'@media (max-width: 768px) {\1}', scss_content)
    scss_content = re.sub(r'@include\s+for-small-mobile\s*{([^}]*)}', 
                         r'@media (max-width: 768px) and (max-height: 900px) {\1}', scss_content)
    
    # حذف تعريفات المتغيرات و mixins
    scss_content = re.sub(r'// Variables.*?// Mixins', '', scss_content, flags=re.DOTALL)
    scss_content = re.sub(r'// Mixins.*?// Only apply', '// Only apply', scss_content, flags=re.DOTALL)
    
    # كتابة ملف CSS
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(scss_content)
    
    print(f"تم تحويل {scss_file.name} إلى {css_file.name}")

if __name__ == '__main__':
    copy_scss_to_css()
    copy_mobile_home_scss() 