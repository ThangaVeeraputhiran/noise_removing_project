#!/usr/bin/env python3
"""
Advanced Training Data Generator
Creates realistic training datasets with various noise types and SNR levels
Designed for learning robust speech enhancement
"""

import numpy as np
import librosa
import soundfile as sf
import os
from pathlib import Path
import json
from datetime import datetime

class TrainingDataGenerator:
    """Generate realistic noisy-clean speech pairs for training"""
    
    # Common noise types
    NOISE_TYPES = {
        'white': lambda sr, dur: np.random.randn(int(sr * dur)),
        'pink': lambda sr, dur: _pink_noise(sr * dur),
        'brown': lambda sr, dur: _brown_noise(sr * dur),
        'speech': lambda sr, dur: _synthetic_speech(sr, dur, noise=True),
        'traffic': lambda sr, dur: _traffic_noise(sr, dur),
        'babble': lambda sr, dur: _babble_noise(sr, dur),
        'office': lambda sr, dur: _office_noise(sr, dur),
        'wind': lambda sr, dur: _wind_noise(sr, dur),
    }
    
    @staticmethod
    def generate_synthetic_speech(sr=16000, duration=2.0, num_syllables=None):
        """Generate synthetic speech-like signal"""
        t = np.linspace(0, duration, int(sr * duration))
        
        # Fundamental frequency (pitch) variations
        f0_mean = 200  # 200 Hz base
        f0_variation = 50 * np.sin(2 * np.pi * 3 * t)  # 3 Hz modulation
        f0 = f0_mean + f0_variation
        
        # Instantaneous phase
        phase = 2 * np.pi * np.cumsum(f0) / sr
        
        # Fundamental
        signal = 0.5 * np.sin(phase)
        
        # Harmonics
        for harmonic in [2, 3, 4, 5]:
            harmonic_amp = 0.2 / harmonic
            signal += harmonic_amp * np.sin(harmonic * phase)
        
        # Amplitude envelope (speech-like modulation)
        envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 2 * t)  # 2 Hz modulation
        signal = signal * envelope
        
        # Add formant-like regions
        formant_freqs = [800, 1500, 2500]
        for f_freq in formant_freqs:
            formant_phase = 2 * np.pi * f_freq * t
            formant = 0.1 * np.sin(formant_phase)
            signal = signal + formant * envelope
        
        return signal.astype(np.float32)
    
    @staticmethod
    def generate_noise(noise_type='white', sr=16000, duration=2.0, snr_db=5.0):
        """Generate specific noise type"""
        if noise_type not in TrainingDataGenerator.NOISE_TYPES:
            noise_type = 'white'
        
        noise_func = TrainingDataGenerator.NOISE_TYPES[noise_type]
        noise = noise_func(sr, duration)
        
        # Normalize
        noise = noise / (np.max(np.abs(noise)) + 1e-10)
        
        return noise.astype(np.float32)
    
    @staticmethod
    def mix_speech_noise(speech, noise, snr_db=5.0):
        """Mix speech and noise to achieve target SNR"""
        # Ensure same length
        min_len = min(len(speech), len(noise))
        speech = speech[:min_len]
        noise = noise[:min_len]
        
        # Calculate powers
        speech_power = np.mean(speech ** 2)
        noise_power = np.mean(noise ** 2)
        
        # Calculate noise gain for target SNR
        # SNR = 10 * log10(P_speech / P_noise)
        snr_linear = 10 ** (snr_db / 10)
        noise_gain = np.sqrt(speech_power / (snr_linear * noise_power + 1e-10))
        
        # Mix
        noisy = speech + noise_gain * noise
        
        # Normalize to avoid clipping
        max_val = np.max(np.abs(noisy)) + 1e-10
        if max_val > 1.0:
            noisy = noisy / max_val * 0.95
        
        return noisy.astype(np.float32), noise_gain * noise
    
    @staticmethod
    def generate_training_set(output_dir='training_data_advanced', 
                            num_samples=500, 
                            sr=16000, 
                            duration=2.0,
                            snr_range=(0, 15)):
        """
        Generate complete training dataset
        
        Args:
            output_dir: Output directory
            num_samples: Total number of training pairs
            sr: Sample rate
            duration: Duration of each sample
            snr_range: SNR range (min, max) in dB
        """
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        clean_dir = output_dir / 'clean'
        noisy_dir = output_dir / 'noisy'
        clean_dir.mkdir(exist_ok=True)
        noisy_dir.mkdir(exist_ok=True)
        
        # Metadata
        metadata = {
            'generated': datetime.now().isoformat(),
            'sr': sr,
            'duration': duration,
            'num_samples': num_samples,
            'snr_range': snr_range,
            'samples': []
        }
        
        print(f"\n{'='*70}")
        print("GENERATING TRAINING DATASET")
        print(f"{'='*70}")
        print(f"Output: {output_dir}")
        print(f"Samples: {num_samples}")
        print(f"SNR Range: {snr_range[0]} - {snr_range[1]} dB")
        
        noise_types = list(TrainingDataGenerator.NOISE_TYPES.keys())
        
        for sample_idx in range(num_samples):
            # Progress
            if (sample_idx + 1) % 50 == 0:
                print(f"  Generated {sample_idx + 1}/{num_samples}...")
            
            # Random noise type and SNR
            noise_type = np.random.choice(noise_types)
            snr_db = np.random.uniform(snr_range[0], snr_range[1])
            
            # Generate speech
            clean = TrainingDataGenerator.generate_synthetic_speech(sr=sr, duration=duration)
            clean = clean / (np.max(np.abs(clean)) + 1e-10) * 0.8  # Normalize
            
            # Generate noise
            noise = TrainingDataGenerator.generate_noise(noise_type=noise_type, sr=sr, duration=duration)
            
            # Mix
            noisy, _ = TrainingDataGenerator.mix_speech_noise(clean, noise, snr_db=snr_db)
            
            # Save
            sample_name = f"sample_{sample_idx:05d}"
            sf.write(clean_dir / f"{sample_name}.wav", clean, sr, subtype='PCM_16')
            sf.write(noisy_dir / f"{sample_name}.wav", noisy, sr, subtype='PCM_16')
            
            # Metadata
            metadata['samples'].append({
                'idx': sample_idx,
                'name': sample_name,
                'noise_type': noise_type,
                'snr_db': float(snr_db),
                'clean_file': f"clean/{sample_name}.wav",
                'noisy_file': f"noisy/{sample_name}.wav"
            })
        
        # Save metadata
        with open(output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"✓ Dataset generated successfully!")
        print(f"  Total samples: {num_samples}")
        print(f"  Clean audio: {clean_dir}")
        print(f"  Noisy audio: {noisy_dir}")
        print(f"  Metadata: {output_dir}/metadata.json")
        print(f"{'='*70}\n")
        
        return output_dir, metadata


# Helper functions for noise generation
def _pink_noise(length):
    """Generate pink noise"""
    length = int(length)
    white = np.random.randn(length)
    return np.cumsum(white) / np.sqrt(length)

def _brown_noise(length):
    """Generate brown (Brownian) noise"""
    length = int(length)
    pink = _pink_noise(int(length * 1.5))
    brown = np.cumsum(pink)
    return brown[:int(length)]

def _synthetic_speech(sr, duration, noise=False):
    """Generate synthetic speech-like noise"""
    t = np.linspace(0, duration, int(sr * duration))
    signal = np.sin(2 * np.pi * 200 * t)
    signal += 0.5 * np.sin(2 * np.pi * 400 * t)
    signal *= 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)
    if noise:
        signal += 0.1 * np.random.randn(len(t))
    return signal

def _traffic_noise(sr, duration):
    """Generate traffic-like noise"""
    t = np.linspace(0, duration, int(sr * duration))
    # Mix of periodic and random
    periodic = 0.3 * np.sin(2 * np.pi * 150 * t)
    periodic += 0.2 * np.sin(2 * np.pi * 75 * t)
    random_part = 0.4 * np.random.randn(len(t))
    return (periodic + random_part) / 2

def _babble_noise(sr, duration):
    """Generate babble (multiple speakers) noise"""
    t = np.linspace(0, duration, int(sr * duration))
    babble = np.zeros_like(t)
    for _ in range(5):  # 5 overlapping speakers
        f = np.random.uniform(200, 400)
        babble += 0.2 * np.sin(2 * np.pi * f * t)
        babble += 0.1 * np.sin(2 * np.pi * f * 1.5 * t)
    babble += 0.1 * np.random.randn(len(t))
    return babble

def _office_noise(sr, duration):
    """Generate office background noise"""
    t = np.linspace(0, duration, int(sr * duration))
    # Mix of hum, typing, and background
    hum = 0.1 * np.sin(2 * np.pi * 60 * t)
    typing = np.random.choice([0, 1], size=len(t), p=[0.7, 0.3]) * 0.3 * np.random.randn(len(t))
    background = 0.2 * np.random.randn(len(t))
    return hum + typing + background

def _wind_noise(sr, duration):
    """Generate wind noise"""
    # Low frequency modulated noise
    t = np.linspace(0, duration, int(sr * duration))
    wind = np.random.randn(int(sr * duration))
    # Apply low-pass filter effect
    from scipy import signal as scipy_signal
    sos = scipy_signal.butter(4, 2000, btype='low', fs=sr, output='sos')
    wind = scipy_signal.sosfilt(sos, wind)
    # Amplitude modulation
    modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 1.5 * t)
    return wind * modulation


if __name__ == '__main__':
    # Example usage
    output_dir, metadata = TrainingDataGenerator.generate_training_set(
        output_dir='training_data_advanced',
        num_samples=100,  # Generate 100 samples
        duration=2.0,
        snr_range=(0, 15)
    )
    
    print(f"\nGenerated dataset at: {output_dir}")
    print(f"First 3 samples:")
    for sample in metadata['samples'][:3]:
        print(f"  {sample['name']}: {sample['noise_type']} (SNR: {sample['snr_db']:.1f} dB)")
