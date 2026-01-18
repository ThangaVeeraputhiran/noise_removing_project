#!/usr/bin/env python
"""
WSGI entry point for Railway deployment
Ensures proper app initialization with error handling
"""
import os
import sys
import logging

# Configure logging to stderr (Railway captures this)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

logger.info("=" * 70)
logger.info("WSGI Initialization Started")
logger.info("=" * 70)

try:
    logger.info("Step 1: Importing Flask...")
    from flask import Flask
    logger.info("✓ Flask imported")
    
    logger.info("Step 2: Importing app_production...")
    from app_production import app, create_directories
    logger.info("✓ app_production imported")
    
    logger.info("Step 3: Creating directories...")
    create_directories()
    logger.info("✓ Directories created")
    
    logger.info("=" * 70)
    logger.info("✓ WSGI App Ready")
    logger.info("=" * 70)
    
except Exception as e:
    logger.error("=" * 70)
    logger.error("✗ WSGI Initialization Failed")
    logger.error("=" * 70)
    logger.exception(f"Error: {e}")
    raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting app on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
