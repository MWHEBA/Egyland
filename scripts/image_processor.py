#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# سكربت معالجة الصور الشامل
يقوم هذا السكربت بكل مهام معالجة الصور في مكان واحد:
1. ضغط الصور مع الحفاظ على الجودة
2. تحويل الصور إلى WebP
3. تحديث الإشارات في ملفات HTML/CSS/JS
4. إضافة دعم عنصر <picture> في HTML
5. تنظيف الصور الزائدة

يمكن استخدامه:
- كأداة CLI
- مع إشارات Django
- كوظيفة دورية (Cron job)
"""

import os
import sys
import re
import shutil
import time
import argparse
from pathlib import Path
from PIL import Image
import logging

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/image_processor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# المجلد الرئيسي للمشروع
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
else:
    BASE_DIR = Path(os.environ.get('DJANGO_BASE_DIR', '.'))

# مجلد الصور
IMG_DIR = BASE_DIR / 'static' / 'img'

# مجلدات الكود التي تحتاج إلى فحص
CODE_DIRS = [
    BASE_DIR / 'templates',
    BASE_DIR / 'static' / 'css',
    BASE_DIR / 'static' / 'scss',
    BASE_DIR / 'static' / 'js',
    BASE_DIR / 'apps',
]

# الإعدادات
JPEG_QUALITY = 85  # جودة الصور بتنسيق JPEG
PNG_COMPRESSION = 9  # درجة ضغط PNG
WEBP_QUALITY = 85  # جودة WebP
MAX_SIZE = 1920  # الحد الأقصى لأبعاد الصورة
VALID_IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
CODE_EXTENSIONS = {'.html', '.css', '.scss', '.js', '.py'}
PROCESSED_MARKER = '.processed'  # علامة للصور المعالجة

def optimize_image(image_path, convert_to_webp=True, keep_original=True):
    """
    ضغط صورة وتحويلها إلى WebP إذا تم تحديد ذلك
    """
    try:
        # التحقق من امتداد الملف
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in VALID_EXTENSIONS:
            return {'success': False, 'error': f'امتداد غير صالح: {file_ext}'}
        
        # حفظ المعلومات الأصلية
        original_size = os.path.getsize(image_path)
        
        # التحقق مما إذا كانت الصورة قد تمت معالجتها بالفعل
        processed_marker = image_path + PROCESSED_MARKER
        if os.path.exists(processed_marker):
            with open(processed_marker, 'r') as f:
                timestamp = f.read().strip()
            file_modified = os.path.getmtime(image_path)
            
            # إذا كانت الصورة لم تتغير منذ آخر معالجة
            if str(file_modified) == timestamp:
                return {'success': True, 'skipped': True, 'message': 'الصورة تمت معالجتها بالفعل'}
        
        # فتح الصورة
        img = Image.open(image_path)
        
        # تحويل إلى RGB إذا كان هناك قناة ألفا (باستثناء PNG)
        if img.mode == 'RGBA' and file_ext != '.png':
            img = img.convert('RGB')
        
        # تغيير حجم الصورة إذا كانت أكبر من الحد الأقصى
        resized = False
        if max(img.size) > MAX_SIZE:
            # الحفاظ على نسبة العرض إلى الارتفاع
            if img.width > img.height:
                new_width = MAX_SIZE
                new_height = int(img.height * MAX_SIZE / img.width)
            else:
                new_height = MAX_SIZE
                new_width = int(img.width * MAX_SIZE / img.height)
            
            img = img.resize((new_width, new_height), Image.LANCZOS)
            resized = True
            logging.info(f"تم تغيير حجم الصورة: {image_path} - الحجم الجديد: {new_width}x{new_height}")
        
        # إنشاء نسخة WebP إذا تم طلب ذلك
        webp_path = None
        if convert_to_webp:
            webp_path = os.path.splitext(image_path)[0] + '.webp'
            
            # حفظ صورة WebP
            if img.mode in ['RGBA', 'LA']:
                img.save(webp_path, 'WEBP', quality=WEBP_QUALITY, lossless=False, method=6)
            else:
                img_rgb = img.convert('RGB')
                img_rgb.save(webp_path, 'WEBP', quality=WEBP_QUALITY, lossless=False, method=6)
            
            # إذا لم نحتفظ بالأصلية، استبدل الصورة الأصلية بصورة WebP
            if not keep_original:
                temp_path = image_path + '.temp'
                shutil.copy2(webp_path, temp_path)
                os.remove(image_path)
                os.rename(temp_path, image_path)
                os.remove(webp_path)
                webp_path = None
        
        # حفظ الصورة المضغوطة بتنسيقها الأصلي
        if file_ext in ['.jpg', '.jpeg']:
            img.save(image_path, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
        elif file_ext == '.png':
            img.save(image_path, 'PNG', optimize=True, compress_level=PNG_COMPRESSION)
        elif file_ext == '.webp':
            img.save(image_path, 'WEBP', quality=JPEG_QUALITY)
        
        # حساب نسبة الضغط
        new_size = os.path.getsize(image_path)
        reduction = (original_size - new_size) / original_size * 100 if original_size > 0 else 0
        
        # إضافة علامة للصورة المعالجة
        with open(processed_marker, 'w') as f:
            f.write(str(os.path.getmtime(image_path)))
        
        result = {
            'success': True,
            'original_size': original_size,
            'new_size': new_size,
            'reduction': reduction,
            'resized': resized,
            'webp_created': webp_path is not None,
            'webp_path': webp_path
        }
        
        logging.info(f"تم معالجة الصورة: {image_path} - الحجم الأصلي: {original_size/1024:.2f}KB - الحجم الجديد: {new_size/1024:.2f}KB - التخفيض: {reduction:.2f}%")
        
        return result
        
    except Exception as e:
        logging.error(f"خطأ في معالجة الصورة {image_path}: {str(e)}")
        return {'success': False, 'error': str(e)}

def process_directory(directory, convert_to_webp=True, keep_original=True, process_all=False):
    """
    معالجة جميع الصور في مجلد
    """
    stats = {
        'processed': 0,
        'skipped': 0,
        'errors': 0,
        'total_saved': 0
    }
    
    # إزالة علامات المعالجة إذا كنا سنعالج جميع الصور
    if process_all:
        remove_processed_markers(directory)
    
    for root, _, files in os.walk(directory):
        for file in files:
            # تجاهل ملفات العلامات
            if file.endswith(PROCESSED_MARKER):
                continue
                
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in VALID_EXTENSIONS:
                result = optimize_image(file_path, convert_to_webp, keep_original)
                
                if result.get('success'):
                    if result.get('skipped'):
                        stats['skipped'] += 1
                    else:
                        stats['processed'] += 1
                        stats['total_saved'] += (result.get('original_size', 0) - result.get('new_size', 0))
                else:
                    stats['errors'] += 1
    
    logging.info(f"تم معالجة {stats['processed']} صورة. تم تخطي {stats['skipped']} صورة. أخطاء: {stats['errors']}. إجمالي المساحة الموفرة: {stats['total_saved']/1024/1024:.2f} ميجابايت")
    
    return stats

def remove_processed_markers(directory):
    """إزالة علامات المعالجة من الصور"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(PROCESSED_MARKER):
                try:
                    os.remove(os.path.join(root, file))
                except Exception as e:
                    logging.error(f"خطأ في إزالة علامة المعالجة: {e}")

def process_single_image(image_path, convert_to_webp=True, keep_original=True):
    """معالجة صورة واحدة"""
    if not os.path.exists(image_path):
        logging.error(f"الملف غير موجود: {image_path}")
        return False
    
    result = optimize_image(image_path, convert_to_webp, keep_original)
    return result.get('success', False)

def find_all_webp_pairs():
    """العثور على جميع أزواج الصور (الأصلية والمقابلة بصيغة WebP)"""
    pairs = []
    
    for root, _, files in os.walk(IMG_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in VALID_IMG_EXTENSIONS:
                webp_path = os.path.splitext(file_path)[0] + '.webp'
                
                if os.path.exists(webp_path):
                    # استخدام المسار النسبي للصور
                    rel_file_path = os.path.relpath(file_path, BASE_DIR)
                    rel_webp_path = os.path.relpath(webp_path, BASE_DIR)
                    
                    pairs.append({
                        'original': file_path,
                        'webp': webp_path,
                        'rel_original': rel_file_path.replace('\\', '/'),
                        'rel_webp': rel_webp_path.replace('\\', '/')
                    })
    
    return pairs

def replace_images(pairs, make_backup=True):
    """استبدال الصور الأصلية بصور WebP"""
    for pair in pairs:
        try:
            # إنشاء نسخة احتياطية إذا كان مطلوبًا
            if make_backup:
                backup_path = pair['original'] + '.backup'
                shutil.copy2(pair['original'], backup_path)
                logging.info(f"تم إنشاء نسخة احتياطية من: {pair['original']}")
            
            # حذف الصورة الأصلية
            os.remove(pair['original'])
            
            # نسخ صورة WebP وإعادة تسمية إلى اسم الصورة الأصلية
            shutil.copy2(pair['webp'], pair['original'])
            
            logging.info(f"تم استبدال: {pair['original']} بصورة WebP")
            
        except Exception as e:
            logging.error(f"خطأ في استبدال الصورة {pair['original']}: {str(e)}")

def find_code_files():
    """العثور على جميع ملفات الكود التي قد تحتوي على إشارات للصور"""
    code_files = []
    
    for directory in CODE_DIRS:
        if not os.path.exists(directory):
            continue
            
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if file_ext in CODE_EXTENSIONS:
                    code_files.append(file_path)
    
    return code_files

def update_code_references(pairs, make_backup=True):
    """تحديث الإشارات إلى الصور في ملفات الكود"""
    code_files = find_code_files()
    modified_files = 0
    
    # إنشاء قاموس للبحث والاستبدال
    replacements = {}
    for pair in pairs:
        # استخراج المسارات النسبية للصور
        original_path = pair['rel_original']
        # لا نقوم بتغيير الاسم، فقط التنسيق
        for ext in VALID_IMG_EXTENSIONS:
            if original_path.lower().endswith(ext):
                # استبدال أي إشارة صريحة إلى امتداد الملف
                webp_search = original_path.replace(ext, '.webp')
                replacements[original_path] = original_path  # نبقى على نفس الاسم في الكود
                replacements[webp_search] = original_path  # نستبدل أي إشارات موجودة إلى ملفات WebP
    
    # تعديل ملفات الكود
    for file_path in code_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            original_content = content
            modified = False
            
            # استبدال جميع الإشارات
            for search, replace in replacements.items():
                if search in content:
                    content = content.replace(search, replace)
                    modified = True
                    logging.info(f"تم تحديث إشارة في {file_path}: {search} -> {replace}")
            
            # حفظ الملف إذا تم تعديله
            if modified:
                # إنشاء نسخة احتياطية إذا كان مطلوبًا
                if make_backup:
                    backup_path = file_path + '.backup'
                    with open(backup_path, 'w', encoding='utf-8') as backup:
                        backup.write(original_content)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                modified_files += 1
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الإشارات في {file_path}: {str(e)}")
    
    logging.info(f"تم تعديل {modified_files} ملف من أصل {len(code_files)} ملف تم فحصه")

def update_html_for_webp_support():
    """تحديث ملفات HTML لاستخدام عنصر <picture> لدعم متصفحات متعددة"""
    html_files = []
    
    # البحث عن ملفات HTML
    for directory in [BASE_DIR / 'templates']:
        if not os.path.exists(directory):
            continue
            
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))
    
    # نمط البحث عن وسوم <img>
    img_pattern = re.compile(r'<img[^>]*src=["\'](\/static\/img\/[^"\']+\.(jpg|jpeg|png))["\'][^>]*>', re.IGNORECASE)
    
    for file_path in html_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            original_content = content
            modified = False
            
            # استبدال عناصر <img> بعناصر <picture>
            def replace_img(match):
                img_tag = match.group(0)
                img_src = match.group(1)
                
                # التحقق مما إذا كانت الصورة لها نسخة WebP
                webp_src = os.path.splitext(img_src)[0] + '.webp'
                webp_path = os.path.join(BASE_DIR, webp_src.lstrip('/'))
                
                if os.path.exists(webp_path):
                    # استخراج سمة alt
                    alt_match = re.search(r'alt=["\'](.*?)["\']', img_tag)
                    alt_text = alt_match.group(1) if alt_match else ""
                    
                    # استخراج سمات أخرى
                    other_attrs = re.sub(r'<img|\s+src=["\'](.*?)["\']|\s+alt=["\'](.*?)["\']', '', img_tag)
                    
                    # إنشاء عنصر <picture>
                    picture_tag = f"""<picture>
    <source srcset="{webp_src}" type="image/webp">
    <img src="{img_src}" alt="{alt_text}"{other_attrs}>
</picture>"""
                    
                    modified = True
                    return picture_tag
                
                return img_tag
            
            content = img_pattern.sub(replace_img, content)
            
            # حفظ الملف إذا تم تعديله
            if content != original_content:
                # إنشاء نسخة احتياطية
                backup_path = file_path + '.backup'
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(original_content)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                logging.info(f"تم تحديث ملف HTML لدعم WebP: {file_path}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث ملف HTML {file_path}: {str(e)}")

def clean_webp_files(directory):
    """مسح ملفات WebP الإضافية"""
    count = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            # مسح ملفات WebP
            if file.lower().endswith('.webp'):
                # تحقق مما إذا كان هناك ملف أصلي له
                original_jpg = os.path.splitext(file_path)[0] + '.jpg'
                original_jpeg = os.path.splitext(file_path)[0] + '.jpeg'
                original_png = os.path.splitext(file_path)[0] + '.png'
                
                if os.path.exists(original_jpg) or os.path.exists(original_jpeg) or os.path.exists(original_png):
                    try:
                        os.remove(file_path)
                        logging.info(f"تم مسح ملف WebP: {file_path}")
                        count += 1
                    except Exception as e:
                        logging.error(f"خطأ في مسح ملف {file_path}: {str(e)}")
    
    logging.info(f"تم مسح {count} ملف WebP")
    return count

def setup_django_signal():
    """إعداد نموذج كود لإشارة Django لمعالجة الصور تلقائياً"""
    code = """
# أضف هذا الكود إلى models.py في التطبيق المسؤول عن الصور

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import YourImageModel  # استبدل بنموذج الصور الخاص بك
from scripts.image_processor import process_single_image

@receiver(post_save, sender=YourImageModel)
def optimize_uploaded_image(sender, instance, created, **kwargs):
    \"\"\"معالجة الصور تلقائياً بعد الرفع\"\"\"
    if instance.image:  # استبدل بحقل الصورة الخاص بك
        image_path = instance.image.path
        process_single_image(image_path, convert_to_webp=True, keep_original=False)
"""
    
    print("\n=== نموذج لإشارة Django ===")
    print(code)
    print("=== انتهى النموذج ===\n")

def setup_cron_job():
    """إعداد وظيفة دورية لمعالجة الصور"""
    cron_command = f"0 3 * * * cd {BASE_DIR} && python scripts/image_processor.py --all >> logs/cron_image_processor.log 2>&1"
    
    print("\n=== نموذج وظيفة دورية (Cron job) ===")
    print("قم بإضافة السطر التالي إلى ملف crontab باستخدام الأمر: crontab -e")
    print(cron_command)
    print("=== انتهى النموذج ===\n")
    print("هذه الوظيفة ستعمل كل يوم الساعة 3 صباحاً وتعالج جميع الصور الجديدة")

def main():
    """الدالة الرئيسية للسكريبت"""
    # إعداد محلل وسيطات سطر الأوامر
    parser = argparse.ArgumentParser(description='معالج الصور الشامل')
    parser.add_argument('--path', help='مسار صورة أو مجلد محدد للمعالجة')
    parser.add_argument('--all', action='store_true', help='معالجة جميع الصور، حتى التي تمت معالجتها من قبل')
    parser.add_argument('--no-webp', action='store_true', help='لا تقم بتحويل الصور إلى WebP')
    parser.add_argument('--replace', action='store_true', help='استبدال الصور الأصلية بصور WebP')
    parser.add_argument('--clean', action='store_true', help='مسح ملفات WebP الإضافية')
    parser.add_argument('--update-html', action='store_true', help='تحديث ملفات HTML لدعم WebP')
    parser.add_argument('--django-signal', action='store_true', help='عرض نموذج إشارة Django')
    parser.add_argument('--cron', action='store_true', help='عرض نموذج وظيفة دورية (Cron job)')
    parser.add_argument('--only-compress', action='store_true', help='ضغط الصور فقط دون تحويل إلى WebP')
    
    args = parser.parse_args()
    
    # التأكد من وجود مجلد السجلات
    logs_dir = BASE_DIR / 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    if args.django_signal:
        setup_django_signal()
        return
    
    if args.cron:
        setup_cron_job()
        return
    
    logging.info("بدء عملية معالجة الصور...")
    
    # تحديد ما إذا كنا سنحتفظ بالصور الأصلية أم لا
    keep_original = not args.replace
    
    # ضغط الصور فقط
    if args.only_compress:
        if args.path:
            path = Path(args.path)
            if path.is_file():
                process_single_image(str(path), False, True)
            elif path.is_dir():
                process_directory(str(path), False, True, args.all)
            else:
                logging.error(f"المسار غير صالح: {args.path}")
        else:
            process_directory(IMG_DIR, False, True, args.all)
        logging.info("اكتملت عملية ضغط الصور")
        return
    
    # مسح ملفات WebP الإضافية إذا طلب المستخدم ذلك
    if args.clean:
        clean_webp_files(IMG_DIR if args.path is None else args.path)
        return
    
    # تحديث ملفات HTML فقط
    if args.update_html:
        update_html_for_webp_support()
        return
    
    # معالجة مسار محدد أو مجلد الصور الافتراضي
    if args.path:
        path = Path(args.path)
        if path.is_file():
            process_single_image(str(path), not args.no_webp, keep_original)
        elif path.is_dir():
            process_directory(str(path), not args.no_webp, keep_original, args.all)
        else:
            logging.error(f"المسار غير صالح: {args.path}")
    else:
        # العملية الكاملة: ضغط وتحويل وتحديث الكود
        process_directory(IMG_DIR, not args.no_webp, keep_original, args.all)
        
        if not args.no_webp:
            # العثور على أزواج الصور وتحديث الكود
            pairs = find_all_webp_pairs()
            logging.info(f"تم العثور على {len(pairs)} زوج من الصور")
            
            if not keep_original:
                replace_images(pairs)
            
            update_code_references(pairs)
            update_html_for_webp_support()
    
    logging.info("اكتملت عملية معالجة الصور")

if __name__ == "__main__":
    main() 