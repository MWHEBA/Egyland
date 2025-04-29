# Image Processing Scripts

This directory contains Python scripts for image processing and optimization in the project.

## Comprehensive Image Processor (image_processor.py)

This script combines all image processing functions in one place:

### Features:
- Image compression while maintaining quality
- WebP conversion for better performance
- Original image replacement with WebP (optional)
- Code references update in HTML/CSS/JS files
- HTML `<picture>` element support for WebP
- Cleanup of redundant image files

Usage options:
- Command-line interface (CLI)
- Django signals for automatic processing
- Cron job for scheduled processing

### Basic Usage:

```bash
# Complete processing (compression + conversion + code update)
python scripts/image_processor.py

# Process specific image
python scripts/image_processor.py --path static/img/example.jpg

# Process specific directory
python scripts/image_processor.py --path static/img/products/

# Process all images, including previously processed ones
python scripts/image_processor.py --all
```

### Advanced Options:

```bash
# Compress images only without WebP conversion
python scripts/image_processor.py --only-compress

# Process without WebP conversion
python scripts/image_processor.py --no-webp

# Replace original images with WebP versions
python scripts/image_processor.py --replace

# Remove redundant WebP files
python scripts/image_processor.py --clean

# Update HTML files only for WebP support
python scripts/image_processor.py --update-html
```

### Automation Setup:

```bash
# Display Django signal code example
python scripts/image_processor.py --django-signal

# Display cron job setup example
python scripts/image_processor.py --cron
```

### Integration with Django:

1. **Using Django signals**:
   - Use the `--django-signal` parameter to view the code example
   - Add the code to the models.py file in your image-handling app

   ```python
   # Add this code to models.py in your image-handling app
   
   from django.db.models.signals import post_save
   from django.dispatch import receiver
   from .models import YourImageModel  # Replace with your image model
   from scripts.image_processor import process_single_image
   
   @receiver(post_save, sender=YourImageModel)
   def optimize_uploaded_image(sender, instance, created, **kwargs):
       """Automatically process images after upload"""
       if instance.image:  # Replace with your image field
           image_path = instance.image.path
           process_single_image(image_path, convert_to_webp=True, keep_original=False)
   ```

2. **As a cron job**:
   - Use the `--cron` parameter to view the cron job example
   - Add the job to crontab (Linux) or Task Scheduler (Windows)

## Technical Details

### Compression Settings:
- **JPEG_QUALITY**: 85 (JPEG image quality)
- **PNG_COMPRESSION**: 9 (PNG compression level)
- **WEBP_QUALITY**: 85 (WebP quality)
- **MAX_SIZE**: 1920 (Maximum image dimension in pixels)

### Requirements:
- Python 3.6 or newer
- Pillow library (included in requirements.txt)

### Important Notes:
- The script tracks processed images to avoid redundant processing
- Creates backups of files before modification
- When replacing images, maintains original file extensions for code compatibility 