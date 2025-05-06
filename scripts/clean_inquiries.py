#!/usr/bin/env python
"""
Script to delete all inquiries and product requests from the database
Used when transitioning to production environment to remove test data
"""

import os
import sys
import django
import logging
import argparse

# Add project directory to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('clean_inquiries.log')
    ]
)
logger = logging.getLogger(__name__)

def clean_all_inquiries():
    """
    Clean all inquiries and product requests from the database
    """
    # Import models
    from apps.inquiries.models import Inquiry as InquiryFromInquiries, InquiryNote
    from apps.products.models import Inquiry as InquiryFromProducts, ProductRequest
    
    try:
        # First delete inquiry notes (child relationships)
        inquiries_notes_count = InquiryNote.objects.count()
        InquiryNote.objects.all().delete()
        logger.info(f"Deleted {inquiries_notes_count} inquiry notes from InquiryNote table")
        
        # Delete inquiries from apps.inquiries model
        inquiries_count = InquiryFromInquiries.objects.count()
        InquiryFromInquiries.objects.all().delete()
        logger.info(f"Deleted {inquiries_count} inquiries from Inquiry table in inquiries app")
        
        # Delete inquiries from apps.products model
        products_inquiries_count = InquiryFromProducts.objects.count()
        InquiryFromProducts.objects.all().delete()
        logger.info(f"Deleted {products_inquiries_count} inquiries from Inquiry table in products app")
        
        # Delete product requests
        product_requests_count = ProductRequest.objects.count()
        ProductRequest.objects.all().delete()
        logger.info(f"Deleted {product_requests_count} product requests from ProductRequest table")
        
        total_deleted = inquiries_notes_count + inquiries_count + products_inquiries_count + product_requests_count
        logger.info(f"Total records deleted: {total_deleted}")
        
        return True, total_deleted
        
    except Exception as e:
        logger.error(f"Error during inquiry cleanup: {str(e)}")
        return False, str(e)

def confirm_action():
    """
    Confirm that the user really wants to delete all inquiries
    """
    print("\n" + "="*80)
    print("WARNING: This action will permanently delete all inquiries and product requests from the database.")
    print("This action cannot be undone.")
    print("="*80 + "\n")
    response = input("Are you sure you want to proceed? (type 'yes' to confirm): ")
    return response.lower() in ['yes', 'y']

def main():
    """
    Main function of the script
    """
    parser = argparse.ArgumentParser(description='Delete inquiries from database')
    parser.add_argument('--force', action='store_true', help='Execute cleaning without confirmation')
    
    args = parser.parse_args()
    
    logger.info("=== Starting inquiry cleanup process ===")
    
    # Execute cleaning
    if args.force or confirm_action():
        logger.info("Starting inquiry deletion...")
        success, result = clean_all_inquiries()
        if not success:
            logger.error(f"Cleanup process failed: {result}")
            return False
        logger.info(f"Cleanup process completed successfully: {result} records deleted")
    else:
        logger.info("Cleanup process cancelled by user")
    
    logger.info("=== Inquiry cleanup process completed ===")
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1) 