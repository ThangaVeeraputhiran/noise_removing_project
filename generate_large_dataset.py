#!/usr/bin/env python3
"""
LARGE-SCALE TRAINING DATASET GENERATOR
Generates 1000+ high-quality training samples
For maximum noise reduction training
"""

import os
import numpy as np
import soundfile as sf
from pathlib import Path
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

class LargeScaleDatasetGenerator:
    """Generate large training dataset for ultra noise reduction"""
    
    def __init__(self, base_path='Dataset_Ultra'):
        self.base_path = base_path
        self.voice_path = os.path.join(base_path, 'source', 'Voice')
        self.noise_path = os.path.join(base_path, 'source', 'Noise')
        self.sr = 16000
        
        # Create directories
        os.makedirs(self.voice_path, exist_ok=True)
        for noise_type in ['Household_Appliance', 'Vehicles', 'Verbal_Human', 'TVnRadio', 'White_Noise', 'Environmental']:
            os.makedirs(os.path.join(self.noise_path, noise_type), exist_ok=True)
    
    def generate_advanced_speech(self, idx, duration=4.0):
        """Generate high-quality synthetic speech with realistic characteristics"""
        t = np.linspace(0, duration, int(self.sr * duration))
        
        # Multiple fundamental frequencies (simulating different speakers)
        f0_options = [100, 120, 150, 180, 200, 220]  # Male and female voices
        f0 = np.random.choice(f0_options)
        
        # Time-varying fundamental (pitch variation)
        f0_variation = f0 + 20 * np.sin(2 * np.pi * 2 * t)
        
        # Formants (vowel sounds)
        vowels = [
            [700, 1220, 2600],   # /a/
            [270, 2290, 3010],   # /i/
            [300, 870, 2240],    # /u/
            [500, 1500, 2500],   # /e/
            [600, 1040, 2250]    # /o/
        ]
        
        # Random vowel sequence
        signal = np.zeros_like(t)
        n_segments = 5
        segment_length = len(t) // n_segments
        
        for i in range(n_segments):
            start = i * segment_length
            end = (i + 1) * segment_length if i < n_segments - 1 else len(t)
            
            formants = vowels[np.random.randint(len(vowels))]
            t_seg = t[start:end]
            
            # Fundamental + harmonics
            seg = 0.4 * np.sin(2 * np.pi * f0_variation[start:end] * t_seg)
            seg += 0.25 * np.sin(2 * np.pi * formants[0] * t_seg)
            seg += 0.2 * np.sin(2 * np.pi * formants[1] * t_seg)
            seg += 0.15 * np.sin(2 * np.pi * formants[2] * t_seg)
            
            signal[start:end] = seg
        
        # Amplitude envelope (natural speech dynamics)
        envelope = np.sin(np.pi * t / duration) ** 0.5
        envelope += 0.3 * np.random.rand(len(t))  # Random variations
        envelope = np.clip(envelope, 0, 1)
        
        signal = signal * envelope
        
        # Add subtle breathiness
        signal += 0.05 * np.random.randn(len(t))
        
        # Normalize
        signal = signal / (np.max(np.abs(signal)) + 1e-10) * 0.75
        
        return signal.astype(np.float32)
    
    def generate_realistic_noise(self, noise_type, idx, duration=4.0):
        """Generate realistic noise with specific characteristics"""
        t = np.linspace(0, duration, int(self.sr * duration))
        
        noise_params = {
            'Household_Appliance': {
                'base_freq': [60, 120, 180, 240],  # AC hum harmonics
                'modulation_freq': (5, 15),
                'white_noise_level': 0.15,
                'spectral_color': 'pink'
            },
            'Vehicles': {
                'base_freq': [80, 160, 240],  # Engine harmonics
                'modulation_freq': (2, 8),
                'white_noise_level': 0.25,
                'spectral_color': 'brown'
            },
            'Verbal_Human': {
                'base_freq': [200, 400, 800, 1600],  # Speech-like
                'modulation_freq': (3, 12),
                'white_noise_level': 0.1,
                'spectral_color': 'white'
            },
            'TVnRadio': {
                'base_freq': [100, 200, 400, 800, 1600, 3200],
                'modulation_freq': (10, 30),
                'white_noise_level': 0.2,
                'spectral_color': 'white'
            },
            'White_Noise': {
                'base_freq': [],
                'modulation_freq': (1, 5),
                'white_noise_level': 0.5,
                'spectral_color': 'white'
            },
            'Environmental': {
                'base_freq': [50, 100, 200, 400],  # Wind, rain, etc.
                'modulation_freq': (0.5, 3),
                'white_noise_level': 0.3,
                'spectral_color': 'pink'
            }
        }
        
        params = noise_params.get(noise_type, noise_params['White_Noise'])
        
        # Start with colored noise
        if params['spectral_color'] == 'pink':
            # Pink noise (1/f spectrum)
            white = np.random.randn(len(t))
            freqs = np.fft.rfftfreq(len(t), 1/self.sr)
            spectrum = np.fft.rfft(white)
            spectrum = spectrum / (np.sqrt(freqs + 1) + 1e-10)
            noise = np.fft.irfft(spectrum, n=len(t))
        elif params['spectral_color'] == 'brown':
            # Brown noise (1/f^2 spectrum)
            white = np.random.randn(len(t))
            freqs = np.fft.rfftfreq(len(t), 1/self.sr)
            spectrum = np.fft.rfft(white)
            spectrum = spectrum / (freqs + 1 + 1e-10)
            noise = np.fft.irfft(spectrum, n=len(t))
        else:
            # White noise
            noise = np.random.randn(len(t))
        
        noise = noise * params['white_noise_level']
        
        # Add harmonic components
        for freq in params['base_freq']:
            amplitude = np.random.uniform(0.1, 0.3)
            noise += amplitude * np.sin(2 * np.pi * freq * t + np.random.uniform(0, 2*np.pi))
        
        # Add amplitude modulation
        mod_freq = np.random.uniform(*params['modulation_freq'])
        modulation = 0.6 + 0.4 * np.sin(2 * np.pi * mod_freq * t)
        noise = noise * modulation
        
        # Normalize
        noise = noise / (np.max(np.abs(noise)) + 1e-10) * 0.65
        
        return noise.astype(np.float32)
    
    def generate_speech_batch(self, n_files, start_idx):
        """Generate batch of speech files"""
        print(f"    Generating speech files {start_idx} to {start_idx + n_files}...")
        for i in range(n_files):
            idx = start_idx + i
            signal = self.generate_advanced_speech(idx, duration=4.0)
            filename = os.path.join(self.voice_path, f'speech_{idx:05d}.wav')
            sf.write(filename, signal, self.sr, subtype='PCM_16')
        return n_files
    
    def generate_noise_batch(self, noise_type, n_files, start_idx):
        """Generate batch of noise files"""
        print(f"    Generating {noise_type} files {start_idx} to {start_idx + n_files}...")
        noise_dir = os.path.join(self.noise_path, noise_type)
        for i in range(n_files):
            idx = start_idx + i
            noise = self.generate_realistic_noise(noise_type, idx, duration=4.0)
            filename = os.path.join(noise_dir, f'{noise_type.lower()}_{idx:05d}.wav')
            sf.write(filename, noise, self.sr, subtype='PCM_16')
        return n_files
    
    def generate_all_data(self, n_speech=500, n_noise_per_type=200):
        """Generate all source data"""
        print(f"\n[1/3] Generating {n_speech} speech files...")
        
        # Generate speech files in batches
        batch_size = 50
        for start_idx in range(0, n_speech, batch_size):
            end_idx = min(start_idx + batch_size, n_speech)
            self.generate_speech_batch(end_idx - start_idx, start_idx)
        
        print(f"✓ Generated {n_speech} speech files")
        
        print(f"\n[2/3] Generating noise files...")
        noise_types = ['Household_Appliance', 'Vehicles', 'Verbal_Human', 'TVnRadio', 'White_Noise', 'Environmental']
        
        for noise_type in noise_types:
            print(f"  Generating {noise_type}...")
            for start_idx in range(0, n_noise_per_type, batch_size):
                end_idx = min(start_idx + batch_size, n_noise_per_type)
                self.generate_noise_batch(noise_type, end_idx - start_idx, start_idx)
            print(f"  ✓ Generated {n_noise_per_type} {noise_type} files")
        
        print(f"✓ Generated {n_noise_per_type * len(noise_types)} total noise files")
    
    def mix_training_data(self, output_path='Dataset_Ultra/Train', n_mixtures=1000):
        """Mix voice and noise to create training pairs"""
        print(f"\n[3/3] Creating {n_mixtures} training mixtures...")
        
        os.makedirs(os.path.join(output_path, 'Noisy'), exist_ok=True)
        os.makedirs(os.path.join(output_path, 'Clean'), exist_ok=True)
        
        # Get all files
        voice_files = sorted(list(Path(self.voice_path).glob('*.wav')))
        
        noise_types = ['Household_Appliance', 'Vehicles', 'Verbal_Human', 'TVnRadio', 'White_Noise', 'Environmental']
        noise_files_by_type = {}
        
        for noise_type in noise_types:
            noise_dir = os.path.join(self.noise_path, noise_type)
            noise_files_by_type[noise_type] = sorted(list(Path(noise_dir).glob('*.wav')))
        
        for i in range(n_mixtures):
            # Random voice
            voice_file = np.random.choice(voice_files)
            voice_data, sr1 = sf.read(str(voice_file))
            
            # Random noise type
            noise_type = np.random.choice(noise_types)
            noise_files = noise_files_by_type[noise_type]
            
            if noise_files:
                noise_file = np.random.choice(noise_files)
                noise_data, sr2 = sf.read(str(noise_file))
                
                # Match lengths
                min_len = min(len(voice_data), len(noise_data))
                voice_data = voice_data[:min_len]
                noise_data = noise_data[:min_len]
                
                # Random SNR: 0 to 20 dB (wide range for robustness)
                snr_db = np.random.uniform(0, 20)
                
                # Mix
                voice_power = np.mean(voice_data ** 2)
                noise_power = np.mean(noise_data ** 2)
                snr_linear = 10 ** (snr_db / 10)
                
                if noise_power > 1e-10:
                    noise_scaled = noise_data * np.sqrt(voice_power / (snr_linear * noise_power))
                else:
                    noise_scaled = noise_data
                
                # Mix
                mixed = voice_data + noise_scaled
                mixed = mixed / (np.max(np.abs(mixed)) + 1e-10) * 0.8
                
                # Save
                clean_file = os.path.join(output_path, 'Clean', f'clean_{i:05d}.wav')
                noisy_file = os.path.join(output_path, 'Noisy', f'noisy_{i:05d}.wav')
                
                sf.write(clean_file, voice_data, self.sr, subtype='PCM_16')
                sf.write(noisy_file, mixed, self.sr, subtype='PCM_16')
            
            if (i + 1) % 100 == 0:
                print(f"  Created {i + 1}/{n_mixtures} training mixtures")
        
        print(f"✓ Created {n_mixtures} training pairs")
    
    def create_manifest(self, output_path='Dataset_Ultra/Train'):
        """Create manifest"""
        clean_files = sorted(list(Path(os.path.join(output_path, 'Clean')).glob('*.wav')))
        noisy_files = sorted(list(Path(os.path.join(output_path, 'Noisy')).glob('*.wav')))
        
        manifest = {
            'dataset_name': 'Ultra Large-Scale Training Dataset',
            'created': datetime.now().isoformat(),
            'total_samples': len(clean_files),
            'sample_rate': 16000,
            'duration_per_file': 4.0,
            'total_duration_hours': len(clean_files) * 4.0 / 3600,
            'clean_files': [str(f) for f in clean_files],
            'noisy_files': [str(f) for f in noisy_files]
        }
        
        manifest_file = os.path.join(output_path, 'manifest.json')
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n✓ Manifest created: {len(clean_files)} samples ({manifest['total_duration_hours']:.1f} hours)")

def main():
    """Generate large-scale training dataset"""
    
    print("\n" + "="*70)
    print("LARGE-SCALE TRAINING DATASET GENERATION")
    print("Target: 1000+ high-quality training samples")
    print("="*70)
    
    generator = LargeScaleDatasetGenerator()
    
    # Generate source data
    print("\nGenerating source data...")
    generator.generate_all_data(n_speech=500, n_noise_per_type=200)
    
    # Mix training data
    print("\nMixing training data...")
    generator.mix_training_data(n_mixtures=1000)
    
    # Create manifest
    generator.create_manifest()
    
    print("\n" + "="*70)
    print("✓ LARGE-SCALE DATASET GENERATION COMPLETE")
    print("="*70)
    print("\nDataset Statistics:")
    print("  - Speech files: 500")
    print("  - Noise files: 1200 (6 types × 200)")
    print("  - Training pairs: 1000")
    print("  - Total duration: ~4.4 hours")
    print("  - Sample rate: 16 kHz")
    print("  - Duration per file: 4 seconds")
    print("\n✓ Ready for ultra noise reduction training!")

if __name__ == '__main__':
    main()
