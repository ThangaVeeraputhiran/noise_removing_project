#!/usr/bin/env python3
"""
Verification script to check if the project is set up correctly
Run this before starting the main pipeline
"""

import sys
import os

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
        return True
    else:
        print("❌ Python version is too old. Need Python 3.8 or higher")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = {
        'numpy': 'numpy',
        'scipy': 'scipy',
        'matplotlib': 'matplotlib',
        'sklearn': 'scikit-learn',
        'librosa': 'librosa',
        'soundfile': 'soundfile',
        'h5py': 'h5py',
        'tensorflow': 'tensorflow',
        'pydub': 'pydub'
    }
    
    missing = []
    installed = []
    
    for import_name, package_name in required_packages.items():
        try:
            if import_name == 'sklearn':
                import sklearn
                version = sklearn.__version__
            else:
                module = __import__(import_name)
                version = getattr(module, '__version__', 'unknown')
            print(f"✅ {package_name:20s} - version {version}")
            installed.append(package_name)
        except ImportError:
            print(f"❌ {package_name:20s} - NOT INSTALLED")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    else:
        print(f"\n✅ All {len(installed)} required packages are installed!")
        return True

def check_gpu():
    """Check if GPU is available"""
    print_header("Checking GPU Availability")
    
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"✅ Found {len(gpus)} GPU(s):")
            for i, gpu in enumerate(gpus):
                print(f"   GPU {i}: {gpu.name}")
            print("\n🚀 Training will be faster with GPU!")
        else:
            print("⚠️  No GPU found. Training will use CPU (slower)")
            print("   This is OK for learning, but will take longer")
        return True
    except Exception as e:
        print(f"❌ Error checking GPU: {e}")
        return False

def check_directory_structure():
    """Check if directory structure is created"""
    print_header("Checking Directory Structure")
    
    required_dirs = [
        'Dataset/Source/Train/Noise',
        'Dataset/Source/Train/Voice',
        'Dataset/Source/Test/Noise',
        'Dataset/Source/Test/Voice',
        'Training_results/Curve',
        'Training_results/Weights',
        'Predictions'
    ]
    
    missing = []
    existing = []
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
            existing.append(dir_path)
        else:
            print(f"❌ {dir_path} - NOT FOUND")
            missing.append(dir_path)
    
    if missing:
        print(f"\n⚠️  Missing directories. Run: ./setup_directories.sh")
        return False
    else:
        print(f"\n✅ All {len(existing)} required directories exist!")
        return True

def check_dataset():
    """Check if dataset files are present"""
    print_header("Checking Dataset")
    
    # Check for training data
    noise_categories = ['Household_Appliance', 'TVnRadio', 'Vechicles', 'Verbal_Human']
    
    has_noise = False
    has_voice = False
    
    for category in noise_categories:
        noise_path = f'Dataset/Source/Train/Noise/{category}'
        if os.path.exists(noise_path):
            files = [f for f in os.listdir(noise_path) if f.endswith('.wav')]
            if files:
                print(f"✅ Found {len(files)} noise files in {category}")
                has_noise = True
    
    voice_path = 'Dataset/Source/Train/Voice'
    if os.path.exists(voice_path):
        for root, dirs, files in os.walk(voice_path):
            voice_files = [f for f in files if f.endswith('.wav')]
            if voice_files:
                print(f"✅ Found {len(voice_files)} voice files")
                has_voice = True
                break
    
    if not has_noise:
        print("❌ No noise audio files found")
        print("   Place .wav files in Dataset/Source/Train/Noise/<category>/")
    
    if not has_voice:
        print("❌ No voice audio files found")
        print("   Place .wav files in Dataset/Source/Train/Voice/")
    
    if has_noise and has_voice:
        print("\n✅ Dataset files are present!")
        return True
    else:
        print("\n⚠️  Dataset not ready. You need to add audio files.")
        print("   See GETTING_STARTED.md for dataset options")
        return False

def check_config():
    """Check if configuration file is readable"""
    print_header("Checking Configuration")
    
    try:
        import config_params
        print(f"✅ config_params.py is readable")
        print(f"   Noise Class: {config_params.NOISE_CLASS}")
        print(f"   Model Type: {config_params.MODEL}")
        print(f"   Batch Size: {config_params.BATCH_SIZE}")
        print(f"   Epochs: {config_params.EPOCH_NUM}")
        return True
    except Exception as e:
        print(f"❌ Error loading config_params.py: {e}")
        return False

def check_scripts():
    """Check if main scripts are present"""
    print_header("Checking Scripts")
    
    required_scripts = [
        'config_params.py',
        'data_tools.py',
        'prepare_data.py',
        'DDAE.py',
        'train_model.py',
        'prediction_denoise.py',
        'run.py',
        'demo.py'
    ]
    
    missing = []
    existing = []
    
    for script in required_scripts:
        if os.path.exists(script):
            print(f"✅ {script}")
            existing.append(script)
        else:
            print(f"❌ {script} - NOT FOUND")
            missing.append(script)
    
    if missing:
        print(f"\n⚠️  Missing scripts: {', '.join(missing)}")
        return False
    else:
        print(f"\n✅ All {len(existing)} required scripts are present!")
        return True

def main():
    print("\n" + "🔍" * 30)
    print("  SPEECH ENHANCEMENT SYSTEM - VERIFICATION")
    print("🔍" * 30)
    
    results = []
    
    # Run all checks
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("GPU", check_gpu()))
    results.append(("Directory Structure", check_directory_structure()))
    results.append(("Scripts", check_scripts()))
    results.append(("Configuration", check_config()))
    results.append(("Dataset", check_dataset()))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:25s} : {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to go!")
        print("\nNext steps:")
        print("  1. If dataset not prepared: python prepare_data.py")
        print("  2. Train the model: python train_model.py")
        print("  3. Run prediction: python prediction_denoise.py")
        print("\nOr use: python run.py --mode all")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  - Missing dependencies: pip install -r requirements.txt")
        print("  - Missing directories: ./setup_directories.sh")
        print("  - Missing dataset: See GETTING_STARTED.md")
    
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
