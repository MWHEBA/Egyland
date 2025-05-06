#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# Django Lock File Remover
This script finds and removes all lingering lock files that cause issues
with Django commands like collectstatic and image processing scripts.

Can be run directly or imported as a module.
"""

import os
import sys
import tempfile
import glob
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

def clear_locks(force=False):
    """
    Find and remove lock files in the project
    
    Args:
        force: Remove all locks without confirmation
    
    Returns:
        int: Number of files removed
    """
    # Common lock file patterns
    lock_patterns = [
        # Temp directory
        os.path.join(tempfile.gettempdir(), "*.lock"),
        os.path.join(tempfile.gettempdir(), "image_processor.lock"),
        os.path.join(tempfile.gettempdir(), "django_*.lock"),
        
        # Project directory
        str(BASE_DIR / "*.lock"),
        str(BASE_DIR / ".*.lock"),
        str(BASE_DIR / "scripts" / "*.lock"),
        
        # Specific Django lock files
        str(BASE_DIR / "static" / "*.lock"),
        str(BASE_DIR / "media" / "*.lock"),
        str(BASE_DIR / ".static.lock"),
        
        # cPanel lock files
        "/tmp/*.lock",
        "/home/*/tmp/*.lock",
    ]
    
    # Find all lock files
    lock_files = []
    for pattern in lock_patterns:
        try:
            lock_files.extend(glob.glob(pattern))
        except Exception:
            # Ignore errors if no permission for directory
            pass
    
    # Add specific files that may not match patterns
    specific_locks = [
        os.path.join(tempfile.gettempdir(), "image_processor.lock"),
        str(BASE_DIR / ".static.lock"),
        "/tmp/image_processor.lock",
    ]
    
    for lock in specific_locks:
        if os.path.exists(lock) and lock not in lock_files:
            lock_files.append(lock)
    
    # Exit if no lock files found
    if not lock_files:
        logging.info("No lock files found.")
        return 0
    
    # Display files and confirm removal
    logging.info(f"Found {len(lock_files)} lock files:")
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            logging.info(f"- {lock_file}")
    
    if not force:
        confirm = input("Do you want to remove these lock files? [y/N]: ")
        if confirm.lower() not in ("y", "yes"):
            logging.info("Operation cancelled.")
            return 0
    
    # Remove lock files
    removed = 0
    for lock_file in lock_files:
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                removed += 1
                logging.info(f"Removed: {lock_file}")
        except Exception as e:
            logging.error(f"Error removing {lock_file}: {str(e)}")
    
    logging.info(f"Removed {removed} lock files.")
    return removed

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    logs_dir = BASE_DIR / "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Remove lock files
    clear_locks(force=len(sys.argv) > 1 and sys.argv[1] == "--force")
