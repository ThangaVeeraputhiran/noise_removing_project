#!/usr/bin/env python
"""
WSGI entry point for Railway - BULLETPROOF VERSION
Minimal imports, maximum reliability
"""
import os
import sys

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[WSGI] Starting initialization...")

# STEP 1: Create Flask app with minimal configuration
print("[WSGI] Creating Flask app...")
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# STEP 2: Create required directories
print("[WSGI] Creating directories...")
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], 'static/spectrograms']:
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception as e:
        print(f"[WSGI] Warning: Could not create {folder}: {e}")

# STEP 3: Define routes
print("[WSGI] Setting up routes...")

@app.route('/')
def index():
    """Main page"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"[WSGI] Error rendering index: {e}")
        return '<h1>Speech Enhancement System</h1><p>App is running</p>', 200

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'speech-enhancement'}), 200

@app.route('/process', methods=['POST'])
def process():
    """Audio processing endpoint - lazy loads heavy dependencies"""
    try:
        from flask import request
        
        # Lazy import heavy modules only when needed
        from app_production import (
            AudioProcessor, NoiseClassifier, 
            EnhancedSpeechProcessor, UltraSpeechEnhancer, ExtremeNoiseEliminator,
            Logger
        )
        from werkzeug.utils import secure_filename
        from datetime import datetime
        import librosa
        import numpy as np
        
        print("[PROCESS] Audio file received")
        
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['audio_file']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get enhancement level
        enhancement_level = request.form.get('enhancement_level', 'high')
        if enhancement_level not in ['light', 'medium', 'high', 'maximum', 'extreme']:
            enhancement_level = 'high'
        
        # Save upload
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(input_path)
        
        print(f"[PROCESS] Processing: {filename} with {enhancement_level} level")
        
        # Load audio
        audio, sr = librosa.load(input_path, sr=16000)
        
        # Process based on level
        if enhancement_level == 'extreme':
            audio_enhanced = ExtremeNoiseEliminator.extreme_enhance(audio, sr=sr)
        elif enhancement_level == 'maximum':
            audio_enhanced = UltraSpeechEnhancer.ultra_enhance(audio, sr=sr, intensity='maximum')
        else:
            audio_enhanced = EnhancedSpeechProcessor.enhance(audio, sr=sr, profile=enhancement_level)
        
        # Save output
        output_filename = f"{timestamp}_enhanced.wav"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        import soundfile
        soundfile.write(output_path, audio_enhanced, sr)
        
        print(f"[PROCESS] Success: saved to {output_filename}")
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'enhancement_level': enhancement_level,
            'duration': f"{len(audio_enhanced) / sr:.2f}s",
            'download_url': f'/download/{output_filename}'
        }), 200
        
    except Exception as e:
        print(f"[PROCESS] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download(filename):
    """Download processed audio"""
    from flask import send_file
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

print("[WSGI] ✓ All routes configured")
print("[WSGI] ✓ App is ready!")

# Entry point for gunicorn
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"[WSGI] Starting server on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


