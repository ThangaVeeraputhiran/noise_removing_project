#!/usr/bin/env python3
"""
Advanced Audio Processor for Speech Enhancement
Includes proper STFT, denoising, and audio reconstruction
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal as scipy_signal
import warnings

warnings.filterwarnings('ignore')

class AdvancedAudioProcessor:
    """Professional audio processing for speech enhancement"""
    
    # Default parameters
    SAMPLE_RATE = 16000
    N_FFT = 256
    HOP_LENGTH = 128
    WINDOW = 'hann'
    
    @staticmethod
    def load_audio(file_path, sr=16000):
        """Load audio file"""
        try:
            audio, sr_loaded = librosa.load(file_path, sr=sr, mono=True)
            return audio.astype(np.float32), sr
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None, sr
    
    @staticmethod
    def save_audio(audio, file_path, sr=16000):
        """Save audio file"""
        try:
            # Ensure audio is in valid range
            audio = np.clip(audio, -1.0, 1.0)
            sf.write(file_path, audio, sr, subtype='PCM_16')
            return True
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    @staticmethod
    def audio_to_spectrogram(audio, n_fft=256, hop_length=128, window='hann'):
        """
        Convert audio to magnitude and phase spectrograms
        Returns both magnitude (dB) and phase for reconstruction
        """
        # Compute STFT
        stft_matrix = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length, window=window)
        
        # Magnitude and phase
        magnitude = np.abs(stft_matrix)
        phase = np.angle(stft_matrix)
        
        # Convert magnitude to dB
        magnitude_db = librosa.power_to_db(magnitude ** 2, ref=np.max, top_db=80)
        magnitude_db = np.clip(magnitude_db, -80, 0)  # Clip to valid range
        
        return magnitude_db.T.astype(np.float32), phase.T.astype(np.float32), magnitude.T.astype(np.float32)
    
    @staticmethod
    def spectrogram_to_audio(magnitude_db, phase, hop_length=128, window='hann'):
        """
        Convert spectrogram back to audio using phase information
        This preserves the phase, resulting in better quality audio
        """
        # Convert from dB to linear magnitude
        magnitude = np.sqrt(librosa.db_to_power(magnitude_db))
        
        # Reconstruct STFT using magnitude and original phase
        stft_matrix = magnitude.T * np.exp(1j * phase.T)
        
        # Inverse STFT
        audio = librosa.istft(stft_matrix, hop_length=hop_length, window=window)
        
        return audio.astype(np.float32)
    
    @staticmethod
    def spectral_subtraction(noisy_spec_db, alpha=2.0, floor_db=-80):
        """
        Spectral subtraction - subtract noise power from noisy signal
        This removes most of the noise while preserving speech
        """
        # Convert to linear scale
        noisy_mag = librosa.db_to_power(noisy_spec_db)
        
        # Estimate noise spectrum (assuming first few frames are noise)
        noise_frames = min(5, noisy_mag.shape[0] // 4)
        noise_power = np.mean(noisy_mag[:noise_frames], axis=0)
        
        # Spectral subtraction
        clean_power = noisy_mag - alpha * noise_power
        
        # Avoid negative values
        clean_power = np.maximum(clean_power, 10 ** (floor_db / 10))
        
        # Convert back to dB
        clean_spec_db = librosa.power_to_db(clean_power)
        clean_spec_db = np.clip(clean_spec_db, -80, 0)
        
        return clean_spec_db.astype(np.float32)
    
    @staticmethod
    def wiener_filter(noisy_audio, frame_length=2048, hop_length=512, noise_duration=1.0, sr=16000):
        """
        Apply Wiener filter for noise reduction
        More sophisticated than spectral subtraction
        """
        # Get number of noise frames (typically first 0.5-1 second)
        noise_frames_count = int(noise_duration * sr / hop_length)
        
        # Compute STFT
        D = librosa.stft(noisy_audio, n_fft=frame_length, hop_length=hop_length)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Estimate noise power spectrum
        noise_power = np.mean(magnitude[:, :noise_frames_count] ** 2, axis=1, keepdims=True)
        
        # Signal power spectrum
        signal_power = magnitude ** 2
        
        # Wiener filter gain
        gain = np.maximum(0, (signal_power - noise_power) / (signal_power + 1e-8))
        gain = np.sqrt(gain)
        
        # Apply gain
        filtered_magnitude = magnitude * gain
        
        # Reconstruct
        D_filtered = filtered_magnitude * np.exp(1j * phase)
        audio_filtered = librosa.istft(D_filtered, hop_length=hop_length)
        
        return audio_filtered.astype(np.float32)
    
    @staticmethod
    def multi_band_noise_reduction(audio, sr=16000, n_bands=4):
        """
        Divide spectrum into bands and apply different noise reduction per band
        Preserves more speech details than single-band approach
        """
        # Split into bands
        nyquist = sr / 2
        band_edges = np.linspace(0, nyquist, n_bands + 1)
        
        # Apply bandpass filter and denoise each band
        filtered_audio = np.zeros_like(audio)
        
        for i in range(n_bands):
            low_freq = band_edges[i]
            high_freq = band_edges[i + 1]
            
            # Skip DC component
            if low_freq == 0:
                low_freq = 50
            
            # Design bandpass filter
            sos = scipy_signal.butter(4, [low_freq, high_freq], btype='band', 
                                     fs=sr, output='sos')
            
            # Apply bandpass
            band_audio = scipy_signal.sosfilt(sos, audio)
            
            # Apply Wiener filter to this band
            band_denoised = AdvancedAudioProcessor.wiener_filter(
                band_audio, sr=sr, noise_duration=0.5)
            
            filtered_audio += band_denoised
        
        return filtered_audio.astype(np.float32)
    
    @staticmethod
    def adaptive_noise_reduction(audio, sr=16000, smoothing_window=5):
        """
        Adaptive noise reduction that adjusts based on local signal characteristics
        Better preserves speech while removing noise
        """
        # Convert to spectrogram
        D = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Smooth across frequency (reduce noise in frequency domain)
        magnitude_smooth = magnitude.copy()
        for i in range(magnitude.shape[0]):
            magnitude_smooth[i, :] = np.convolve(
                magnitude[i, :], 
                np.ones(smoothing_window) / smoothing_window, 
                mode='same'
            )
        
        # Estimate noise as minimum magnitude across time
        noise_estimate = np.percentile(magnitude, 10, axis=1, keepdims=True)
        
        # Calculate SNR for adaptive gain
        snr = magnitude / (noise_estimate + 1e-8)
        snr_db = 20 * np.log10(snr + 1e-8)
        
        # Adaptive gain based on SNR
        gain = np.tanh(snr_db / 20)  # Smooth gain curve
        gain = np.maximum(gain, 0.1)  # Minimum gain to preserve signal
        
        # Apply gain
        magnitude_denoised = magnitude * gain
        
        # Reconstruct
        D_denoised = magnitude_denoised * np.exp(1j * phase)
        audio_denoised = librosa.istft(D_denoised)
        
        return audio_denoised.astype(np.float32)
    
    @staticmethod
    def process_audio_complete(input_audio, sr=16000, method='combined'):
        """
        Complete audio processing pipeline
        Combines multiple denoising techniques for best results
        """
        if method == 'spectral_subtraction':
            spec_db, phase, _ = AdvancedAudioProcessor.audio_to_spectrogram(input_audio)
            spec_clean = AdvancedAudioProcessor.spectral_subtraction(spec_db)
            output_audio = AdvancedAudioProcessor.spectrogram_to_audio(spec_clean, phase)
        
        elif method == 'wiener':
            output_audio = AdvancedAudioProcessor.wiener_filter(input_audio, sr=sr)
        
        elif method == 'adaptive':
            output_audio = AdvancedAudioProcessor.adaptive_noise_reduction(input_audio, sr=sr)
        
        elif method == 'multiband':
            output_audio = AdvancedAudioProcessor.multi_band_noise_reduction(input_audio, sr=sr)
        
        elif method == 'combined':
            # Use best approach: adaptive + multiband
            output_audio = AdvancedAudioProcessor.adaptive_noise_reduction(input_audio, sr=sr)
            output_audio = AdvancedAudioProcessor.multi_band_noise_reduction(output_audio, sr=sr)
        
        else:
            output_audio = input_audio
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(output_audio))
        if max_val > 1.0:
            output_audio = output_audio / max_val
        
        return output_audio.astype(np.float32)
    
    @staticmethod
    def calculate_snr(clean_audio, noisy_audio):
        """Calculate Signal-to-Noise Ratio in dB"""
        noise = noisy_audio - clean_audio
        signal_power = np.mean(clean_audio ** 2)
        noise_power = np.mean(noise ** 2)
        
        if noise_power < 1e-10:
            return float('inf')
        
        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
        return snr
    
    @staticmethod
    def plot_spectrograms(original, processed, sr=16000, title="Audio Comparison"):
        """Create comparison plot of spectrograms"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Original spectrogram
        D_orig = librosa.stft(original, n_fft=2048)
        S_orig_db = librosa.power_to_db(np.abs(D_orig) ** 2, ref=np.max)
        img1 = librosa.display.specshow(S_orig_db, sr=sr, x_axis='time', y_axis='hz', ax=axes[0, 0])
        axes[0, 0].set_title('Original Audio')
        fig.colorbar(img1, ax=axes[0, 0], format='%+2.0f dB')
        
        # Processed spectrogram
        D_proc = librosa.stft(processed, n_fft=2048)
        S_proc_db = librosa.power_to_db(np.abs(D_proc) ** 2, ref=np.max)
        img2 = librosa.display.specshow(S_proc_db, sr=sr, x_axis='time', y_axis='hz', ax=axes[0, 1])
        axes[0, 1].set_title('Processed Audio')
        fig.colorbar(img2, ax=axes[0, 1], format='%+2.0f dB')
        
        # Waveforms
        time_orig = np.arange(len(original)) / sr
        axes[1, 0].plot(time_orig, original, linewidth=0.5)
        axes[1, 0].set_title('Original Waveform')
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].set_ylabel('Amplitude')
        
        time_proc = np.arange(len(processed)) / sr
        axes[1, 1].plot(time_proc, processed, linewidth=0.5, color='green')
        axes[1, 1].set_title('Processed Waveform')
        axes[1, 1].set_xlabel('Time (s)')
        axes[1, 1].set_ylabel('Amplitude')
        
        plt.tight_layout()
        return fig


# Test function
def test_audio_processor():
    """Test the audio processor"""
    print("Testing Advanced Audio Processor...")
    
    # Generate test audio
    sr = 16000
    duration = 3
    t = np.linspace(0, duration, int(sr * duration))
    
    # Speech signal (multiple frequencies)
    speech = np.sin(2 * np.pi * 200 * t) + 0.5 * np.sin(2 * np.pi * 400 * t)
    
    # Noise
    noise = 0.3 * np.random.randn(len(t))
    
    # Noisy signal
    noisy = speech + noise
    
    # Process
    denoised = AdvancedAudioProcessor.process_audio_complete(noisy, sr=sr, method='combined')
    
    print(f"✓ Denoising successful")
    print(f"  Original length: {len(noisy)} samples")
    print(f"  Processed length: {len(denoised)} samples")


if __name__ == '__main__':
    test_audio_processor()
