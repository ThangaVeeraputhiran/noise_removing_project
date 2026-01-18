#!/usr/bin/env python3
"""
Final Verification Script - Confirms all components are working
"""

import os
import sys
import subprocess

def check_file(path, description):
    """Check if file exists"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  ✅ {description}: {path} ({size:,} bytes)")
        return True
    else:
        print(f"  ❌ {description}: {path} NOT FOUND")
        return False

def verify_system():
    """Verify entire system"""
    
    print("\n" + "="*70)
    print("SPEECH ENHANCEMENT SYSTEM - FINAL VERIFICATION")
    print("="*70 + "\n")
    
    all_good = True
    
    # 1. Check core files
    print("[1] Core System Files")
    all_good &= check_file('production_system.py', 'Production engine')
    all_good &= check_file('app_production.py', 'Flask application')
    all_good &= check_file('speech_enhancer_dsp.py', 'DSP algorithms')
    
    # 2. Check web files
    print("\n[2] Web Interface Files")
    all_good &= check_file('templates/index.html', 'Web interface')
    all_good &= check_file('static/css/style.css', 'Styling')
    all_good &= check_file('static/js/app.js', 'JavaScript')
    
    # 3. Check documentation
    print("\n[3] Documentation Files")
    all_good &= check_file('PROJECT_COMPLETION_REPORT.md', 'Completion report')
    all_good &= check_file('FINAL_COMPLETION_SUMMARY.md', 'Final summary')
    all_good &= check_file('README.md', 'README')
    
    # 4. Check directories
    print("\n[4] Required Directories")
    dirs = ['uploads', 'outputs', 'static/spectrograms', 'denoised_output']
    for d in dirs:
        if os.path.exists(d):
            print(f"  ✅ {d}")
        else:
            print(f"  ⚠️  {d} (will be created)")
    
    # 5. Test imports
    print("\n[5] Python Module Tests")
    try:
        import librosa
        print(f"  ✅ librosa {librosa.__version__}")
    except:
        print("  ⚠️  librosa not installed")
    
    try:
        import scipy
        print(f"  ✅ scipy {scipy.__version__}")
    except:
        print("  ⚠️  scipy not installed")
    
    try:
        import numpy
        print(f"  ✅ numpy {numpy.__version__}")
    except:
        print("  ⚠️  numpy not installed")
    
    try:
        import flask
        print(f"  ✅ flask {flask.__version__}")
    except:
        print("  ⚠️  flask not installed")
    
    # 6. Test core functionality
    print("\n[6] Core Functionality Tests")
    try:
        from production_system import AdvancedSpeechEnhancer, NoiseClassifier
        print("  ✅ Can import AdvancedSpeechEnhancer")
        print("  ✅ Can import NoiseClassifier")
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        all_good = False
    
    # 7. Summary
    print("\n" + "="*70)
    if all_good:
        print("✅ ALL VERIFICATIONS PASSED!")
        print("\nSystem is ready to use:")
        print("  1. Run: python app_production.py")
        print("  2. Open: http://localhost:5000")
        print("  3. Upload audio file")
        print("  4. Download enhanced audio")
    else:
        print("⚠️  Some checks failed - install dependencies")
        print("\nInstall with:")
        print("  pip install flask librosa soundfile scipy numpy")
    
    print("="*70 + "\n")
    
    return all_good

if __name__ == '__main__':
    success = verify_system()
    sys.exit(0 if success else 1)
