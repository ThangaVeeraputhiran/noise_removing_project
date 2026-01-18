#!/usr/bin/env python3
"""
Simple Dataset Preparation - Without librosa in loop
Generates training data efficiently
"""

import os
import numpy as np
import soundfile as sf
from pathlib import Path
import json
from datetime import datetime

class SimpleDatasetGenerator:
    """Generate training dataset efficiently"""
    
    def __init__(self, base_path='Dataset_Generated'):
        self.base_path = base_path
        self.voice_path = os.path.join(base_path, 'source', 'Voice')
        self.noise_path = os.path.join(base_path, 'source', 'Noise')
        self.sr = 16000
        
        # Create directories
        os.makedirs(self.voice_path, exist_ok=True)
        os.makedirs(os.path.join(self.noise_path, 'Household_Appliance'), exist_ok=True)
        os.makedirs(os.path.join(self.noise_path, 'TVnRadio'), exist_ok=True)
        os.makedirs(os.path.join(self.noise_path, 'Vehicles'), exist_ok=True)
        os.makedirs(os.path.join(self.noise_path, 'Verbal_Human'), exist_ok=True)
    
    def generate_synthetic_speech(self, n_files=100, duration=3.0):
        """Generate synthetic clean speech for training"""
        print(f"[1/3] Generating {n_files} synthetic speech files...")
        
        for i in range(n_files):
            # Create speech-like signal with formants
            t = np.linspace(0, duration, int(self.sr * duration))
            
            # Fundamental frequency + harmonics (simulating speech)
            f0 = 100 + np.random.randint(-50, 150)  # Fundamental
            
            # Formants (characteristic frequencies of vowels)
            formants = [
                700 + np.random.randint(-100, 100),   # F1
                1220 + np.random.randint(-200, 200),  # F2
                2600 + np.random.randint(-300, 300)   # F3
            ]
            
            # Amplitude envelope (speech is not constant)
            envelope = np.sin(np.pi * t / duration) ** 0.3
            
            # Generate waveform
            signal = np.zeros_like(t)
            signal += 0.5 * np.sin(2 * np.pi * f0 * t)
            signal += 0.3 * np.sin(2 * np.pi * formants[0] * t)
            signal += 0.2 * np.sin(2 * np.pi * formants[1] * t)
            signal += 0.1 * np.sin(2 * np.pi * formants[2] * t)
            
            signal = signal * envelope
            signal = signal / (np.max(np.abs(signal)) + 1e-10) * 0.8
            
            # Save
            filename = os.path.join(self.voice_path, f'synthetic_speech_{i:04d}.wav')
            sf.write(filename, signal, self.sr, subtype='PCM_16')
            
            if (i + 1) % 20 == 0:
                print(f"  Generated {i + 1}/{n_files} files")
        
        print(f"✓ Generated {n_files} synthetic speech files")
    
    def generate_synthetic_noise(self, n_files=50, duration=3.0):
        """Generate synthetic noise datasets"""
        print(f"[2/3] Generating {n_files * 4} synthetic noise files...")
        
        noise_types = {
            'Household_Appliance': {
                'freq_range': (100, 500),
                'description': 'Refrigerator, microwave, washing machine'
            },
            'Vehicles': {
                'freq_range': (50, 200),
                'description': 'Car, bus, motorcycle'
            },
            'Verbal_Human': {
                'freq_range': (400, 2000),
                'description': 'Background speech, conversations'
            },
            'TVnRadio': {
                'freq_range': (100, 4000),
                'description': 'TV, radio, broadcast'
            }
        }
        
        for noise_type, params in noise_types.items():
            print(f"  Generating {noise_type}...")
            freq_min, freq_max = params['freq_range']
            
            for i in range(n_files):
                t = np.linspace(0, duration, int(self.sr * duration))
                
                # Create noise with specific characteristics
                noise = np.random.randn(len(t)) * 0.1
                
                # Add some structure (not white noise)
                n_components = np.random.randint(3, 8)
                for _ in range(n_components):
                    freq = np.random.uniform(freq_min, freq_max)
                    amp = np.random.uniform(0.1, 0.3)
                    noise += amp * np.sin(2 * np.pi * freq * t)
                
                # Add amplitude modulation (makes it more realistic)
                mod_freq = np.random.uniform(2, 8)
                modulation = 0.5 + 0.5 * np.sin(2 * np.pi * mod_freq * t)
                noise = noise * modulation
                
                # Normalize
                noise = noise / (np.max(np.abs(noise)) + 1e-10) * 0.6
                
                # Save
                noise_dir = os.path.join(self.noise_path, noise_type)
                filename = os.path.join(noise_dir, f'synthetic_{noise_type.lower()}_{i:04d}.wav')
                sf.write(filename, noise, self.sr, subtype='PCM_16')
            
            print(f"    ✓ Generated {n_files} {noise_type} files")
        
        print(f"✓ Generated synthetic noise datasets")
    
    def mix_datasets(self, output_path='Dataset_Generated/Train', n_mixtures=200):
        """Mix voice and noise to create training dataset"""
        print(f"[3/3] Creating mixed training dataset with {n_mixtures} mixtures...")
        
        os.makedirs(os.path.join(output_path, 'Noisy'), exist_ok=True)
        os.makedirs(os.path.join(output_path, 'Clean'), exist_ok=True)
        
        # Get all files
        voice_files = sorted(list(Path(self.voice_path).glob('*.wav')))
        
        noise_types = ['Household_Appliance', 'Vehicles', 'Verbal_Human', 'TVnRadio']
        noise_files_by_type = {}
        
        for noise_type in noise_types:
            noise_dir = os.path.join(self.noise_path, noise_type)
            noise_files_by_type[noise_type] = sorted(list(Path(noise_dir).glob('*.wav')))
        
        for i in range(n_mixtures):
            # Random voice file
            voice_file = np.random.choice(voice_files)
            voice_data, sr1 = sf.read(str(voice_file))
            
            # Random noise type
            noise_type = np.random.choice(noise_types)
            noise_files = noise_files_by_type[noise_type]
            
            if noise_files:
                noise_file = np.random.choice(noise_files)
                noise_data, sr2 = sf.read(str(noise_file))
                
                # Ensure same length
                min_len = min(len(voice_data), len(noise_data))
                voice_data = voice_data[:min_len]
                noise_data = noise_data[:min_len]
                
                # Random SNR: 5 to 15 dB
                snr_db = np.random.uniform(5, 15)
                
                # Mix
                voice_power = np.mean(voice_data ** 2)
                noise_power = np.mean(noise_data ** 2)
                snr_linear = 10 ** (snr_db / 10)
                
                # Scale noise
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
            
            if (i + 1) % 50 == 0:
                print(f"  Created {i + 1}/{n_mixtures} training mixtures")
        
        print(f"✓ Created {n_mixtures} mixed training samples")
    
    def create_manifest(self, output_path='Dataset_Generated/Train'):
        """Create manifest file for training"""
        clean_files = sorted(list(Path(os.path.join(output_path, 'Clean')).glob('*.wav')))
        noisy_files = sorted(list(Path(os.path.join(output_path, 'Noisy')).glob('*.wav')))
        
        manifest = {
            'dataset_name': 'Generated Training Dataset',
            'created': datetime.now().isoformat(),
            'total_samples': len(clean_files),
            'sample_rate': 16000,
            'clean_files': [str(f) for f in clean_files],
            'noisy_files': [str(f) for f in noisy_files]
        }
        
        manifest_file = os.path.join(output_path, 'manifest.json')
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✓ Manifest created: {len(clean_files)} samples")

def main():
    """Prepare complete training dataset"""
    
    print("\n" + "="*70)
    print("TRAINING DATASET GENERATION")
    print("="*70 + "\n")
    
    generator = SimpleDatasetGenerator()
    
    # Generate synthetic data
    generator.generate_synthetic_speech(n_files=100, duration=3.0)
    generator.generate_synthetic_noise(n_files=50, duration=3.0)
    
    # Mix into training set
    generator.mix_datasets(n_mixtures=200)
    
    # Create manifest
    generator.create_manifest()
    
    print("\n" + "="*70)
    print("✓ DATASET GENERATION COMPLETE")
    print("="*70)
    print("\nDataset structure:")
    print("  Dataset_Generated/")
    print("    source/")
    print("      Voice/          - 100 clean speech files")
    print("      Noise/          - 200 noise files (4 types)")
    print("    Train/")
    print("      Clean/          - 200 clean speech files")
    print("      Noisy/          - 200 mixed noisy speech files")
    print("\n✓ Ready for model training/retraining!")

if __name__ == '__main__':
    main()
