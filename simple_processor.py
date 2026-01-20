#!/usr/bin/env python3
"""
Simple Audio Processor - Fallback Mode
No numba, no complex dependencies - just basic signal processing
"""

import os
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.fftpack import fft, ifft

class SimpleAudioProcessor:
    """Simple processor without numba dependencies"""
    
    @staticmethod
    def load_audio(file_path, sr=16000):
        """Load audio file"""
        try:
            audio, sample_rate = sf.read(file_path)
            
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            
            # Resample if needed (simple decimation/interpolation)
            if sample_rate != sr:
                num_samples = int(len(audio) * sr / sample_rate)
                audio = signal.resample(audio, num_samples)
            
            # Normalize
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.95
            
            return audio.astype(np.float32), sr
        except Exception as e:
            raise Exception(f"Error loading audio: {str(e)}")
    
    @staticmethod
    def save_audio(audio, file_path, sr=16000):
        """Save audio file"""
        try:
            # Normalize to prevent clipping
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.95
            
            sf.write(file_path, audio, sr)
            return True
        except Exception as e:
            raise Exception(f"Error saving audio: {str(e)}")
    
    @staticmethod
    def spectral_subtraction(audio, sr=16000, alpha=2.0):
        """Simple spectral subtraction noise reduction"""
        
        # Parameters
        frame_length = 512
        hop_length = 256
        
        # Compute STFT
        f, t, stft_data = signal.stft(
            audio, 
            fs=sr, 
            nperseg=frame_length, 
            noverlap=frame_length - hop_length
        )
        
        # Estimate noise from first 10 frames (assumed to be noise)
        noise_estimate = np.mean(np.abs(stft_data[:, :10]), axis=1, keepdims=True)
        
        # Spectral subtraction
        magnitude = np.abs(stft_data)
        phase = np.angle(stft_data)
        
        # Subtract noise
        clean_magnitude = magnitude - alpha * noise_estimate
        clean_magnitude = np.maximum(clean_magnitude, 0.1 * magnitude)  # Floor
        
        # Reconstruct
        clean_stft = clean_magnitude * np.exp(1j * phase)
        
        # Inverse STFT
        _, enhanced_audio = signal.istft(
            clean_stft, 
            fs=sr, 
            nperseg=frame_length, 
            noverlap=frame_length - hop_length
        )
        
        return enhanced_audio.astype(np.float32)
    
    @staticmethod
    def enhance(audio, sr=16000, level='medium'):
        """Enhanced audio with level control"""
        
        # Alpha values for different levels
        alpha_map = {
            'low': 1.5,
            'medium': 2.0,
            'high': 2.5,
            'advanced': 3.0,
            'extreme': 3.5
        }
        
        alpha = alpha_map.get(level, 2.0)
        
        # Apply spectral subtraction
        enhanced = SimpleAudioProcessor.spectral_subtraction(audio, sr, alpha)
        
        # Ensure proper length
        if len(enhanced) > len(audio):
            enhanced = enhanced[:len(audio)]
        elif len(enhanced) < len(audio):
            enhanced = np.pad(enhanced, (0, len(audio) - len(enhanced)))
        
        # Normalize
        if np.max(np.abs(enhanced)) > 0:
            enhanced = enhanced / np.max(np.abs(enhanced)) * 0.95
        
        return enhanced.astype(np.float32)
    
    @staticmethod
    def calculate_snr(original, enhanced):
        """Calculate SNR improvement (simplified)"""
        # Estimate signal and noise power
        signal_power = np.mean(enhanced ** 2)
        noise_power = np.mean((original - enhanced) ** 2) + 1e-10
        
        snr = 10 * np.log10(signal_power / noise_power)
        return max(0, min(snr, 20))  # Clip to reasonable range
    
    @staticmethod
    def classify_noise(audio, sr=16000):
        """Simple noise classification based on spectral features"""
        
        # Compute spectral features
        f, psd = signal.welch(audio, sr, nperseg=1024)
        
        # Simple heuristics
        low_freq_power = np.sum(psd[f < 500])
        mid_freq_power = np.sum(psd[(f >= 500) & (f < 2000)])
        high_freq_power = np.sum(psd[f >= 2000])
        
        total_power = low_freq_power + mid_freq_power + high_freq_power + 1e-10
        
        # Classification logic
        if low_freq_power / total_power > 0.6:
            return 'vehicle', 75.0
        elif high_freq_power / total_power > 0.5:
            return 'appliance', 70.0
        elif mid_freq_power / total_power > 0.5:
            return 'voice', 80.0
        else:
            return 'general', 65.0


class SimpleLogger:
    """Simple logging"""
    
    @staticmethod
    def log(message, level="INFO"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")


# Compatibility aliases
AudioProcessor = SimpleAudioProcessor
Logger = SimpleLogger
NoiseClassifier = SimpleAudioProcessor

# Export simplified enhancer
class AdvancedSpeechEnhancer:
    """Simplified enhancer"""
    @staticmethod
    def enhance(audio, sr=16000, profile='medium'):
        return SimpleAudioProcessor.enhance(audio, sr, profile)
    
    @staticmethod
    def calculate_snr_improvement(original, enhanced, sr=16000):
        return SimpleAudioProcessor.calculate_snr(original, enhanced)
