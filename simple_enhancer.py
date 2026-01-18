#!/usr/bin/env python3
"""
Simplified but Effective Speech Enhancement using DSP
Robust noise reduction without complex issues
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
import warnings

warnings.filterwarnings('ignore')

class SimpleEnhancer:
    """
    Simple but effective speech enhancement
    """
    
    SAMPLE_RATE = 16000
    N_FFT = 512
    HOP_LENGTH = 128
    
    @staticmethod
    def wiener_denoise(audio, noise_duration=0.5):
        """
        Wiener filtering for noise reduction
        Optimal in mean-square-error sense
        """
        sr = SimpleEnhancer.SAMPLE_RATE
        n_fft = SimpleEnhancer.N_FFT
        hop_length = SimpleEnhancer.HOP_LENGTH
        
        # STFT
        D = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length, window='hann')
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Estimate noise from first few frames
        noise_frames = max(2, int(noise_duration * sr / hop_length))
        noise_power = np.mean(magnitude[:, :noise_frames] ** 2, axis=1, keepdims=True)
        noise_power = np.maximum(noise_power, 1e-10)
        
        # Signal power
        signal_power = magnitude ** 2
        
        # Wiener gain
        gain = np.maximum(0, (signal_power - noise_power) / (signal_power + noise_power))
        
        # Apply gain
        magnitude_clean = magnitude * gain
        
        # Reconstruct
        D_clean = magnitude_clean * np.exp(1j * phase)
        audio_clean = librosa.istft(D_clean, hop_length=hop_length, window='hann')
        
        return audio_clean.astype(np.float32)
    
    @staticmethod
    def spectral_subtraction(audio, alpha=2.0, floor=0.001):
        """
        Spectral subtraction
        Subtracts noise estimate from signal
        """
        sr = SimpleEnhancer.SAMPLE_RATE
        n_fft = SimpleEnhancer.N_FFT
        hop_length = SimpleEnhancer.HOP_LENGTH
        
        # STFT
        D = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length, window='hann')
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Noise estimate
        noise_frames = 3
        noise_magnitude = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Spectral subtraction
        magnitude_clean = magnitude - alpha * noise_magnitude
        magnitude_clean = np.maximum(magnitude_clean, floor * noise_magnitude)
        
        # Reconstruct
        D_clean = magnitude_clean * np.exp(1j * phase)
        audio_clean = librosa.istft(D_clean, hop_length=hop_length, window='hann')
        
        return audio_clean.astype(np.float32)
    
    @staticmethod
    def bandpass_denoise(audio, low_freq=300, high_freq=3400):
        """
        Bandpass filtering to isolate speech frequencies
        Human speech mainly in 300-3400 Hz range
        """
        sr = SimpleEnhancer.SAMPLE_RATE
        
        # Design filter
        sos = signal.butter(5, [low_freq, high_freq], btype='band', fs=sr, output='sos')
        
        # Apply filter
        audio_filtered = signal.sosfilt(sos, audio)
        
        return audio_filtered.astype(np.float32)
    
    @staticmethod
    def improve_snr(noisy_audio, clean_estimate, iterations=2):
        """
        Iteratively improve SNR
        Refinement step for better results
        """
        for _ in range(iterations):
            clean_estimate = SimpleEnhancer.wiener_denoise(clean_estimate, noise_duration=0.3)
        
        return clean_estimate.astype(np.float32)
    
    @staticmethod
    def enhance(audio, method='combined', strength='high'):
        """
        Complete enhancement pipeline
        method: 'wiener', 'spectral', 'combined'
        strength: 'light', 'medium', 'high'
        """
        
        # Ensure mono
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        
        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 1.0:
            audio = audio / max_val
        
        if method == 'wiener':
            enhanced = SimpleEnhancer.wiener_denoise(audio)
        
        elif method == 'spectral':
            if strength == 'light':
                alpha = 1.5
            elif strength == 'medium':
                alpha = 2.0
            else:
                alpha = 2.5
            enhanced = SimpleEnhancer.spectral_subtraction(audio, alpha=alpha)
        
        elif method == 'combined':
            # Combine multiple approaches
            if strength == 'light':
                # Light: just Wiener
                enhanced = SimpleEnhancer.wiener_denoise(audio, noise_duration=0.5)
            
            elif strength == 'medium':
                # Medium: Wiener + bandpass
                enhanced = SimpleEnhancer.wiener_denoise(audio)
                enhanced = SimpleEnhancer.bandpass_denoise(enhanced)
                enhanced = SimpleEnhancer.wiener_denoise(enhanced, noise_duration=0.3)
            
            else:  # high or maximum
                # High: Multi-stage processing
                enhanced = SimpleEnhancer.wiener_denoise(audio, noise_duration=0.5)
                enhanced = SimpleEnhancer.spectral_subtraction(enhanced, alpha=2.0)
                enhanced = SimpleEnhancer.bandpass_denoise(enhanced, low_freq=200, high_freq=4000)
                enhanced = SimpleEnhancer.wiener_denoise(enhanced, noise_duration=0.2)
                
                if strength == 'maximum':
                    # Extra refinement
                    enhanced = SimpleEnhancer.spectral_subtraction(enhanced, alpha=1.5)
                    enhanced = SimpleEnhancer.improve_snr(audio, enhanced, iterations=1)
        
        else:
            enhanced = audio
        
        # Normalize output
        max_val_out = np.max(np.abs(enhanced))
        if max_val_out > 1.0:
            enhanced = enhanced / max_val_out
        
        return enhanced.astype(np.float32)


# Test function
def test():
    """Test the enhancer"""
    print("="*60)
    print("SIMPLE SPEECH ENHANCER - TEST")
    print("="*60)
    
    # Generate test audio
    sr = 16000
    duration = 3
    t = np.linspace(0, duration, int(sr * duration))
    
    # Speech-like signal
    speech = np.zeros_like(t)
    for f in [200, 400, 600, 800]:
        speech += 0.2 * np.sin(2 * np.pi * f * t)
    
    # Modulation
    modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)
    speech = speech * modulation
    
    # Noise
    noise = 0.5 * np.random.randn(len(t))
    noisy = speech + noise
    
    print(f"\nAudio: {duration}s at {sr}Hz")
    print(f"Clean RMS: {np.sqrt(np.mean(speech**2)):.4f}")
    print(f"Noise RMS: {np.sqrt(np.mean(noise**2)):.4f}")
    print(f"Noisy RMS: {np.sqrt(np.mean(noisy**2)):.4f}")
    
    # Enhance
    print("\nEnhancing (method='combined', strength='high')...")
    enhanced = SimpleEnhancer.enhance(noisy, method='combined', strength='high')
    
    print(f"Enhanced RMS: {np.sqrt(np.mean(enhanced**2)):.4f}")
    
    # Calculate improvement
    noise_orig = noisy - speech
    noise_enhanced = enhanced - speech
    snr_orig = 10 * np.log10(np.mean(speech**2) / (np.mean(noise_orig**2) + 1e-10))
    snr_enh = 10 * np.log10(np.mean(speech**2) / (np.mean(noise_enhanced**2) + 1e-10))
    improvement = snr_enh - snr_orig
    
    print(f"SNR Original: {snr_orig:.2f} dB")
    print(f"SNR Enhanced: {snr_enh:.2f} dB")
    print(f"SNR Improvement: {improvement:.2f} dB")
    
    print("\n✓ Test completed successfully")
    print("="*60)


if __name__ == '__main__':
    test()
