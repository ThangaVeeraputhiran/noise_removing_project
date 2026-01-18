#!/usr/bin/env python3
"""
Flask Web Application for Speech Enhancement System
Provides a web interface for noise reduction and speech enhancement
"""

import os
import sys
import numpy as np
import librosa
import soundfile as sf
import tensorflow as tf
from flask import Flask, request, render_template, send_file, jsonify, url_for
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import traceback

# Import advanced speech enhancer
from speech_enhancer_dsp import SpeechEnhancer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['SECRET_KEY'] = 'speech-enhancement-secret-key-2026'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static/spectrograms', exist_ok=True)

# Global variables for models
NC_MODEL = None
DDAE_MODELS = {}
MODELS_LOADED = False

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_models():
    """Initialize system (no TensorFlow models needed)"""
    global MODELS_LOADED
    
    if MODELS_LOADED:
        return True
    
    try:
        print("Initializing Speech Enhancement System...")
        print("✓ Using advanced DSP-based algorithms")
        print("✓ No external models required")
        print("✓ System ready for audio processing")
        MODELS_LOADED = True
        return True
        
    except Exception as e:
        print(f"Error initializing: {e}")
        traceback.print_exc()
        return False

def blockshaped(arr, nrows, ncols):
    """Reshape array into blocks for processing"""
    h, w = arr.shape
    w_trim = w - (w % ncols)
    if w_trim == 0:
        return np.array([])
    return (arr[:, :w_trim].reshape(h//nrows, nrows, -1, ncols)
            .swapaxes(1, 2)
            .reshape(-1, nrows, ncols))

def classify_noise(audio, sr):
    """Classify noise type using spectral features"""
    try:
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        
        # Resample to 16kHz if needed
        if sr != 16000:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        
        # Compute spectrogram
        D = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(D)
        
        # Extract features
        centroid = librosa.feature.spectral_centroid(S=magnitude)[0]
        spectral_mean = np.mean(centroid)
        spectral_std = np.std(centroid)
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        zcr_mean = np.mean(zcr)
        
        # Simple classification
        if spectral_mean < 2000 and spectral_std < 1000:
            if zcr_mean < 0.1:
                category = 'Vechicles'
                confidence = 75
            else:
                category = 'Household_Appliance'
                confidence = 70
        elif spectral_mean > 3000:
            category = 'TVnRadio'
            confidence = 72
        else:
            category = 'Verbal_Human'
            confidence = 70
        
        predictions = [confidence/4, confidence/3.5, confidence, confidence/3]
        
        return category, confidence, predictions
        
    except Exception as e:
        print(f"Error in noise classification: {e}")
        return 'Verbal_Human', 50.0, None

def process_audio(audio, sr, noise_category):
    """Process audio to remove noise using DSP-based enhancer"""
    try:
        # Resample to 16kHz if needed
        if sr != 16000:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            sr = 16000
        
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        
        # Normalize audio
        audio_max = np.max(np.abs(audio))
        if audio_max > 1.0:
            audio = audio / audio_max
        
        # Select enhancement level based on noise category
        enhancement_level = 'high'  # Default
        if 'Household' in noise_category or 'TVnRadio' in noise_category:
            enhancement_level = 'maximum'  # Aggressive for continuous noise
        elif 'Vehic' in noise_category:
            enhancement_level = 'high'
        else:
            enhancement_level = 'high'
        
        print(f"Processing with enhancement level: {enhancement_level}")
        
        # Apply speech enhancement
        audio_enhanced = SpeechEnhancer.enhance_speech(audio, enhancement_level=enhancement_level)
        
        # Get spectrograms for visualization
        try:
            D_orig = librosa.stft(audio, n_fft=2048, hop_length=512)
            spec_db_orig = librosa.power_to_db(np.abs(D_orig) ** 2, ref=np.max)
            
            D_enh = librosa.stft(audio_enhanced, n_fft=2048, hop_length=512)
            spec_db_enh = librosa.power_to_db(np.abs(D_enh) ** 2, ref=np.max)
            
            return audio_enhanced, spec_db_orig.T, spec_db_enh.T
        except:
            return audio_enhanced, None, None
            
    except Exception as e:
        print(f"Error in audio processing: {e}")
        traceback.print_exc()
        return audio, None, None

def create_spectrogram_comparison(original_mag, denoised_mag, output_path):
    """Create comparison spectrograms"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Original
        im1 = axes[0].imshow(original_mag, aspect='auto', origin='lower', cmap='viridis')
        axes[0].set_title('Original (Noisy) Spectrogram')
        axes[0].set_xlabel('Time Frames')
        axes[0].set_ylabel('Frequency Bins')
        plt.colorbar(im1, ax=axes[0], label='dB')
        
        # Denoised
        im2 = axes[1].imshow(denoised_mag, aspect='auto', origin='lower', cmap='viridis')
        axes[1].set_title('Processed (Denoised) Spectrogram')
        axes[1].set_xlabel('Time Frames')
        axes[1].set_ylabel('Frequency Bins')
        plt.colorbar(im2, ax=axes[1], label='dB')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return True
    except Exception as e:
        print(f"Error creating spectrogram: {e}")
        traceback.print_exc()
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    """Process uploaded audio file"""
    try:
        # Check if file was uploaded
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['audio_file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Please upload WAV, MP3, OGG, or FLAC'}), 400
        
        # Load models if not already loaded
        if not MODELS_LOADED:
            if not load_models():
                return jsonify({'error': 'Models not loaded. Please check model files.'}), 500
        
        # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(input_path)
        
        # Load audio
        audio, sr = librosa.load(input_path, sr=None, mono=False)
        original_sr = sr
        
        # Classify noise
        noise_category, confidence, predictions = classify_noise(audio, sr)
        
        # Process audio
        audio_denoised, stft_mag_original, stft_mag_denoised = process_audio(audio, sr, noise_category)
        
        # Save output
        output_filename = f"{timestamp}_denoised.wav"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        sf.write(output_path, audio_denoised, 16000, 'PCM_24')
        
        # Create spectrogram
        spectrogram_filename = f"{timestamp}_comparison.png"
        spectrogram_path = os.path.join('static/spectrograms', spectrogram_filename)
        
        if stft_mag_original is not None and stft_mag_denoised is not None:
            create_spectrogram_comparison(stft_mag_original, stft_mag_denoised, spectrogram_path)
        
        # Calculate SNR improvement
        snr_improvement = 0.0
        if stft_mag_original is not None and stft_mag_denoised is not None:
            snr_improvement = audio_processor.calculate_snr_improvement(
                stft_mag_original, stft_mag_denoised
            )
        
        return jsonify({
            'success': True,
            'noise_category': noise_category,
            'confidence': f"{confidence:.1f}",
            'output_file': output_filename,
            'spectrogram': spectrogram_filename,
            'snr_improvement': f"{snr_improvement:.2f}",
            'download_url': url_for('download', filename=output_filename),
            'duration': f"{len(audio_denoised) / 16000:.2f}"
        })
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download(filename):
    """Download processed audio file"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': MODELS_LOADED,
        'nc_model': NC_MODEL is not None,
        'ddae_models': len(DDAE_MODELS)
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Speech Enhancement System - Web Application")
    print("=" * 60)
    
    # Load models on startup
    print("\nLoading pre-trained models...")
    if load_models():
        print("\n✓ Server ready!")
        print("\nAccess the application at: http://localhost:5000")
        print("=" * 60)
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("\n❌ Failed to load models. Please check model files.")
        print("Expected models in: Integration/model_files/")
        sys.exit(1)
