#!/usr/bin/env python3
"""
Quick Start Script for Speech Enhancement System
This script provides a simple interface to run the complete pipeline
"""

import os
import sys
import argparse
import config_params

def print_banner():
    print("=" * 70)
    print(" " * 15 + "Speech Enhancement System")
    print(" " * 10 + "Deep Learning Based Noise Reduction")
    print("=" * 70)

def check_dataset():
    """Check if dataset directories exist and have files"""
    noise_dir = config_params.PATH_DIR_NOISE_CLASS
    voice_dir = config_params.PATH_DIR_VOICE_SOURCE
    
    if not os.path.exists(noise_dir):
        print(f"❌ Noise directory not found: {noise_dir}")
        return False
    
    if not os.path.exists(voice_dir):
        print(f"❌ Voice directory not found: {voice_dir}")
        return False
    
    noise_files = [f for f in os.listdir(noise_dir) if f.endswith('.wav')]
    voice_files = []
    for root, dirs, files in os.walk(voice_dir):
        voice_files.extend([f for f in files if f.endswith('.wav')])
    
    if len(noise_files) == 0:
        print(f"❌ No .wav files found in noise directory: {noise_dir}")
        return False
    
    if len(voice_files) == 0:
        print(f"❌ No .wav files found in voice directory: {voice_dir}")
        return False
    
    print(f"✓ Found {len(noise_files)} noise files")
    print(f"✓ Found {len(voice_files)} voice files")
    return True

def prepare_data():
    """Run data preparation script"""
    print("\n" + "=" * 70)
    print("STEP 1: Preparing Dataset")
    print("=" * 70)
    
    if not check_dataset():
        print("\n⚠️  Please add audio files to the dataset directories first!")
        print("   Run ./setup_directories.sh to create the directory structure")
        return False
    
    print("\nRunning data preparation...")
    os.system("python prepare_data.py")
    return True

def train_model():
    """Run model training"""
    print("\n" + "=" * 70)
    print("STEP 2: Training Model")
    print("=" * 70)
    
    # Check if prepared data exists
    if not os.path.exists(config_params.PATH_SPECROGRAM_HDF5_FILE):
        print(f"❌ Prepared dataset not found: {config_params.PATH_SPECROGRAM_HDF5_FILE}")
        print("   Please run data preparation first!")
        return False
    
    print("\nStarting training...")
    os.system("python train_model.py")
    return True

def run_prediction():
    """Run prediction/inference"""
    print("\n" + "=" * 70)
    print("STEP 3: Running Prediction")
    print("=" * 70)
    
    # Check if model exists
    if not os.path.exists(config_params.PATH_WEIGHTS):
        print(f"❌ Model weights not found: {config_params.PATH_WEIGHTS}")
        print("   Please train the model first or download pre-trained weights!")
        return False
    
    print("\nRunning prediction...")
    os.system("python prediction_denoise.py")
    return True

def main():
    parser = argparse.ArgumentParser(description='Speech Enhancement System')
    parser.add_argument('--mode', type=str, default='all', 
                       choices=['all', 'prepare', 'train', 'predict'],
                       help='Mode to run: all, prepare, train, or predict')
    parser.add_argument('--noise-class', type=str, 
                       choices=['Household_Appliance', 'TVnRadio', 'Vechicles', 'Verbal_Human'],
                       help='Noise class to train/predict')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Update noise class if specified
    if args.noise_class:
        print(f"\nNoise Class: {args.noise_class}")
        # Note: This would require updating config_params dynamically
    else:
        print(f"\nNoise Class: {config_params.NOISE_CLASS}")
    
    print(f"Mode: {args.mode}")
    print("")
    
    if args.mode == 'all':
        if prepare_data():
            if train_model():
                run_prediction()
    elif args.mode == 'prepare':
        prepare_data()
    elif args.mode == 'train':
        train_model()
    elif args.mode == 'predict':
        run_prediction()
    
    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)

if __name__ == '__main__':
    main()
