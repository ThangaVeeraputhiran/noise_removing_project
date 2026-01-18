#!/usr/bin/env python3
"""
Generate sample audio files for testing the Speech Enhancement System
Creates synthetic audio with different types of noise
"""

import numpy as np
import soundfile as sf
import os

def generate_sine_wave(frequency, duration, sample_rate=16000):
    """Generate a sine wave (simulates voice tone)"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    return 0.3 * np.sin(2 * np.pi * frequency * t)

def generate_white_noise(duration, sample_rate=16000, amplitude=0.1):
    """Generate white noise"""
    samples = int(sample_rate * duration)
    return amplitude * np.random.randn(samples)

def generate_speech_like_signal(duration, sample_rate=16000):
    """Generate a speech-like signal with multiple frequencies"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Fundamental frequency and harmonics (simulating speech)
    signal = (0.3 * np.sin(2 * np.pi * 200 * t) +  # F0
              0.15 * np.sin(2 * np.pi * 400 * t) +  # 2nd harmonic
              0.1 * np.sin(2 * np.pi * 600 * t) +   # 3rd harmonic
              0.05 * np.sin(2 * np.pi * 800 * t))   # 4th harmonic
    
    # Add some variation (simulate intonation)
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 2 * t)
    signal = signal * envelope
    
    return signal

def generate_vehicle_noise(duration, sample_rate=16000):
    """Generate vehicle-like noise (low frequency rumble)"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Low frequency engine rumble
    noise = (0.2 * np.sin(2 * np.pi * 60 * t) +
             0.15 * np.sin(2 * np.pi * 120 * t) +
             0.1 * np.random.randn(len(t)))
    
    return noise

def generate_household_noise(duration, sample_rate=16000):
    """Generate household appliance noise (periodic with white noise)"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Vacuum/fan like noise
    noise = (0.15 * np.sin(2 * np.pi * 100 * t) +
             0.1 * np.sin(2 * np.pi * 300 * t) +
             0.15 * np.random.randn(len(t)))
    
    return noise

def create_noisy_audio(clean_signal, noise_signal, snr_db):
    """Mix clean signal with noise at specified SNR"""
    # Calculate power
    signal_power = np.mean(clean_signal ** 2)
    noise_power = np.mean(noise_signal ** 2)
    
    # Calculate noise scaling factor
    snr_linear = 10 ** (snr_db / 10)
    noise_scale = np.sqrt(signal_power / (noise_power * snr_linear))
    
    # Mix
    noisy_signal = clean_signal + noise_scale * noise_signal
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(noisy_signal))
    if max_val > 0.95:
        noisy_signal = noisy_signal * (0.95 / max_val)
    
    return noisy_signal

def create_sample_files():
    """Create sample audio files for testing"""
    
    # Create directory
    sample_dir = 'sample_audio'
    os.makedirs(sample_dir, exist_ok=True)
    
    duration = 3.0  # 3 seconds
    sample_rate = 16000
    
    print("Creating sample audio files...")
    
    # Generate clean speech-like signal
    clean_speech = generate_speech_like_signal(duration, sample_rate)
    sf.write(f'{sample_dir}/clean_speech.wav', clean_speech, sample_rate)
    print(f"✓ Created clean_speech.wav")
    
    # Generate different types of noise
    white_noise = generate_white_noise(duration, sample_rate, amplitude=0.2)
    vehicle_noise = generate_vehicle_noise(duration, sample_rate)
    household_noise = generate_household_noise(duration, sample_rate)
    
    # Create noisy samples at different SNR levels
    snr_levels = [0, 5, 10]  # dB
    
    for snr in snr_levels:
        # White noise (Verbal Human)
        noisy_white = create_noisy_audio(clean_speech, white_noise, snr)
        sf.write(f'{sample_dir}/noisy_verbal_snr{snr}db.wav', noisy_white, sample_rate)
        print(f"✓ Created noisy_verbal_snr{snr}db.wav")
        
        # Vehicle noise
        noisy_vehicle = create_noisy_audio(clean_speech, vehicle_noise, snr)
        sf.write(f'{sample_dir}/noisy_vehicle_snr{snr}db.wav', noisy_vehicle, sample_rate)
        print(f"✓ Created noisy_vehicle_snr{snr}db.wav")
        
        # Household noise
        noisy_household = create_noisy_audio(clean_speech, household_noise, snr)
        sf.write(f'{sample_dir}/noisy_household_snr{snr}db.wav', noisy_household, sample_rate)
        print(f"✓ Created noisy_household_snr{snr}db.wav")
    
    print(f"\n✅ All sample files created in '{sample_dir}/' directory")
    print("\nYou can now test the web application with these files!")
    print("Or upload your own audio files through the web interface.")

if __name__ == '__main__':
    create_sample_files()
