#!/usr/bin/env python3
"""
Fast Training Pipeline for Speech Enhancement System
Simplified and optimized for CPU
"""

import os
import sys
import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
from scipy import signal as scipy_signal
import tensorflow as tf
import warnings

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from datetime import datetime

class FastLogger:
    """Logging utility"""
    @staticmethod
    def log(message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

class FastConfig:
    """Configuration"""
    SAMPLE_RATE = 16000
    DATASET_ROOT = './Dataset_Generated'
    MODEL_PATH = './models_trained'
    N_FFT = 256
    HOP_LENGTH = 128

def create_synthetic_voice(duration=3, sr=16000):
    """Create synthetic voice"""
    t = np.linspace(0, duration, int(sr * duration))
    f0 = np.random.randint(80, 250)
    signal_voice = np.zeros_like(t)
    for harmonic in range(1, 6):
        freq = f0 * harmonic
        amplitude = 1.0 / harmonic
        signal_voice += amplitude * np.sin(2 * np.pi * freq * t)
    modulation = 0.5 * (1 + np.sin(2 * np.pi * 5 * t))
    signal_voice = signal_voice * modulation + 0.05 * np.random.randn(len(signal_voice))
    return (signal_voice / np.max(np.abs(signal_voice))).astype(np.float32)

def create_synthetic_noise(noise_type, duration=3, sr=16000):
    """Create synthetic noise"""
    t = np.linspace(0, duration, int(sr * duration))
    if noise_type == 'Household_Appliance':
        noise = sum(0.2 * np.sin(2 * np.pi * freq * t) for freq in [60, 120, 180, 240])
        noise += 0.3 * np.random.randn(len(t))
    elif noise_type == 'Vechicles':
        noise = sum(0.25 * np.sin(2 * np.pi * freq * t) for freq in [100, 150, 200])
        noise += 0.25 * np.random.randn(len(t))
    elif noise_type == 'TVnRadio':
        noise = sum(0.15 * np.sin(2 * np.pi * freq * t) for freq in [50, 100, 150, 300])
        noise += 0.35 * np.random.randn(len(t))
    else:  # Verbal_Human
        noise = sum(0.15 * np.sin(2 * np.pi * freq * t) for freq in [200, 400, 600, 800])
        noise += 0.3 * np.random.randn(len(t))
    return (noise / np.max(np.abs(noise))).astype(np.float32)

def mix_with_snr(clean, noise, snr_db):
    """Mix audio at specific SNR"""
    min_len = min(len(clean), len(noise))
    clean = clean[:min_len]
    noise = noise[:min_len]
    signal_power = np.mean(clean ** 2)
    noise_power = np.mean(noise ** 2)
    snr_linear = 10 ** (snr_db / 10)
    scaled_noise_power = signal_power / snr_linear
    noise_scale = np.sqrt(scaled_noise_power / (noise_power + 1e-10))
    return (clean + noise_scale * noise).astype(np.float32)

def generate_dataset_fast():
    """Generate dataset quickly"""
    FastLogger.log("Generating synthetic dataset...")
    
    os.makedirs(os.path.join(FastConfig.DATASET_ROOT, 'source', 'Voice'), exist_ok=True)
    for noise_type in ['Household_Appliance', 'Vechicles', 'Verbal_Human', 'TVnRadio']:
        os.makedirs(os.path.join(FastConfig.DATASET_ROOT, 'source', 'Noise', noise_type), exist_ok=True)
    
    # Generate voice samples
    voice_dir = os.path.join(FastConfig.DATASET_ROOT, 'source', 'Voice')
    for i in range(30):
        voice = create_synthetic_voice(duration=np.random.uniform(2, 5))
        sf.write(os.path.join(voice_dir, f'voice_{i:03d}.wav'), voice, FastConfig.SAMPLE_RATE)
    FastLogger.log(f"  ✓ Created 30 voice samples")
    
    # Generate noise samples
    for noise_type in ['Household_Appliance', 'Vechicles', 'Verbal_Human', 'TVnRadio']:
        noise_dir = os.path.join(FastConfig.DATASET_ROOT, 'source', 'Noise', noise_type)
        for i in range(30):
            noise = create_synthetic_noise(noise_type, duration=np.random.uniform(2, 5))
            sf.write(os.path.join(noise_dir, f'{noise_type}_{i:03d}.wav'), noise, FastConfig.SAMPLE_RATE)
        FastLogger.log(f"  ✓ Created 30 {noise_type} noise samples")
    
    FastLogger.log("✓ Dataset generation complete")

def build_noise_classifier():
    """Build noise classifier"""
    FastLogger.log("Building Noise Classifier...")
    
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer((129, 126)),
        tf.keras.layers.Reshape((129, 126, 1)),
        tf.keras.layers.Conv2D(16, (3, 3), padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(32, (3, 3), padding='same', activation='relu'),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(4, activation='softmax')
    ])
    
    FastLogger.log(f"  ✓ Model parameters: {model.count_params():,}")
    return model

def build_ddae():
    """Build DDAE"""
    FastLogger.log("Building DDAE...")
    
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer((129, 126)),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(126)
    ])
    
    FastLogger.log(f"  ✓ Model parameters: {model.count_params():,}")
    return model

def generate_spectrograms(voice_files, noise_files, num_samples=300):
    """Generate spectrograms"""
    FastLogger.log(f"Generating {num_samples} training spectrograms...")
    
    X_clean = []
    X_noisy = []
    y_noise_class = []
    
    noise_types = ['Household_Appliance', 'Vechicles', 'Verbal_Human', 'TVnRadio']
    
    for idx in range(min(num_samples, len(voice_files) * len(noise_files))):
        voice_file = voice_files[idx % len(voice_files)]
        noise_idx = (idx // len(voice_files)) % len(noise_files)
        noise_file = noise_files[noise_idx]
        snr = np.random.choice([5, 10, 15, 20])
        
        try:
            voice, _ = librosa.load(voice_file, sr=FastConfig.SAMPLE_RATE)
            noise, _ = librosa.load(noise_file, sr=FastConfig.SAMPLE_RATE)
            
            min_len = min(len(voice), len(noise), FastConfig.SAMPLE_RATE * 4)
            voice = voice[:min_len]
            noise = noise[:min_len]
            
            noisy = mix_with_snr(voice, noise, snr)
            
            # Create spectrograms
            stft_voice = librosa.stft(voice, n_fft=FastConfig.N_FFT, hop_length=FastConfig.HOP_LENGTH)
            stft_noisy = librosa.stft(noisy, n_fft=FastConfig.N_FFT, hop_length=FastConfig.HOP_LENGTH)
            
            spec_clean = librosa.power_to_db(np.abs(stft_voice) ** 2, ref=np.max)
            spec_noisy = librosa.power_to_db(np.abs(stft_noisy) ** 2, ref=np.max)
            
            X_clean.append(spec_clean.T)
            X_noisy.append(spec_noisy.T)
            
            # Determine noise class
            noise_class = 0
            for i, nt in enumerate(noise_types):
                if nt in noise_file:
                    noise_class = i
                    break
            y_noise_class.append(noise_class)
            
            if (idx + 1) % 50 == 0:
                FastLogger.log(f"  Processed {idx + 1} spectrograms...")
        except:
            continue
    
    FastLogger.log(f"✓ Generated {len(X_clean)} spectrograms")
    return np.array(X_clean), np.array(X_noisy), np.array(y_noise_class)

def train_models_fast():
    """Train models quickly"""
    
    FastLogger.log("="*70)
    FastLogger.log("SPEECH ENHANCEMENT - FAST TRAINING PIPELINE")
    FastLogger.log("="*70)
    
    # Generate dataset
    generate_dataset_fast()
    
    # Load files
    voice_dir = os.path.join(FastConfig.DATASET_ROOT, 'source', 'Voice')
    voice_files = sorted([os.path.join(voice_dir, f) for f in os.listdir(voice_dir)])
    
    noise_files = []
    for noise_type in ['Household_Appliance', 'Vechicles', 'Verbal_Human', 'TVnRadio']:
        noise_dir = os.path.join(FastConfig.DATASET_ROOT, 'source', 'Noise', noise_type)
        noise_files.extend(sorted([os.path.join(noise_dir, f) for f in os.listdir(noise_dir)]))
    
    # Generate spectrograms
    X_clean, X_noisy, y_noise = generate_spectrograms(voice_files, noise_files, num_samples=200)
    
    os.makedirs(FastConfig.MODEL_PATH, exist_ok=True)
    
    # Train Noise Classifier
    FastLogger.log("\nTraining Noise Classifier...")
    nc_model = build_noise_classifier()
    nc_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    
    y_noise_cat = tf.keras.utils.to_categorical(y_noise, 4)
    nc_model.fit(X_noisy, y_noise_cat, epochs=20, batch_size=16, verbose=0)
    nc_path = os.path.join(FastConfig.MODEL_PATH, 'noise_classifier.h5')
    nc_model.save(nc_path)
    FastLogger.log(f"✓ Noise Classifier saved: {nc_path}")
    
    # Train DDAE
    FastLogger.log("\nTraining DDAE...")
    ddae_model = build_ddae()
    ddae_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    ddae_model.fit(X_noisy, X_clean, epochs=20, batch_size=16, verbose=0)
    ddae_path = os.path.join(FastConfig.MODEL_PATH, 'ddae.h5')
    ddae_model.save(ddae_path)
    FastLogger.log(f"✓ DDAE saved: {ddae_path}")
    
    FastLogger.log("\n" + "="*70)
    FastLogger.log("✓✓✓ TRAINING COMPLETE ✓✓✓")
    FastLogger.log("="*70)
    FastLogger.log(f"Models saved to: {FastConfig.MODEL_PATH}")
    
    return True

if __name__ == '__main__':
    train_models_fast()
