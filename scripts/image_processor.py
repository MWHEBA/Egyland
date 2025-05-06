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
import tempfile
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
IMG_DIRS = [
    BASE_DIR / 'static' / 'img',
    BASE_DIR / 'media',
]

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

# Application lock handling
class ApplicationLock:
    """
    Class to handle application locking to prevent multiple instances running
    """
    def __init__(self, lock_file=None, disabled=False):
        self.disabled = disabled
        if self.disabled:
            logging.info("Application lock disabled")
            return
            
        if lock_file is None:
            # Use temporary directory for lock file to avoid permission issues
            temp_dir = tempfile.gettempdir()
            self.lock_file = os.path.join(temp_dir, 'image_processor.lock')
        else:
            self.lock_file = lock_file
        self.locked = False
        
    def acquire(self):
        """Acquire application lock"""
        if self.disabled:
            return True
            
        if os.path.exists(self.lock_file):
            # Check if the lock is stale (older than 1 hour)
            lock_time = os.path.getmtime(self.lock_file)
            current_time = time.time()
            if current_time - lock_time > 3600:  # 1 hour
                logging.warning(f"Removing stale lock file (age: {(current_time - lock_time) / 60:.1f} minutes)")
                try:
                    os.remove(self.lock_file)
                except:
                    logging.error(f"Failed to remove stale lock file: {self.lock_file}")
                    return False
            else:
                logging.error(f"Another instance is running. Lock file: {self.lock_file}")
                return False
                
        try:
            with open(self.lock_file, 'w') as f:
                f.write(f"{os.getpid()}")
            self.locked = True
            logging.info(f"Acquired application lock: {self.lock_file}")
            return True
        except Exception as e:
            logging.error(f"Failed to create lock file: {str(e)}")
            return False
    
    def release(self):
        """Release application lock"""
        if self.disabled or not self.locked:
            return
            
        if os.path.exists(self.lock_file):
            try:
                os.remove(self.lock_file)
                self.locked = False
                logging.info(f"Released application lock: {self.lock_file}")
            except Exception as e:
                logging.error(f"Failed to remove lock file: {str(e)}")

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
    
    for img_dir in IMG_DIRS:
        if not os.path.exists(img_dir):
            continue
            
        for root, _, files in os.walk(img_dir):
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
    """Update image references in code files"""
    if not pairs:
        logging.info("No image pairs found, skipping code update")
        return 0
    
    code_files = find_code_files()
    modified_count = 0
    
    # Create a lookup table for faster search
    replacement_map = {pair['rel_original']: pair['rel_webp'] for pair in pairs}
    
    # Regular expression patterns to find image references
    img_patterns = [
        re.compile(r'(static\/img\/[^"\']+\.(jpg|jpeg|png))|(/static/img/[^"\']+\.(jpg|jpeg|png))'),
        re.compile(r'(media\/[^"\']+\.(jpg|jpeg|png))|(/media/[^"\']+\.(jpg|jpeg|png))')
    ]
    
    for file_path in code_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            original_content = content
            modified = False
            
            # Replace all image references
            for original, webp in replacement_map.items():
                if original in content:
                    # Keep both versions for HTML picture element later
                    if not file_path.endswith('.html'):
                        content = content.replace(original, webp)
                        modified = True
            
            # Save the file if modified
            if modified:
                # Create backup
                if make_backup:
                    backup_path = file_path + '.backup'
                    with open(backup_path, 'w', encoding='utf-8') as backup:
                        backup.write(original_content)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                modified_count += 1
                logging.info(f"Updated image references in: {file_path}")
        
        except Exception as e:
            logging.error(f"Error updating file {file_path}: {str(e)}")
    
    logging.info(f"Updated {modified_count} files with WebP references")
    return modified_count

def update_html_for_webp_support():
    """Update HTML files to use the picture element for WebP support"""
    html_files = []
    
    for directory in CODE_DIRS:
        if not os.path.exists(directory):
            continue
            
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))
    
    if not html_files:
        logging.info("No HTML files found")
        return 0
    
    modified_count = 0
    # Update regex patterns to match both static/img and media paths
    img_patterns = [
        re.compile(r'<img[^>]*src=["\'](\/static\/img\/[^"\']+\.(jpg|jpeg|png))["\'][^>]*>', re.IGNORECASE),
        re.compile(r'<img[^>]*src=["\'](\/media\/[^"\']+\.(jpg|jpeg|png))["\'][^>]*>', re.IGNORECASE),
        re.compile(r'<img[^>]*src=["\'](static\/img\/[^"\']+\.(jpg|jpeg|png))["\'][^>]*>', re.IGNORECASE),
        re.compile(r'<img[^>]*src=["\'](media\/[^"\']+\.(jpg|jpeg|png))["\'][^>]*>', re.IGNORECASE)
    ]
    
    for file_path in html_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            original_content = content
            modified = False
            
            # Process each regex pattern
            for img_pattern in img_patterns:
                # Replace <img> elements with <picture> elements
                def replace_img(match):
                    img_tag = match.group(0)
                    img_src = match.group(1)
                    
                    # Check if the image has a WebP version
                    webp_src = os.path.splitext(img_src)[0] + '.webp'
                    # Handle both absolute and relative paths
                    if img_src.startswith('/'):
                        webp_path = os.path.join(BASE_DIR, webp_src.lstrip('/'))
                    else:
                        webp_path = os.path.join(BASE_DIR, webp_src)
                    
                    if os.path.exists(webp_path):
                        # Extract alt attribute
                        alt_match = re.search(r'alt=["\'](.*?)["\']', img_tag)
                        alt_text = alt_match.group(1) if alt_match else ""
                        
                        # Extract other attributes
                        other_attrs = re.sub(r'<img|\s+src=["\'](.*?)["\']|\s+alt=["\'](.*?)["\']', '', img_tag)
                        
                        # Create picture element
                        picture_tag = f"""<picture>
    <source srcset="{webp_src}" type="image/webp">
    <img src="{img_src}" alt="{alt_text}"{other_attrs}>
</picture>"""
                        
                        nonlocal modified
                        modified = True
                        return picture_tag
                    
                    return img_tag
                
                content = img_pattern.sub(replace_img, content)
            
            # Save the file if modified
            if content != original_content:
                # Create backup
                backup_path = file_path + '.backup'
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(original_content)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                modified_count += 1
                logging.info(f"Updated HTML file for WebP support: {file_path}")
            
        except Exception as e:
            logging.error(f"Error updating HTML file {file_path}: {str(e)}")
    
    logging.info(f"Updated {modified_count} HTML files for WebP support")
    return modified_count

def clean_webp_files(directories=None):
    """مسح ملفات WebP الإضافية"""
    count = 0
    
    if directories is None:
        directories = IMG_DIRS
    
    if isinstance(directories, str):
        directories = [directories]
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
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

def process_all_image_directories(convert_to_webp=True, keep_original=True, process_all=False):
    """
    Process all configured image directories
    """
    total_stats = {
        'processed': 0,
        'skipped': 0,
        'errors': 0,
        'total_saved': 0
    }
    
    for directory in IMG_DIRS:
        if os.path.exists(directory):
            logging.info(f"Processing directory: {directory}")
            stats = process_directory(directory, convert_to_webp, keep_original, process_all)
            
            total_stats['processed'] += stats['processed']
            total_stats['skipped'] += stats['skipped']
            total_stats['errors'] += stats['errors']
            total_stats['total_saved'] += stats['total_saved']
        else:
            logging.warning(f"Directory not found: {directory}")
    
    logging.info(f"Total: Processed {total_stats['processed']} images. Skipped {total_stats['skipped']}. Errors: {total_stats['errors']}. Total space saved: {total_stats['total_saved']/1024/1024:.2f} MB")
    
    return total_stats

def main():
    """Main function for the script"""
    # Setup command line argument parser
    parser = argparse.ArgumentParser(description='Comprehensive Image Processor')
    parser.add_argument('--path', help='Specific image or directory path to process')
    parser.add_argument('--all', action='store_true', help='Process all images, including previously processed ones')
    parser.add_argument('--no-webp', action='store_true', help='Do not convert images to WebP')
    parser.add_argument('--replace', action='store_true', help='Replace original images with WebP versions')
    parser.add_argument('--clean', action='store_true', help='Clean redundant WebP files')
    parser.add_argument('--update-html', action='store_true', help='Update HTML files for WebP support')
    parser.add_argument('--django-signal', action='store_true', help='Show Django signal model code')
    parser.add_argument('--cron', action='store_true', help='Show cron job example')
    parser.add_argument('--only-compress', action='store_true', help='Only compress images without WebP conversion')
    parser.add_argument('--no-lock', action='store_true', help='Disable application lock (use in cPanel environment)')
    parser.add_argument('--lock-file', help='Custom path for lock file')
    
    args = parser.parse_args()
    
    # Ensure logs directory exists
    logs_dir = BASE_DIR / 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create application lock
    app_lock = ApplicationLock(args.lock_file, disabled=args.no_lock)
    if not app_lock.acquire():
        logging.error("Cannot acquire lock. Exiting.")
        sys.exit(1)
        
    try:
        if args.django_signal:
            setup_django_signal()
            return
        
        if args.cron:
            setup_cron_job()
            return
        
        logging.info("Starting image processing...")
        
        # Determine whether to keep original images
        keep_original = not args.replace
        
        # Compress only
        if args.only_compress:
            if args.path:
                path = Path(args.path)
                if path.is_file():
                    process_single_image(str(path), False, True)
                elif path.is_dir():
                    process_directory(str(path), False, True, args.all)
                else:
                    logging.error(f"Invalid path: {args.path}")
            else:
                process_all_image_directories(False, True, args.all)
            logging.info("Image compression completed")
            return
        
        # Clean WebP files if requested
        if args.clean:
            if args.path:
                clean_webp_files(args.path)
            else:
                clean_webp_files()
            return
        
        # Update HTML files only
        if args.update_html:
            update_html_for_webp_support()
            return
        
        # Process specific path or default image directories
        if args.path:
            path = Path(args.path)
            if path.is_file():
                process_single_image(str(path), not args.no_webp, keep_original)
            elif path.is_dir():
                process_directory(str(path), not args.no_webp, keep_original, args.all)
            else:
                logging.error(f"Invalid path: {args.path}")
        else:
            # Complete process: compress, convert, and update code
            process_all_image_directories(not args.no_webp, keep_original, args.all)
            
            if not args.no_webp:
                # Find image pairs and update code
                pairs = find_all_webp_pairs()
                logging.info(f"Found {len(pairs)} image pairs")
                
                if not keep_original:
                    replace_images(pairs)
                
                update_code_references(pairs)
                update_html_for_webp_support()
        
        logging.info("Image processing completed")
    finally:
        # Release application lock
        app_lock.release()

if __name__ == "__main__":
    main() 