#!/usr/bin/env python3
"""
Production Flask Web Application for Speech Enhancement System
Full-featured web interface with advanced denoising
"""

import os
import sys
import numpy as np
import librosa
import soundfile as sf
from flask import Flask, request, render_template, send_file, jsonify, url_for
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import traceback
import json

# Import production system
from production_system import AdvancedSpeechEnhancer, NoiseClassifier, AudioProcessor, Logger
from enhanced_speech_processor import EnhancedSpeechProcessor
from ultra_speech_enhancer import UltraSpeechEnhancer
from extreme_noise_eliminator import ExtremeNoiseEliminator

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['SPECTROGRAMS'] = 'static/spectrograms'
app.config['SECRET_KEY'] = 'speech-enhancement-secret-2026'

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/options', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path=None):
    return '', 200
# Create directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['SPECTROGRAMS']]:
    os.makedirs(folder, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_spectrogram_comparison(audio_orig, audio_enh, sr=16000):
    """Create comparison spectrogram"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    
    # Original spectrogram
    D_orig = librosa.stft(audio_orig, n_fft=2048, hop_length=512)
    S_orig_db = librosa.power_to_db(np.abs(D_orig) ** 2, ref=np.max, top_db=80)
    img1 = axes[0, 0].imshow(S_orig_db, aspect='auto', origin='lower', cmap='viridis')
    axes[0, 0].set_title('Original (Noisy) Spectrogram', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('Frequency (Hz)')
    plt.colorbar(img1, ax=axes[0, 0], label='dB')
    
    # Enhanced spectrogram
    D_enh = librosa.stft(audio_enh, n_fft=2048, hop_length=512)
    S_enh_db = librosa.power_to_db(np.abs(D_enh) ** 2, ref=np.max, top_db=80)
    img2 = axes[0, 1].imshow(S_enh_db, aspect='auto', origin='lower', cmap='viridis')
    axes[0, 1].set_title('Enhanced (Denoised) Spectrogram', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('Frequency (Hz)')
    plt.colorbar(img2, ax=axes[0, 1], label='dB')
    
    # Original waveform
    time = np.arange(len(audio_orig)) / sr
    axes[1, 0].plot(time, audio_orig, linewidth=0.5, color='steelblue')
    axes[1, 0].set_title('Original Waveform', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Time (s)')
    axes[1, 0].set_ylabel('Amplitude')
    axes[1, 0].set_ylim([-1, 1])
    
    # Enhanced waveform
    time_enh = np.arange(len(audio_enh)) / sr
    axes[1, 1].plot(time_enh, audio_enh, linewidth=0.5, color='green')
    axes[1, 1].set_title('Enhanced Waveform', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Time (s)')
    axes[1, 1].set_ylabel('Amplitude')
    axes[1, 1].set_ylim([-1, 1])
    
    plt.tight_layout()
    return fig

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/test')
def test():
    """Connection test page"""
    return render_template('test.html')

@app.route('/upload-test')
def upload_test():
    """Upload test page"""
    return render_template('upload_test.html')

@app.route('/process', methods=['POST'])
def process():
    """Process audio file with enhanced algorithm"""
    try:
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['audio_file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Get enhancement level
        enhancement_level = request.form.get('enhancement_level', 'high')
        if enhancement_level not in ['light', 'medium', 'high', 'maximum', 'extreme']:
            enhancement_level = 'high'
        
        # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(input_path)
        
        Logger.log(f"Processing uploaded file: {filename}")
        
        # Load audio
        audio_orig, sr = AudioProcessor.load_audio(input_path)
        
        # Classify noise
        noise_type, confidence, scores = NoiseClassifier.classify(audio_orig, sr)
        Logger.log(f"Noise classified as: {noise_type} ({confidence:.1f}%)")
        
        # Enhance using ULTRA algorithm for maximum cleaning
        Logger.log(f"Enhancing with '{enhancement_level}' profile (ULTRA MODE - Maximum Noise Reduction)...")
        
        if enhancement_level == 'extreme':
            # EXTREME MODE - 100% clean, perfect silence in gaps
            audio_enh = ExtremeNoiseEliminator.extreme_enhance(audio_orig, sr=sr, ensure_perfect_silence=True)
        elif enhancement_level == 'maximum':
            # Use ultra enhancer for maximum level
            audio_enh = UltraSpeechEnhancer.ultra_enhance(audio_orig, sr=sr, intensity='maximum')
        elif enhancement_level == 'high':
            # Use ultra enhancer with high intensity
            audio_enh = UltraSpeechEnhancer.ultra_enhance(audio_orig, sr=sr, intensity='high')
        else:
            # Use enhanced processor for light/medium
            audio_enh = EnhancedSpeechProcessor.enhance(audio_orig, sr=sr, profile=enhancement_level)
        
        # Save output
        output_filename = f"{timestamp}_enhanced.wav"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        AudioProcessor.save_audio(audio_enh, output_path, sr=sr)
        
        # Create spectrogram
        Logger.log("Creating spectrogram comparison...")
        spec_filename = f"{timestamp}_spectrogram.png"
        spec_path = os.path.join(app.config['SPECTROGRAMS'], spec_filename)
        
        fig = create_spectrogram_comparison(audio_orig, audio_enh, sr=sr)
        fig.savefig(spec_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # Calculate SNR improvement using ULTRA method
        if enhancement_level == 'extreme':
            snr_improvement = ExtremeNoiseEliminator.calculate_snr_improvement(audio_orig, audio_enh, sr=sr)
        elif enhancement_level in ['high', 'maximum']:
            snr_improvement = UltraSpeechEnhancer.calculate_snr_improvement(audio_orig, audio_enh, sr=sr)
        else:
            snr_improvement = EnhancedSpeechProcessor.calculate_snr_improvement(audio_orig, audio_enh, sr=sr)
        
        duration = len(audio_enh) / sr
        
        Logger.log(f"Processing complete. SNR improvement: {snr_improvement:.2f} dB")
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'spectrogram': spec_filename,
            'noise_type': noise_type,
            'confidence': f"{confidence:.1f}",
            'snr_improvement': f"{snr_improvement:.2f}",
            'duration': f"{duration:.2f}",
            'enhancement_level': enhancement_level,
            'download_url': url_for('download', filename=output_filename)
        })
    
    except Exception as e:
        Logger.log(f"Error processing: {str(e)}", "ERROR")
        traceback.print_exc()
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/test-upload', methods=['POST'])
def test_upload():
    """Simple test endpoint for file uploads"""
    try:
        if 'audio_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['audio_file']
        return jsonify({
            'success': True,
            'message': 'File received successfully',
            'filename': file.filename,
            'size': len(file.read()) if hasattr(file, 'read') else 0
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    """Download processed audio"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'system': 'Production Speech Enhancement',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/info')
def api_info():
    """API information"""
    return jsonify({
        'name': 'Production Speech Enhancement System',
        'version': '1.0',
        'profiles': ['light', 'medium', 'high', 'maximum'],
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': 100
    })

if __name__ == '__main__':
    print("="*70)
    print("PRODUCTION SPEECH ENHANCEMENT SYSTEM - WEB APPLICATION")
    print("="*70)
    print("\n✓ System initialized successfully")
    print("\nStarting Flask server...")
    print(f"Access at: http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
