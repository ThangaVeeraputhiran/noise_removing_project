#!/usr/bin/env python3
"""
AGGRESSIVE SPEECH ENHANCER
Maximum clarity for hard-to-understand noisy speech
Focuses on speech frequency bands and aggressive noise suppression
"""

import numpy as np
import librosa
from scipy import signal as scipy_signal
from scipy.ndimage import median_filter, gaussian_filter1d

class AggressiveSpeechEnhancer:
    """
    Maximum speech clarity enhancement
    Designed for very noisy, hard-to-understand speech
    """
    
    SAMPLE_RATE = 16000
    N_FFT = 2048  # High resolution for speech focus
    HOP_LENGTH = 512
    
    @staticmethod
    def stft(audio, n_fft=2048, hop_length=512):
        """High-res STFT"""
        window = np.hanning(n_fft)
        return librosa.stft(audio, n_fft=n_fft, hop_length=hop_length, window=window)
    
    @staticmethod
    def istft(D, hop_length=512, n_fft=2048, length=None):
        """Inverse STFT"""
        window = np.hanning(n_fft)
        return librosa.istft(D, hop_length=hop_length, window=window, length=length)
    
    @staticmethod
    def speech_frequency_mask(sr=16000, n_fft=2048):
        """
        Create mask emphasizing speech frequencies (80 Hz - 8 kHz)
        ENHANCED: Maximum formant emphasis for exceptional clarity
        """
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        
        # Base: 1.0 everywhere
        mask = np.ones_like(freqs)
        
        # Suppress very low freq (< 80 Hz)
        mask[freqs < 80] = 0.1
        
        # Suppress very high freq (> 8 kHz)
        mask[freqs > 8000] = 0.3
        
        # ENHANCED: Maximum emphasis on primary formant region (800-4000 Hz)
        speech_band = (freqs >= 800) & (freqs <= 4000)
        mask[speech_band] = 3.5  # INCREASED from 2.0 for maximum clarity
        
        # ENHANCED: Extreme emphasis on consonant definition (2-4 kHz)
        consonant_band = (freqs >= 2000) & (freqs <= 4000)
        mask[consonant_band] = 4.0  # NEW: Maximum boost for intelligibility
        
        # ENHANCED: Stronger emphasis on 500-1000 Hz (F1 formant)
        mid_low = (freqs >= 500) & (freqs < 1000)
        mask[mid_low] = 2.5  # INCREASED from 1.5
        
        # NEW: Add sub-200 Hz fundamental boost
        fundamental = (freqs >= 80) & (freqs < 250)
        mask[fundamental] = 2.0  # Voice quality foundation
        
        return mask
    
    @staticmethod
    def adaptive_voice_detection(audio, sr=16000, n_fft=2048, hop_length=512):
        """
        Detect voice activity with multiple features
        Returns: mask (1=voice, 0=noise/silence)
        """
        stft_result = AggressiveSpeechEnhancer.stft(audio, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft_result)
        
        # Feature 1: Energy in speech band
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        speech_band = (freqs >= 80) & (freqs <= 8000)
        speech_energy = np.sum(magnitude[speech_band, :], axis=0)
        
        # Feature 2: Spectral centroid
        centroid = librosa.feature.spectral_centroid(S=magnitude, sr=sr)[0]
        centroid_norm = (centroid - 500) / 3500  # Normalize to [0,1]
        centroid_norm = np.clip(centroid_norm, 0, 1)
        
        # Feature 3: Spectral flatness (speech is harmonic, not flat)
        flatness = np.sum(magnitude, axis=0) / (np.max(magnitude, axis=0) + 1e-10)
        flatness_norm = 1.0 - (flatness / np.max(flatness + 1e-10))
        
        # Feature 4: Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio, hop_length=hop_length)[0]
        zcr_norm = np.clip(zcr / 0.2, 0, 1)
        
        # Combine features
        energy_norm = speech_energy / (np.max(speech_energy) + 1e-10)
        
        # Weighted combination
        vad_score = (
            0.4 * energy_norm +
            0.25 * centroid_norm +
            0.2 * flatness_norm +
            0.15 * zcr_norm
        )
        
        # Smooth
        vad_score = median_filter(vad_score, size=5)
        vad_score = gaussian_filter1d(vad_score, sigma=2)
        
        # Threshold
        threshold = np.percentile(vad_score, 50)
        vad_mask = (vad_score > threshold).astype(float)
        
        return vad_mask, vad_score
    
    @staticmethod
    def ultra_aggressive_denoising(audio, sr=16000):
        """
        Ultra-aggressive noise suppression for hard-to-understand speech
        ENHANCED: Maximum clarity with higher alpha values
        """
        n_fft = 2048
        hop_length = 512
        
        # Get STFT
        stft_result = AggressiveSpeechEnhancer.stft(audio, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft_result)
        phase = np.angle(stft_result)
        
        # Estimate noise (use minimum magnitude across time + percentile filtering)
        noise_spectrum_min = np.min(magnitude, axis=1, keepdims=True)
        noise_spectrum_percentile = np.percentile(magnitude, 2, axis=1, keepdims=True)  # Even lower
        noise_spectrum = np.minimum(noise_spectrum_min, noise_spectrum_percentile)
        noise_spectrum = median_filter(noise_spectrum, size=(15, 1))  # Stronger smoothing
        noise_spectrum = np.maximum(noise_spectrum, np.max(magnitude) * 0.0005)  # Even lower floor
        
        # ENHANCED: Maximum clarity - ultra-aggressive spectral subtraction
        alpha = 12.0  # INCREASED from 8.0 (maximum aggression for clarity)
        beta = 0.00005  # DECREASED from 0.0001 (almost no floor, maximum suppression)
        
        enhanced_mag = magnitude - alpha * noise_spectrum
        enhanced_mag = np.maximum(enhanced_mag, beta * magnitude)
        
        # Reconstruct
        stft_clean = enhanced_mag * np.exp(1j * phase)
        audio_clean = AggressiveSpeechEnhancer.istft(stft_clean, hop_length=hop_length, n_fft=n_fft, length=len(audio))
        
        return audio_clean.astype(np.float32)
    
    @staticmethod
    def speech_band_emphasis(audio, sr=16000):
        """
        Emphasize speech frequencies, suppress noise bands
        """
        n_fft = 2048
        hop_length = 512
        
        stft_result = AggressiveSpeechEnhancer.stft(audio, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft_result)
        phase = np.angle(stft_result)
        
        # Get frequency mask
        freq_mask = AggressiveSpeechEnhancer.speech_frequency_mask(sr=sr, n_fft=n_fft)
        
        # Apply mask
        masked_magnitude = magnitude * freq_mask[:, np.newaxis]
        
        # Reconstruct
        stft_masked = masked_magnitude * np.exp(1j * phase)
        audio_masked = AggressiveSpeechEnhancer.istft(stft_masked, hop_length=hop_length, n_fft=n_fft, length=len(audio))
        
        return audio_masked.astype(np.float32)
    
    @staticmethod
    def vad_gating(audio, sr=16000):
        """
        Voice activity detection gating
        Suppress non-speech regions
        """
        n_fft = 2048
        hop_length = 512
        
        # Get VAD mask
        vad_mask, _ = AggressiveSpeechEnhancer.adaptive_voice_detection(audio, sr=sr, n_fft=n_fft, hop_length=hop_length)
        
        # Expand to sample level with smooth transitions
        vad_samples = np.repeat(vad_mask, hop_length)
        if len(vad_samples) > len(audio):
            vad_samples = vad_samples[:len(audio)]
        elif len(vad_samples) < len(audio):
            vad_samples = np.pad(vad_samples, (0, len(audio) - len(vad_samples)), constant_values=0)
        
        # Smooth transitions
        vad_smooth = gaussian_filter1d(vad_samples, sigma=sr // 100)  # 10ms smoothing
        
        # Apply gate: 0.2 floor in silence (don't kill completely to avoid artifacts)
        gated = audio * (0.2 + 0.8 * vad_smooth)
        
        return gated.astype(np.float32)
    
    @staticmethod
    def multi_stage_aggressive_enhance(audio, sr=16000):
        """
        Multi-stage ultra-aggressive enhancement
        Stage 1: Extreme spectral subtraction
        Stage 2: Speech band emphasis
        Stage 3: Additional spectral subtraction (second pass)
        Stage 4: VAD gating
        Stage 5: Final speech emphasis
        """
        print("Stage 1/5: Ultra-aggressive spectral subtraction...")
        enhanced = AggressiveSpeechEnhancer.ultra_aggressive_denoising(audio, sr=sr)
        
        print("Stage 2/5: Speech frequency emphasis...")
        enhanced = AggressiveSpeechEnhancer.speech_band_emphasis(enhanced, sr=sr)
        
        print("Stage 3/5: Second-pass spectral subtraction...")
        enhanced = AggressiveSpeechEnhancer.ultra_aggressive_denoising(enhanced, sr=sr)
        
        print("Stage 4/5: VAD-based gating...")
        enhanced = AggressiveSpeechEnhancer.vad_gating(enhanced, sr=sr)
        
        print("Stage 5/5: Final speech emphasis...")
        enhanced = AggressiveSpeechEnhancer.speech_band_emphasis(enhanced, sr=sr)
        
        # Normalize
        max_val = np.max(np.abs(enhanced))
        if max_val > 0.99:
            enhanced = enhanced / max_val * 0.99
        
        return enhanced.astype(np.float32)


if __name__ == '__main__':
    print("Aggressive Speech Enhancer loaded")
