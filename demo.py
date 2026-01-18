#!/usr/bin/env python3
"""
Quick demo script to test a single audio file
This script demonstrates the complete pipeline on a single test file
"""

import os
import numpy as np
import soundfile as sf
import librosa
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
import data_tools

# Configuration
MODEL_PATH = './Training_results/Weights/DDAE_FC_Verbal_Human.h5'
INPUT_AUDIO = './demo_input.wav'  # Place your test audio here
OUTPUT_AUDIO = './demo_output_denoised.wav'

def plot_comparison(clean, noisy, denoised, sr=16000):
    """Plot waveform and spectrogram comparison"""
    fig, axes = plt.subplots(3, 2, figsize=(15, 10))
    
    # Time domain
    time = np.arange(len(clean)) / sr
    axes[0, 0].plot(time, clean)
    axes[0, 0].set_title('Clean Voice - Waveform')
    axes[0, 0].set_xlabel('Time (s)')
    
    axes[1, 0].plot(time[:len(noisy)], noisy)
    axes[1, 0].set_title('Noisy - Waveform')
    axes[1, 0].set_xlabel('Time (s)')
    
    axes[2, 0].plot(time[:len(denoised)], denoised)
    axes[2, 0].set_title('Denoised - Waveform')
    axes[2, 0].set_xlabel('Time (s)')
    
    # Frequency domain (spectrograms)
    D_clean = librosa.stft(clean)
    axes[0, 1].imshow(librosa.amplitude_to_db(np.abs(D_clean), ref=np.max),
                      aspect='auto', origin='lower', cmap='viridis')
    axes[0, 1].set_title('Clean Voice - Spectrogram')
    
    D_noisy = librosa.stft(noisy)
    axes[1, 1].imshow(librosa.amplitude_to_db(np.abs(D_noisy), ref=np.max),
                      aspect='auto', origin='lower', cmap='viridis')
    axes[1, 1].set_title('Noisy - Spectrogram')
    
    D_denoised = librosa.stft(denoised)
    axes[2, 1].imshow(librosa.amplitude_to_db(np.abs(D_denoised), ref=np.max),
                      aspect='auto', origin='lower', cmap='viridis')
    axes[2, 1].set_title('Denoised - Spectrogram')
    
    plt.tight_layout()
    plt.savefig('./demo_comparison.png', dpi=300)
    print("Comparison plot saved to: ./demo_comparison.png")
    plt.close()

def demo():
    print("=" * 60)
    print("Speech Enhancement Demo")
    print("=" * 60)
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model not found: {MODEL_PATH}")
        print("Please train the model first or download pre-trained weights!")
        return
    
    # Check if input exists
    if not os.path.exists(INPUT_AUDIO):
        print(f"❌ Input audio not found: {INPUT_AUDIO}")
        print("Please place a test audio file at this location!")
        print("\nYou can create a test file by recording or using any .wav file")
        return
    
    print(f"\n✓ Loading model from: {MODEL_PATH}")
    model = load_model(MODEL_PATH)
    
    print(f"✓ Loading input audio: {INPUT_AUDIO}")
    audio, sr = librosa.load(INPUT_AUDIO, sr=16000)
    
    print(f"✓ Audio loaded: {len(audio)} samples, {sr} Hz")
    print(f"✓ Duration: {len(audio)/sr:.2f} seconds")
    
    # Process audio
    print("\n⚙️  Processing audio...")
    
    # Split into 1-second chunks
    chunk_size = 16000  # 1 second at 16kHz
    chunks = []
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]
        if len(chunk) == chunk_size:
            chunks.append(chunk)
    
    if len(chunks) == 0:
        print("❌ Audio too short! Need at least 1 second")
        return
    
    print(f"✓ Split into {len(chunks)} chunks")
    
    # Process each chunk
    denoised_chunks = []
    for i, chunk in enumerate(chunks):
        # Convert to spectrogram
        mag_amp_db, mag_phase = data_tools.numpy_audio_to_matrix_spectrogram(
            np.array([chunk]), None
        )
        
        # Normalize
        X_in = data_tools.scaled_in(mag_amp_db)
        
        # Predict
        X_pred = model.predict(X_in, verbose=0)
        
        # Denormalize
        inv_scaled = data_tools.scaled_out(X_pred, mag_amp_db)
        
        # Convert back to audio
        denoised_chunk = data_tools.matrix_spectrogram_to_numpy_audio(
            inv_scaled, mag_phase, len(chunk)
        )
        
        denoised_chunks.append(denoised_chunk[0])
        print(f"  Processed chunk {i+1}/{len(chunks)}")
    
    # Concatenate all chunks
    denoised_audio = np.concatenate(denoised_chunks)
    
    print(f"\n✓ Denoised audio length: {len(denoised_audio)} samples")
    
    # Save output
    sf.write(OUTPUT_AUDIO, denoised_audio, sr, 'PCM_24')
    print(f"✓ Saved denoised audio to: {OUTPUT_AUDIO}")
    
    # Plot comparison if original clean voice is available
    print("\n📊 Generating comparison plots...")
    plot_comparison(audio[:len(denoised_audio)], audio[:len(denoised_audio)], denoised_audio, sr)
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Denoised audio: {OUTPUT_AUDIO}")
    print(f"  - Comparison plot: ./demo_comparison.png")
    print("\nPlay the audio files to hear the difference!")

if __name__ == '__main__':
    try:
        demo()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
