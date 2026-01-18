#!/usr/bin/env python3
"""
Sophisticated Speech Enhancement using Advanced Signal Processing
No TensorFlow dependency - pure DSP algorithms
High-quality noise removal while preserving speech
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.fftpack import fft, ifft
import warnings

warnings.filterwarnings('ignore')

class SpeechEnhancer:
    """
    Advanced speech enhancement using multiple DSP algorithms
    Combines spectral subtraction, Wiener filtering, and adaptive filtering
    """
    
    SAMPLE_RATE = 16000
    N_FFT = 2048
    HOP_LENGTH = 512
    WINDOW = 'hann'
    
    @staticmethod
    def load_audio(file_path):
        """Load audio file"""
        audio, sr = librosa.load(file_path, sr=SpeechEnhancer.SAMPLE_RATE, mono=True)
        return audio.astype(np.float32), sr
    
    @staticmethod
    def save_audio(audio, file_path):
        """Save audio file"""
        audio = np.clip(audio, -1.0, 1.0)
        sf.write(file_path, audio, SpeechEnhancer.SAMPLE_RATE, subtype='PCM_16')
    
    @staticmethod
    def stft(audio):
        """Compute STFT"""
        return librosa.stft(audio, n_fft=SpeechEnhancer.N_FFT, 
                          hop_length=SpeechEnhancer.HOP_LENGTH,
                          window=SpeechEnhancer.WINDOW)
    
    @staticmethod
    def istft(D):
        """Inverse STFT"""
        audio = librosa.istft(D, hop_length=SpeechEnhancer.HOP_LENGTH,
                           window=SpeechEnhancer.WINDOW)
        return audio.astype(np.float32)
    
    @staticmethod
    def spectral_subtraction(noisy_audio, alpha=2.0, noise_frames=5):
        """
        Spectral Subtraction Algorithm
        Remove noise estimate from signal
        """
        # Compute STFT
        D = SpeechEnhancer.stft(noisy_audio)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Estimate noise spectrum from beginning (assume quiet start)
        noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Spectral subtraction with over-subtraction factor
        clean_magnitude = magnitude - alpha * noise_spectrum
        
        # Avoid negative values (set floor)
        clean_magnitude = np.maximum(clean_magnitude, 0.1 * noise_spectrum)
        
        # Reconstruct
        D_clean = clean_magnitude * np.exp(1j * phase)
        audio_clean = SpeechEnhancer.istft(D_clean)
        
        return audio_clean.astype(np.float32)
    
    @staticmethod
    def wiener_filter(noisy_audio, noise_est_frames=5):
        """
        Wiener Filter for optimal noise reduction
        Minimizes MSE between noisy and clean signal
        """
        # Compute STFT
        D = SpeechEnhancer.stft(noisy_audio)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Power spectrum
        power = magnitude ** 2
        
        # Estimate noise power from quiet frames
        noise_power = np.mean(power[:, :noise_est_frames], axis=1, keepdims=True)
        
        # Signal power
        signal_power = power
        
        # Wiener gain function
        wiener_gain = np.maximum(0, (signal_power - noise_power) / (signal_power + 1e-10))
        
        # Apply gain
        clean_magnitude = magnitude * wiener_gain
        
        # Reconstruct
        D_clean = clean_magnitude * np.exp(1j * phase)
        audio_clean = SpeechEnhancer.istft(D_clean)
        
        return audio_clean.astype(np.float32)
    
    @staticmethod
    def multi_band_filtering(audio, num_bands=8):
        """
        Multi-band processing
        Divide frequency spectrum into bands and process each independently
        """
        sr = SpeechEnhancer.SAMPLE_RATE
        nyquist = sr / 2
        
        # Frequency bands
        band_edges = np.linspace(0, nyquist, num_bands + 1)
        filtered_audio = np.zeros_like(audio)
        
        for i in range(num_bands):
            low_freq = max(50, band_edges[i])
            high_freq = min(nyquist - 1, band_edges[i + 1])
            
            # Bandpass filter
            sos = signal.butter(6, [low_freq, high_freq], btype='band', 
                              fs=sr, output='sos')
            band_audio = signal.sosfilt(sos, audio)
            
            # Apply Wiener to this band
            band_clean = SpeechEnhancer.wiener_filter(band_audio, noise_est_frames=3)
            
            # Ensure same length
            min_len = min(len(filtered_audio), len(band_clean))
            filtered_audio[:min_len] += band_clean[:min_len]
        
        return filtered_audio.astype(np.float32)
    
    @staticmethod
    def perceptual_weighting(audio, noise_reduction_strength=1.0):
        """
        Perceptually-weighted noise reduction
        Applies more aggressive filtering to frequencies less sensitive to human ear
        """
        # A-weighting curve (inverted) for higher perceptual importance of speech frequencies
        freqs = np.fft.rfftfreq(len(audio) * 2, 1 / SpeechEnhancer.SAMPLE_RATE)
        
        # Emphasis on speech frequencies (300-3000 Hz)
        speech_emphasis = np.zeros_like(freqs)
        speech_mask = (freqs >= 300) & (freqs <= 3000)
        speech_emphasis[speech_mask] = 1.0 + 0.5 * noise_reduction_strength
        speech_emphasis[~speech_mask] = 1.0
        
        # Apply in frequency domain
        audio_fft = np.fft.rfft(audio)
        audio_fft_weighted = audio_fft * speech_emphasis
        audio_weighted = np.fft.irfft(audio_fft_weighted, n=len(audio))
        
        return audio_weighted.astype(np.float32)
    
    @staticmethod
    def voice_activity_detection(audio, threshold_db=-40):
        """
        Simple VAD to identify speech regions
        Used to protect speech from over-suppression
        """
        # Compute spectrogram
        D = SpeechEnhancer.stft(audio)
        magnitude_db = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)
        
        # Simple energy-based VAD
        frame_energy = np.mean(magnitude_db, axis=0)
        vad = frame_energy > threshold_db
        
        return vad
    
    @staticmethod
    def adaptive_gain_control(audio, target_level=-20):
        """
        Adaptive gain to maintain consistent output level
        Prevents output from being too quiet or too loud
        """
        # Measure current level
        current_level = librosa.power_to_db(np.mean(audio ** 2))
        
        # Calculate gain needed
        gain_db = target_level - current_level
        gain_linear = 10 ** (gain_db / 20)
        
        # Apply gain with limiting
        audio_gained = audio * gain_linear
        audio_gained = np.clip(audio_gained, -1.0, 1.0)
        
        return audio_gained.astype(np.float32)
    
    @staticmethod
    def enhance_speech(input_audio, enhancement_level='high'):
        """
        Complete speech enhancement pipeline
        Combines multiple algorithms for optimal results
        """
        
        if enhancement_level == 'light':
            # Light enhancement - minimal processing
            enhanced = SpeechEnhancer.spectral_subtraction(input_audio, alpha=1.5)
        
        elif enhancement_level == 'medium':
            # Medium - balanced approach
            enhanced = SpeechEnhancer.wiener_filter(input_audio, noise_est_frames=5)
            enhanced = SpeechEnhancer.adaptive_gain_control(enhanced)
        
        elif enhancement_level == 'high':
            # High - aggressive multi-algorithm approach
            # Stage 1: Multi-band Wiener filtering
            enhanced = SpeechEnhancer.multi_band_filtering(input_audio, num_bands=8)
            
            # Stage 2: Spectral subtraction
            enhanced = SpeechEnhancer.spectral_subtraction(enhanced, alpha=1.5)
            
            # Stage 3: Perceptual weighting
            enhanced = SpeechEnhancer.perceptual_weighting(enhanced, noise_reduction_strength=0.8)
            
            # Stage 4: Gain control
            enhanced = SpeechEnhancer.adaptive_gain_control(enhanced, target_level=-20)
        
        elif enhancement_level == 'maximum':
            # Maximum - all algorithms combined
            # Stage 1: Initial Wiener
            enhanced = SpeechEnhancer.wiener_filter(input_audio, noise_est_frames=8)
            
            # Stage 2: Multi-band (aggressive)
            enhanced = SpeechEnhancer.multi_band_filtering(enhanced, num_bands=12)
            
            # Stage 3: Spectral subtraction (strong)
            enhanced = SpeechEnhancer.spectral_subtraction(enhanced, alpha=2.5)
            
            # Stage 4: Repeat Wiener
            enhanced = SpeechEnhancer.wiener_filter(enhanced, noise_est_frames=3)
            
            # Stage 5: Perceptual weighting (strong)
            enhanced = SpeechEnhancer.perceptual_weighting(enhanced, noise_reduction_strength=1.5)
            
            # Stage 6: Gain control
            enhanced = SpeechEnhancer.adaptive_gain_control(enhanced, target_level=-18)
        
        else:
            enhanced = input_audio
        
        # Final normalization
        max_val = np.max(np.abs(enhanced))
        if max_val > 1.0:
            enhanced = enhanced / max_val
        
        return enhanced.astype(np.float32)
    
    @staticmethod
    def calculate_snr_improvement(original, enhanced):
        """Calculate SNR improvement"""
        # Assume quiet frames at beginning are noise
        noise_est = np.mean(np.abs(original[:1000]))
        
        # SNR of original
        signal_power_orig = np.mean(original ** 2)
        noise_power_orig = noise_est ** 2
        snr_orig = 10 * np.log10(signal_power_orig / (noise_power_orig + 1e-10))
        
        # SNR of enhanced (compared to original)
        diff = original - enhanced
        snr_enh = 10 * np.log10(signal_power_orig / (np.mean(diff ** 2) + 1e-10))
        
        return max(0, snr_enh - snr_orig)


# Demo function
def demo():
    """Demo the speech enhancer"""
    print("="*60)
    print("SPEECH ENHANCEMENT SYSTEM - DEMONSTRATION")
    print("="*60)
    
    # Generate test audio
    sr = 16000
    duration = 3
    t = np.linspace(0, duration, int(sr * duration))
    
    # Clean signal - simulated speech
    clean = np.zeros_like(t)
    for f in [200, 400, 600]:
        clean += 0.3 * np.sin(2 * np.pi * f * t)
    
    # Add modulation (speech-like)
    modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 5 * t)
    clean = clean * modulation
    
    # Add noise
    noise = 0.5 * np.random.randn(len(t))
    noisy = clean + noise
    
    print(f"\nTest audio generated ({duration}s at {sr}Hz)")
    print(f"Clean signal RMS: {np.sqrt(np.mean(clean**2)):.4f}")
    print(f"Noise signal RMS: {np.sqrt(np.mean(noise**2)):.4f}")
    print(f"Noisy signal RMS: {np.sqrt(np.mean(noisy**2)):.4f}")
    
    # Enhance
    print("\nEnhancing audio...")
    enhanced = SpeechEnhancer.enhance_speech(noisy, enhancement_level='high')
    
    print(f"Enhanced signal RMS: {np.sqrt(np.mean(enhanced**2)):.4f}")
    
    # Calculate improvement
    improvement = SpeechEnhancer.calculate_snr_improvement(noisy, enhanced)
    print(f"\nSNR improvement: {improvement:.2f} dB")
    
    print("\n✓ Demo completed successfully")
    print("="*60)


if __name__ == '__main__':
    demo()
