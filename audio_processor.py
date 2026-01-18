#!/usr/bin/env python3
"""
Simplified audio processing tools for web application
Optimized for real-time processing
"""

import numpy as np
import librosa
import scipy.signal
import matplotlib.pyplot as plt
import os

def scaled_in(matrix_spec):
    """Normalize input spectrogram for model (scale between -1 and 1)"""
    return (matrix_spec + 46) / 50

def scaled_out(matrix_spec, original):
    """Denormalize model output"""
    return matrix_spec * 50 - 46

def inv_scaled_ou(matrix_spec):
    """Inverse scaling for noise prediction"""
    return matrix_spec * 82 + 6

def process_audio_simple(audio, sr, model, target_sr=16000):
    """
    Simplified audio processing for web interface
    
    Args:
        audio: numpy array of audio samples
        sr: sample rate
        model: trained DDAE model
        target_sr: target sample rate (default 16000)
    
    Returns:
        denoised_audio: cleaned audio
        original_spec: original spectrogram magnitude
        denoised_spec: denoised spectrogram magnitude
    """
    # Convert to mono if needed
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Resample if needed
    if sr != target_sr:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
    
    # Parameters matching the training
    n_fft = 256
    hop_length = 128
    
    # Compute STFT
    stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    mag = np.abs(stft)
    phase = np.angle(stft)
    
    # Convert to dB
    mag_db = librosa.amplitude_to_db(mag, ref=np.max)
    
    # Prepare for model: need (129, 126) blocks
    h, w = mag_db.shape  # Should be (129, time_frames)
    
    # Process in chunks of 126 time frames
    chunk_size = 126
    denoised_chunks = []
    
    num_chunks = w // chunk_size
    
    if num_chunks == 0:
        # Audio too short, pad it
        padding = chunk_size - w
        mag_db_padded = np.pad(mag_db, ((0, 0), (0, padding)), mode='edge')
        mag_db = mag_db_padded
        phase = np.pad(phase, ((0, 0), (0, padding)), mode='edge')
        num_chunks = 1
    
    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size
        
        if end > mag_db.shape[1]:
            break
            
        chunk = mag_db[:, start:end]  # Shape: (129, 126)
        
        # Expand dims for model input
        chunk_input = np.expand_dims(chunk, axis=0)  # Shape: (1, 129, 126)
        
        # Normalize
        chunk_normalized = scaled_in(chunk_input)
        
        # Predict
        try:
            noise_pred = model.predict(chunk_normalized, verbose=0)
            
            # Denormalize
            noise_pred_db = scaled_out(noise_pred[0], chunk)
            
            # Subtract predicted noise
            chunk_denoised = chunk - noise_pred_db
            
            denoised_chunks.append(chunk_denoised)
        except:
            # If prediction fails, use original
            denoised_chunks.append(chunk)
    
    # Reconstruct full spectrogram
    if len(denoised_chunks) > 0:
        mag_db_denoised = np.concatenate(denoised_chunks, axis=1)
    else:
        mag_db_denoised = mag_db
    
    # Trim to original size
    mag_db_denoised = mag_db_denoised[:, :w]
    
    # Convert back to linear scale
    mag_denoised = librosa.db_to_amplitude(mag_db_denoised)
    
    # Reconstruct audio
    stft_denoised = mag_denoised[:mag.shape[0], :mag.shape[1]] * np.exp(1j * phase[:mag.shape[0], :mag.shape[1]])
    audio_denoised = librosa.istft(stft_denoised, hop_length=hop_length, n_fft=n_fft, length=len(audio))
    
    return audio_denoised, mag[:, :mag_db_denoised.shape[1]], mag_denoised

def create_spectrogram_plot(mag_original, mag_denoised, output_path, sr=16000):
    """
    Create comparison spectrogram plot
    
    Args:
        mag_original: original magnitude spectrogram
        mag_denoised: denoised magnitude spectrogram
        output_path: path to save the plot
        sr: sample rate
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Original
    img1 = librosa.display.specshow(
        librosa.amplitude_to_db(mag_original, ref=np.max),
        sr=sr, hop_length=128, x_axis='time', y_axis='hz',
        ax=axes[0], cmap='viridis'
    )
    axes[0].set_title('Original Audio with Noise', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Frequency (Hz)')
    fig.colorbar(img1, ax=axes[0], format='%+2.0f dB')
    
    # Denoised  
    img2 = librosa.display.specshow(
        librosa.amplitude_to_db(mag_denoised, ref=np.max),
        sr=sr, hop_length=128, x_axis='time', y_axis='hz',
        ax=axes[1], cmap='viridis'
    )
    axes[1].set_title('Denoised Audio (Noise Removed)', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Time (s)')
    axes[1].set_ylabel('Frequency (Hz)')
    fig.colorbar(img2, ax=axes[1], format='%+2.0f dB')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def calculate_snr_improvement(mag_original, mag_denoised):
    """Calculate SNR improvement in dB"""
    try:
        # Calculate power
        power_original = np.mean(mag_original ** 2)
        power_denoised = np.mean(mag_denoised ** 2)
        
        # Calculate improvement
        if power_denoised > 0:
            improvement = 10 * np.log10(power_original / power_denoised)
            return max(0, improvement)  # Return 0 if negative
        return 0.0
    except:
        return 0.0
