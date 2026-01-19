#!/usr/bin/env python3
"""
Railway Deployment Startup Test
Verifies all critical components before deployment
"""
import sys
import os

print("=" * 70)
print("RAILWAY DEPLOYMENT STARTUP TEST")
print("=" * 70)

# Test 1: Python version
print("\n[1/7] Python Version Check...")
print(f"✓ Python {sys.version.split()[0]}")

# Test 2: Required modules
print("\n[2/7] Checking Required Modules...")
required_modules = [
    'flask', 'numpy', 'scipy', 'librosa', 'soundfile', 
    'matplotlib', 'gunicorn', 'werkzeug'
]

missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f"  ✓ {module}")
    except ImportError as e:
        print(f"  ✗ {module} - {e}")
        missing.append(module)

if missing:
    print(f"\n✗ CRITICAL: Missing modules: {missing}")
    sys.exit(1)

# Test 3: Flask app import
print("\n[3/7] Flask App Import...")
try:
    from app_production import app
    print("✓ app_production.py imported successfully")
except Exception as e:
    print(f"✗ Failed to import app_production.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Health endpoint
print("\n[4/7] Testing Health Endpoint...")
try:
    with app.test_client() as client:
        response = client.get('/health')
        if response.status_code == 200:
            print(f"✓ Health endpoint responding: {response.get_json()}")
        else:
            print(f"✗ Health endpoint returned {response.status_code}")
            sys.exit(1)
except Exception as e:
    print(f"✗ Health endpoint test failed: {e}")
    sys.exit(1)

# Test 5: Directories
print("\n[5/7] Checking Directories...")
directories = ['uploads', 'outputs', 'static/spectrograms', 'training_data_generated']
for d in directories:
    if os.path.exists(d):
        print(f"✓ {d}")
    else:
        print(f"✗ {d} (will be created)")

# Test 6: Static files
print("\n[6/7] Checking Static Files...")
templates = ['templates/index.html']
for t in templates:
    if os.path.exists(t):
        print(f"✓ {t}")
    else:
        print(f"⚠ {t} (optional)")

# Test 7: Critical functions
print("\n[7/7] Testing Critical Functions...")
try:
    import numpy as np
    from app_production import align_length, restore_speech_gain
    
    # Test align_length
    ref = np.random.randn(16000)
    target = np.random.randn(16000)
    result = align_length(ref, target)
    print(f"✓ align_length works")
    
    # Test restore_speech_gain
    result = restore_speech_gain(ref, target)
    print(f"✓ restore_speech_gain works")
    
except Exception as e:
    print(f"✗ Function test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL CHECKS PASSED - READY FOR RAILWAY DEPLOYMENT")
print("=" * 70)
print("\nNext steps:")
print("1. Push to GitHub: git add . && git commit -m 'fix: railway deployment' && git push")
print("2. On Railway.app: Trigger new deployment from web dashboard")
print("3. Check logs in Railway dashboard for startup messages")
print("4. Visit: https://your-app.railway.app/health")
print("=" * 70 + "\n")
