# Inquiry Cleanup Script

This directory contains a utility script for cleaning up inquiries and product requests from the database, especially when preparing for production.

## clean_inquiries.py

This script is designed to delete all inquiries and product requests from the database. It's useful when transitioning to a production environment to remove test data.

### Basic Usage

```bash
# Run the script with confirmation prompt
python scripts/clean_inquiries.py
```

### Advanced Options

```bash
# Execute cleaning without confirmation prompt
python scripts/clean_inquiries.py --force
```

### Running on Windows

When running the script on Windows, use:

```
python scripts\clean_inquiries.py
```

On Linux/Mac systems, you can make the file executable:

```
chmod +x scripts/clean_inquiries.py
./scripts/clean_inquiries.py
```

## Important Notes

1. **Warning:** The cleaning operation cannot be undone. Consider making a manual database backup before running this script.

2. **Use Proper Environment:** Make sure to run this script in the appropriate environment (development, testing, production).

3. **Log File:** The script creates a log file in the current directory named `clean_inquiries.log` with operation details.

## What Gets Deleted

The script will delete the following data:

1. All inquiry notes from `apps.inquiries.models.InquiryNote`
2. All inquiries from `apps.inquiries.models.Inquiry`
3. All inquiries from `apps.products.models.Inquiry`
4. All product requests from `apps.products.models.ProductRequest`

# Image Processor Script

## Overview

The `image_processor.py` script provides comprehensive image processing capabilities:

1. **Compresses images** while maintaining visual quality
2. **Converts images to WebP format** for better performance
3. **Updates references** in HTML/CSS/JS files
4. **Adds `<picture>` element support** in HTML for cross-browser compatibility
5. **Cleans up excess image files** when needed

## Default Directories

The script processes images in the following directories by default:
- `static/img/` - Static image assets
- `media/` - User-uploaded images

## Usage

### Basic Usage

Process all images in the default directories:

```bash
python scripts/image_processor.py
```

### Process a Specific Directory or File

```bash
python scripts/image_processor.py --path media/products/
python scripts/image_processor.py --path static/img/logo.png
```

### Compression Only (No WebP Conversion)

```bash
python scripts/image_processor.py --only-compress
```

### Process All Images, Including Already Processed

```bash
python scripts/image_processor.py --all
```

### Update HTML For WebP Support

Updates HTML files to use the `<picture>` element with WebP:

```bash
python scripts/image_processor.py --update-html
```

### Clean WebP Files

Removes WebP versions of images:

```bash
python scripts/image_processor.py --clean
```

### cPanel Environment

When running in cPanel or environments with file permission issues, use the `--no-lock` option:

```bash
python scripts/image_processor.py --no-lock
```

This disables the application lock mechanism, allowing the script to run even if lock files can't be created or removed properly.

You can also specify a custom lock file location:

```bash
python scripts/image_processor.py --lock-file /tmp/custom_image_processor.lock
```

## Django Integration

You can use this script with Django signals to automatically process images when they're uploaded. Add the following code to your models.py file:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from scripts.image_processor import process_single_image

@receiver(post_save, sender=YourImageModel)
def optimize_uploaded_image(sender, instance, created, **kwargs):
    if instance.image:
        image_path = instance.image.path
        process_single_image(image_path)
```

## Cron Job Setup

To run this script daily, add the following to your crontab:

```
0 3 * * * cd /path/to/project && python scripts/image_processor.py --all >> logs/cron_image_processor.log 2>&1
```

For cPanel environments, you may want to add the `--no-lock` option:

```
0 3 * * * cd /path/to/project && python scripts/image_processor.py --all --no-lock >> logs/cron_image_processor.log 2>&1
```

## Options

```
  --path PATH           Specific image or directory path to process
  --all                 Process all images, including previously processed ones
  --no-webp             Do not convert images to WebP
  --replace             Replace original images with WebP versions
  --clean               Clean redundant WebP files
  --update-html         Update HTML files for WebP support
  --django-signal       Show Django signal model code
  --cron                Show cron job example
  --only-compress       Only compress images without WebP conversion
  --no-lock             Disable application lock (use in cPanel environment)
  --lock-file PATH      Custom path for lock file
```

## Technical Details

- JPEG Quality: 85%
- PNG Compression: Level 9
- WebP Quality: 85%
- Max Dimensions: 1920px (preserves aspect ratio)
- Supported formats: JPEG, PNG
- Output formats: Original format (compressed) + WebP 

# Lock Files Remover Script

## Overview

The `clear_locks.py` script finds and removes lock files that can cause issues with Django commands and image processing tasks.

## Purpose

Lock files can sometimes remain in the system if a process is interrupted abruptly, preventing subsequent processes from running correctly. This script helps identify and remove these lock files, particularly useful in:

1. Shared hosting environments like cPanel
2. After image processing script crashes
3. When Django `collectstatic` commands fail with lock errors
4. When multiple processes try to access the same resources

## Usage

### Basic Usage (With Confirmation)

```bash
python scripts/clear_locks.py
```

This scans for lock files and asks for confirmation before deleting them.

### Remove Lock Files Without Confirmation

```bash
python scripts/clear_locks.py --force
```

### When to Use This Script

Run this script when you encounter these common errors:

1. "Another process is already running" errors
2. "Lock file exists" errors with image processing
3. Django commands hanging indefinitely
4. File permission errors in shared hosting

## Integration with Deployment

You can add this script to your deployment process to ensure no stale lock files exist:

```bash
# Example deployment script
python scripts/clear_locks.py --force
python manage.py collectstatic --noinput
python manage.py migrate
```

## Where Lock Files Are Checked

The script checks for lock files in:

1. System temporary directories
2. Project directory
3. Static and media directories
4. cPanel temporary directories (for shared hosting) 