#!/usr/bin/env python
"""
WSGI entry point for Railway deployment
Ensures proper app initialization
"""
import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Create app instance
from app_production import app

# Ensure directories exist
from app_production import create_directories
create_directories()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
