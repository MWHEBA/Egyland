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