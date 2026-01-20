#!/usr/bin/env python3
"""
WSGI Entry Point with Pre-Import Numba Configuration
This file MUST be imported first to set environment variables before any other imports
"""

import os
import sys

# CRITICAL: Set environment variables BEFORE any imports
# This must happen at the very first moment Python starts
os.environ['NUMBA_DISABLE_JIT'] = '1'
os.environ['NUMBA_CACHE_DIR'] = '/tmp/numba_cache'
os.environ['NUMBA_WARNINGS'] = '0'
os.environ['PYTHONWARNINGS'] = 'ignore'

print("=" * 80)
print("🔧 NUMBA CONFIGURATION (Pre-Import)")
print("=" * 80)
print(f"NUMBA_DISABLE_JIT:  {os.environ.get('NUMBA_DISABLE_JIT')}")
print(f"NUMBA_CACHE_DIR:    {os.environ.get('NUMBA_CACHE_DIR')}")
print(f"NUMBA_WARNINGS:     {os.environ.get('NUMBA_WARNINGS')}")
print("=" * 80)
print("")

# Now import the application
from app_production import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=False, host='0.0.0.0', port=port)
