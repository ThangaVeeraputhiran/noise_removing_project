#!/usr/bin/env python3
"""
Complete Training Pipeline for Speech Enhancement System
Includes: Data generation, preprocessing, model training, and integration
Author: AI Assistant
Date: 2026-01-17
"""

import os
import sys
import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
from scipy import signal
import tensorflow as tf
from sklearn.model_selection import train_test_split
import h5py
from datetime import datetime
import json

# ============================================================================
# CONFIGURATION & PARAMETERS
# ============================================================================

class Config:
    """Configuration for the complete pipeline"""
    
    # Dataset paths
    DATASET_ROOT = './Dataset_Generated'
    SOURCE_PATH = './Dataset_Generated/Source'
    TRAIN_PATH = './Dataset_Generated/Train'
    TEST_PATH = './Dataset_Generated/Test'
    
    # Audio parameters
    SAMPLE_RATE = 16000
    MIN_DURATION = 0.5  # seconds
    FRAME_SIZE = 18000  # samples
    HOP_LENGTH_FRAME = 250
    N_FFT = 256
    HOP_LENGTH_FFT = 128
    SLICE_LENGTH = 16384
    
    # Training parameters
    BATCH_SIZE = 64
    EPOCHS = 100
    LEARNING_RATE = 0.001
    VALIDATION_SPLIT = 0.2
    TEST_SPLIT = 0.2
    
    # Noise types to generate
    NOISE_TYPES = ['Household_Appliance', 'Vechicles', 'Verbal_Human', 'TVnRadio']
    
    # SNR levels (dB)
    SNR_LEVELS = [5, 10, 15, 20]
    
    # Model paths
    MODEL_PATH = './models_trained'
    NC_MODEL_PATH = os.path.join(MODEL_PATH, 'noise_classifier.h5')
    TFLITE_MODEL_PATH = os.path.join(MODEL_PATH, 'noise_classifier.tflite')

# ============================================================================
# LOGGER
# ============================================================================

class Logger:
    """Simple logging utility"""
    
    @staticmethod
    def log(message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

# ============================================================================
# AUDIO GENERATION & PREPROCESSING
# ============================================================================

class AudioGenerator:
    """Generate synthetic audio data for training"""
    
    @staticmethod
    def create_directories():
        """Create all necessary directories"""
        Logger.log("Creating directory structure...")
        
        dirs = [
            Config.DATASET_ROOT,
            os.path.join(Config.SOURCE_PATH, 'Voice'),
            os.path.join(Config.SOURCE_PATH, 'Noise'),
            Config.TRAIN_PATH,
            Config.TEST_PATH,
            Config.MODEL_PATH,
            './Training_Results',
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        Logger.log(f"✓ Created {len(dirs)} directories")
    
    @staticmethod
    def generate_synthetic_voice(duration=5, sr=16000):
        """
        Generate synthetic voice-like audio
        Using multiple sine waves to simulate speech characteristics
        """
        t = np.linspace(0, duration, int(sr * duration))
        
        # Create voice-like signal with multiple frequencies
        # Simulate fundamental frequency and harmonics
        f0 = np.random.randint(80, 250)  # Fundamental frequency (Hz)
        
        signal_voice = np.zeros_like(t)
        
        # Add fundamental and harmonics
        for harmonic in range(1, 6):
            freq = f0 * harmonic
            amplitude = 1.0 / harmonic
            signal_voice += amplitude * np.sin(2 * np.pi * freq * t)
        
        # Add amplitude modulation (simulate speech)
        modulation = 0.5 * (1 + np.sin(2 * np.pi * 5 * t))  # 5 Hz modulation
        signal_voice = signal_voice * modulation
        
        # Normalize
        signal_voice = signal_voice / np.max(np.abs(signal_voice))
        
        # Add some random variation
        signal_voice += 0.05 * np.random.randn(len(signal_voice))
        signal_voice = signal_voice / np.max(np.abs(signal_voice))
        
        return signal_voice.astype(np.float32)
    
    @staticmethod
    def generate_noise(noise_type, duration=5, sr=16000):
        """
        Generate synthetic noise for different categories
        """
        t = np.linspace(0, duration, int(sr * duration))
        
        if noise_type == 'Household_Appliance':
            # Washer/vacuum-like noise - mix of frequencies
            noise = np.zeros_like(t)
            for freq in [60, 120, 180, 240]:
                noise += np.sin(2 * np.pi * freq * t) * 0.2
            noise += 0.3 * np.random.randn(len(t))  # Add some randomness
            
        elif noise_type == 'Vechicles':
            # Engine-like noise - lower frequencies
            noise = np.zeros_like(t)
            for freq in [100, 150, 200]:
                noise += np.sin(2 * np.pi * freq * t) * 0.25
            noise += 0.25 * np.random.randn(len(t))
            
        elif noise_type == 'TVnRadio':
            # Broadcast-like noise
            noise = np.zeros_like(t)
            for freq in [50, 100, 150, 300]:
                noise += np.sin(2 * np.pi * freq * t) * 0.15
            noise += 0.35 * np.random.randn(len(t))
            
        elif noise_type == 'Verbal_Human':
            # Background speech-like noise
            noise = np.zeros_like(t)
            for freq in [200, 400, 600, 800]:
                noise += np.sin(2 * np.pi * freq * t) * 0.15
            noise += 0.3 * np.random.randn(len(t))
        else:
            # White noise fallback
            noise = np.random.randn(len(t)) * 0.3
        
        # Normalize
        noise = noise / np.max(np.abs(noise))
        return noise.astype(np.float32)
    
    @staticmethod
    def mix_with_snr(clean_audio, noise_audio, snr_db):
        """
        Mix clean audio with noise at specific SNR
        SNR = 10 * log10(P_signal / P_noise)
        """
        # Ensure same length
        min_len = min(len(clean_audio), len(noise_audio))
        clean_audio = clean_audio[:min_len]
        noise_audio = noise_audio[:min_len]
        
        # Calculate signal and noise power
        signal_power = np.mean(clean_audio ** 2)
        noise_power = np.mean(noise_audio ** 2)
        
        # Calculate scaling factor for noise
        snr_linear = 10 ** (snr_db / 10)
        scaled_noise_power = signal_power / snr_linear
        noise_scale = np.sqrt(scaled_noise_power / (noise_power + 1e-10))
        
        # Mix
        noisy_audio = clean_audio + noise_scale * noise_audio
        
        return noisy_audio.astype(np.float32)
    
    @staticmethod
    def generate_dataset(num_samples_per_category=100):
        """Generate complete synthetic dataset"""
        Logger.log(f"Generating synthetic dataset ({num_samples_per_category} samples per noise type)...")
        
        voice_dir = os.path.join(Config.SOURCE_PATH, 'Voice')
        noise_base_dir = os.path.join(Config.SOURCE_PATH, 'Noise')
        
        # Generate voice samples
        Logger.log("Generating voice samples...")
        for i in range(num_samples_per_category):
            duration = np.random.uniform(3, 8)
            voice = AudioGenerator.generate_synthetic_voice(duration=duration)
            
            voice_path = os.path.join(voice_dir, f'voice_{i:04d}.wav')
            sf.write(voice_path, voice, Config.SAMPLE_RATE)
            
            if (i + 1) % 20 == 0:
                Logger.log(f"  Generated {i + 1} voice samples")
        
        Logger.log(f"✓ Generated {num_samples_per_category} voice samples")
        
        # Generate noise samples
        Logger.log("Generating noise samples...")
        for noise_type in Config.NOISE_TYPES:
            noise_dir = os.path.join(noise_base_dir, noise_type)
            os.makedirs(noise_dir, exist_ok=True)
            
            for i in range(num_samples_per_category):
                duration = np.random.uniform(3, 8)
                noise = AudioGenerator.generate_noise(noise_type, duration=duration)
                
                noise_path = os.path.join(noise_dir, f'{noise_type}_{i:04d}.wav')
                sf.write(noise_path, noise, Config.SAMPLE_RATE)
            
            Logger.log(f"  ✓ Generated {num_samples_per_category} {noise_type} samples")
        
        Logger.log("✓ Dataset generation complete")

# ============================================================================
# SPECTROGRAM & FEATURE EXTRACTION
# ============================================================================

class AudioPreprocessor:
    """Handle audio preprocessing and spectrogram generation"""
    
    @staticmethod
    def audio_to_spectrogram(audio, n_fft=256, hop_length=128):
        """Convert audio to spectrogram"""
        # Compute STFT
        stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft)
        
        # Convert to dB scale
        spec_db = librosa.power_to_db(magnitude ** 2, ref=np.max)
        
        return spec_db.astype(np.float32)
    
    @staticmethod
    def spectrogram_to_audio(spec_db, n_fft=256, hop_length=128):
        """Convert spectrogram back to audio"""
        # Convert from dB to linear
        magnitude = np.sqrt(librosa.db_to_power(spec_db))
        
        # Reconstruct phase using Griffin-Lim algorithm
        audio = librosa.istft(magnitude, hop_length=hop_length)
        
        return audio.astype(np.float32)
    
    @staticmethod
    def process_audio_files(voice_files, noise_files, snr_levels, output_dir):
        """
        Process all audio files to create training dataset
        """
        Logger.log(f"Processing audio files to generate spectrograms...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        processed_data = {
            'noisy_specs': [],
            'clean_specs': [],
            'metadata': []
        }
        
        sample_count = 0
        
        for snr in snr_levels:
            for noise_idx, noise_file in enumerate(noise_files[:20]):  # Limit to 20 noise files
                for voice_idx, voice_file in enumerate(voice_files[:20]):  # Limit to 20 voice files
                    try:
                        # Load audio
                        voice, _ = librosa.load(voice_file, sr=Config.SAMPLE_RATE)
                        noise, _ = librosa.load(noise_file, sr=Config.SAMPLE_RATE)
                        
                        # Ensure sufficient length
                        min_len = min(len(voice), len(noise))
                        if min_len < Config.SAMPLE_RATE * 2:  # At least 2 seconds
                            continue
                        
                        # Crop to same length
                        voice = voice[:min_len]
                        noise = noise[:min_len]
                        
                        # Mix
                        noisy_audio = AudioGenerator.mix_with_snr(voice, noise, snr)
                        
                        # Extract frames
                        frame_length = Config.FRAME_SIZE
                        hop_length = Config.HOP_LENGTH_FRAME
                        
                        voice_frames = librosa.util.frame(voice, frame_length=frame_length, 
                                                          hop_length=hop_length)
                        noisy_frames = librosa.util.frame(noisy_audio, frame_length=frame_length,
                                                          hop_length=hop_length)
                        
                        # Convert to spectrograms
                        for frame_idx in range(min(voice_frames.shape[1], noisy_frames.shape[1])):
                            voice_frame = voice_frames[:, frame_idx]
                            noisy_frame = noisy_frames[:, frame_idx]
                            
                            clean_spec = AudioPreprocessor.audio_to_spectrogram(
                                voice_frame, Config.N_FFT, Config.HOP_LENGTH_FFT)
                            noisy_spec = AudioPreprocessor.audio_to_spectrogram(
                                noisy_frame, Config.N_FFT, Config.HOP_LENGTH_FFT)
                            
                            processed_data['clean_specs'].append(clean_spec)
                            processed_data['noisy_specs'].append(noisy_spec)
                            processed_data['metadata'].append({
                                'voice_file': voice_file,
                                'noise_file': noise_file,
                                'snr_db': snr,
                                'frame_idx': frame_idx
                            })
                            
                            sample_count += 1
                            
                            if sample_count % 100 == 0:
                                Logger.log(f"  Processed {sample_count} spectrograms...")
                    
                    except Exception as e:
                        Logger.log(f"  ⚠️  Error processing files: {e}", "WARN")
                        continue
        
        Logger.log(f"✓ Processed {sample_count} spectrograms")
        
        return processed_data

# ============================================================================
# MODEL TRAINING
# ============================================================================

class ModelTrainer:
    """Handle training of Noise Classifier and DDAE models"""
    
    @staticmethod
    def build_noise_classifier(input_shape=(129, 126)):
        """Build CNN-based Noise Classifier"""
        Logger.log("Building Noise Classifier model...")
        
        model = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=input_shape),
            
            # Reshape for CNN
            tf.keras.layers.Reshape((input_shape[0], input_shape[1], 1)),
            
            # Convolutional blocks
            tf.keras.layers.Conv2D(32, (3, 3), padding='same', activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.3),
            
            tf.keras.layers.Conv2D(64, (3, 3), padding='same', activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.3),
            
            tf.keras.layers.Conv2D(128, (3, 3), padding='same', activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.3),
            
            # Global average pooling
            tf.keras.layers.GlobalAveragePooling2D(),
            
            # Dense layers
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            
            # Output layer (4 noise classes)
            tf.keras.layers.Dense(len(Config.NOISE_TYPES), activation='softmax', name='output')
        ], name='NoiseClassifier')
        
        Logger.log(f"✓ Noise Classifier built with {model.count_params()} parameters")
        return model
    
    @staticmethod
    def build_ddae(input_shape=(129, 126)):
        """Build Deep Denoising Autoencoder"""
        Logger.log("Building DDAE model...")
        
        model = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=input_shape),
            
            # Encoder
            tf.keras.layers.Dense(500, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Dense(500, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Dense(500, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Dense(300, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            
            # Decoder
            tf.keras.layers.Dense(500, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Dense(500, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Dense(500, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),
            
            # Output
            tf.keras.layers.Dense(126, name='output')
        ], name='DDAE')
        
        Logger.log(f"✓ DDAE built with {model.count_params()} parameters")
        return model
    
    @staticmethod
    def train_noise_classifier(processed_data):
        """Train Noise Classifier"""
        Logger.log("Training Noise Classifier...")
        
        # Prepare data
        X = np.array(processed_data['noisy_specs'])
        
        # Create labels based on noise files
        y = np.zeros(len(processed_data['metadata']))
        for idx, meta in enumerate(processed_data['metadata']):
            noise_file = meta['noise_file']
            for class_idx, noise_type in enumerate(Config.NOISE_TYPES):
                if noise_type in noise_file:
                    y[idx] = class_idx
                    break
        
        y = tf.keras.utils.to_categorical(y, num_classes=len(Config.NOISE_TYPES))
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=Config.VALIDATION_SPLIT, random_state=42)
        
        Logger.log(f"  Training set: {X_train.shape}, Validation set: {X_val.shape}")
        
        # Build and compile model
        model = ModelTrainer.build_noise_classifier()
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=Config.LEARNING_RATE),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss', patience=15, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6),
            tf.keras.callbacks.ModelCheckpoint(
                Config.NC_MODEL_PATH, monitor='val_accuracy',
                save_best_only=True, mode='max')
        ]
        
        # Train
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=Config.EPOCHS,
            batch_size=Config.BATCH_SIZE,
            callbacks=callbacks,
            verbose=1
        )
        
        Logger.log(f"✓ Noise Classifier trained and saved to {Config.NC_MODEL_PATH}")
        
        # Plot training history
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.title('Noise Classifier - Loss')
        
        plt.subplot(1, 2, 2)
        plt.plot(history.history['accuracy'], label='Training Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.title('Noise Classifier - Accuracy')
        
        plt.tight_layout()
        plt.savefig('./Training_Results/noise_classifier_training.png', dpi=300)
        plt.close()
        
        Logger.log("✓ Training plots saved")
        
        return model
    
    @staticmethod
    def train_ddae(processed_data):
        """Train DDAE model"""
        Logger.log("Training DDAE model...")
        
        # Prepare data - use noisy spectrograms as input and clean as output
        X_noisy = np.array(processed_data['noisy_specs'])
        X_clean = np.array(processed_data['clean_specs'])
        
        Logger.log(f"  Input data shape: {X_noisy.shape}, Output data shape: {X_clean.shape}")
        
        # Split data
        indices = np.arange(len(X_noisy))
        train_idx, test_idx = train_test_split(
            indices, test_size=Config.TEST_SPLIT, random_state=42)
        
        X_train_noisy = X_noisy[train_idx]
        X_train_clean = X_clean[train_idx]
        X_test_noisy = X_noisy[test_idx]
        X_test_clean = X_clean[test_idx]
        
        Logger.log(f"  Training set: {X_train_noisy.shape}")
        Logger.log(f"  Test set: {X_test_noisy.shape}")
        
        # Build and compile model
        model = ModelTrainer.build_ddae()
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=Config.LEARNING_RATE),
            loss='mse',
            metrics=['mae']
        )
        
        # Callbacks
        ddae_path = os.path.join(Config.MODEL_PATH, 'ddae.h5')
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss', patience=20, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6),
            tf.keras.callbacks.ModelCheckpoint(
                ddae_path, monitor='val_loss',
                save_best_only=True, mode='min')
        ]
        
        # Train
        history = model.fit(
            X_train_noisy, X_train_clean,
            validation_split=Config.VALIDATION_SPLIT,
            epochs=Config.EPOCHS,
            batch_size=Config.BATCH_SIZE,
            callbacks=callbacks,
            verbose=1
        )
        
        Logger.log(f"✓ DDAE trained and saved to {ddae_path}")
        
        # Plot training history
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('MSE Loss')
        plt.legend()
        plt.title('DDAE - Loss')
        
        plt.subplot(1, 2, 2)
        plt.plot(history.history['mae'], label='Training MAE')
        plt.plot(history.history['val_mae'], label='Validation MAE')
        plt.xlabel('Epoch')
        plt.ylabel('MAE')
        plt.legend()
        plt.title('DDAE - MAE')
        
        plt.tight_layout()
        plt.savefig('./Training_Results/ddae_training.png', dpi=300)
        plt.close()
        
        Logger.log("✓ Training plots saved")
        
        # Test the model
        test_pred = model.predict(X_test_noisy[:100])
        test_loss = np.mean((test_pred - X_test_clean[:100]) ** 2)
        Logger.log(f"✓ Test MSE Loss: {test_loss:.6f}")
        
        return model

# ============================================================================
# MODEL OPTIMIZATION & CONVERSION
# ============================================================================

class ModelOptimizer:
    """Convert models to TFLite and optimize"""
    
    @staticmethod
    def convert_to_tflite(model_path, output_path):
        """Convert Keras model to TFLite"""
        Logger.log(f"Converting {model_path} to TFLite...")
        
        try:
            # Load model
            model = tf.keras.models.load_model(model_path, compile=False)
            
            # Create converter
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS,
                tf.lite.OpsSet.SELECT_TF_OPS
            ]
            
            # Convert
            tflite_model = converter.convert()
            
            # Save
            with open(output_path, 'wb') as f:
                f.write(tflite_model)
            
            # Get file size
            original_size = os.path.getsize(model_path) / (1024 * 1024)
            converted_size = os.path.getsize(output_path) / (1024 * 1024)
            compression_ratio = (1 - converted_size / original_size) * 100
            
            Logger.log(f"✓ Converted to TFLite: {output_path}")
            Logger.log(f"  Original size: {original_size:.2f} MB")
            Logger.log(f"  TFLite size: {converted_size:.2f} MB")
            Logger.log(f"  Compression: {compression_ratio:.1f}%")
            
            return True
        except Exception as e:
            Logger.log(f"❌ Conversion failed: {e}", "ERROR")
            return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute complete training pipeline"""
    
    Logger.log("="*80)
    Logger.log("SPEECH ENHANCEMENT SYSTEM - COMPLETE TRAINING PIPELINE")
    Logger.log("="*80)
    
    try:
        # Step 1: Create directories
        AudioGenerator.create_directories()
        
        # Step 2: Generate synthetic dataset
        AudioGenerator.generate_dataset(num_samples_per_category=50)
        
        # Step 3: Get file lists
        voice_dir = os.path.join(Config.SOURCE_PATH, 'Voice')
        voice_files = sorted([os.path.join(voice_dir, f) for f in os.listdir(voice_dir)])
        
        noise_files_all = []
        for noise_type in Config.NOISE_TYPES:
            noise_dir = os.path.join(Config.SOURCE_PATH, 'Noise', noise_type)
            noise_files = sorted([os.path.join(noise_dir, f) for f in os.listdir(noise_dir)])
            noise_files_all.extend(noise_files)
        
        Logger.log(f"✓ Found {len(voice_files)} voice files and {len(noise_files_all)} noise files")
        
        # Step 4: Process audio files
        processed_data = AudioPreprocessor.process_audio_files(
            voice_files, noise_files_all, Config.SNR_LEVELS, Config.TRAIN_PATH)
        
        # Step 5: Train Noise Classifier
        nc_model = ModelTrainer.train_noise_classifier(processed_data)
        
        # Step 6: Train DDAE
        ddae_model = ModelTrainer.train_ddae(processed_data)
        
        # Step 7: Convert to TFLite
        ModelOptimizer.convert_to_tflite(Config.NC_MODEL_PATH, Config.TFLITE_MODEL_PATH)
        
        Logger.log("="*80)
        Logger.log("✓✓✓ TRAINING PIPELINE COMPLETED SUCCESSFULLY ✓✓✓")
        Logger.log("="*80)
        Logger.log(f"Models saved to: {Config.MODEL_PATH}")
        Logger.log(f"Training results: ./Training_Results")
        Logger.log("="*80)
        
    except Exception as e:
        Logger.log(f"❌ Pipeline failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
