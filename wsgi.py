#!/usr/bin/env python
"""
WSGI entry point - Absolute minimum, zero dependencies
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Minimal Flask app
from flask import Flask

app = Flask(__name__)

# Simple route - NO complexity
@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Speech Enhancement System</title>
    <style>
        body { font-family: Arial; margin: 40px; text-align: center; }
        .container { max-width: 600px; margin: 0 auto; background: #f0f0f0; padding: 20px; border-radius: 8px; }
        h1 { color: #333; }
        .status { color: green; font-weight: bold; font-size: 18px; }
        input { padding: 8px; margin: 5px; width: 300px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 4px; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Speech Enhancement System</h1>
        <p class="status">✓ App is LIVE and READY!</p>
        <br>
        <input type="file" id="audio" accept=".wav,.mp3,.ogg,.flac,.m4a">
        <br>
        <select id="level">
            <option value="light">Light</option>
            <option value="medium">Medium</option>
            <option value="high" selected>High</option>
            <option value="maximum">Maximum</option>
            <option value="extreme">Extreme</option>
        </select>
        <br>
        <button onclick="upload()">Process Audio</button>
        <div id="result"></div>
    </div>
    <script>
        async function upload() {
            const file = document.getElementById('audio').files[0];
            if (!file) { alert('Select file'); return; }
            const fd = new FormData();
            fd.append('audio_file', file);
            fd.append('enhancement_level', document.getElementById('level').value);
            try {
                const r = await fetch('/process', { method: 'POST', body: fd });
                const d = await r.json();
                if (d.success) {
                    document.getElementById('result').innerHTML = '<p style="color:green">✓ Done! <a href="' + d.download_url + '">Download</a></p>';
                } else {
                    document.getElementById('result').innerHTML = '<p style="color:red">Error: ' + d.error + '</p>';
                }
            } catch(e) {
                document.getElementById('result').innerHTML = '<p style="color:red">Error: ' + e + '</p>';
            }
        }
    </script>
</body>
</html>''', 200, {'Content-Type': 'text/html'}

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

@app.route('/process', methods=['POST'])
def process():
    """Process audio with advanced noise removal"""
    try:
        from flask import request
        import os
        from datetime import datetime
        
        if 'audio_file' not in request.files:
            return {'error': 'No file'}, 400
        
        file = request.files['audio_file']
        if not file.filename:
            return {'error': 'No filename'}, 400
        
        # Create directories if needed
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('outputs', exist_ok=True)
        
        # Lazy load heavy imports
        import librosa
        import soundfile
        import numpy as np
        from production_system import AdvancedSpeechEnhancer
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        level = request.form.get('enhancement_level', 'medium')
        
        # Map enhancement levels to actual processing
        profile_map = {
            'light': 'light',
            'medium': 'medium',
            'high': 'high',
            'maximum': 'maximum',
            'extreme': 'maximum'  # Extreme uses maximum settings
        }
        
        profile = profile_map.get(level, 'high')
        
        input_path = f'uploads/{timestamp}_{file.filename}'
        file.save(input_path)
        
        # Load audio at 16kHz
        audio, sr = librosa.load(input_path, sr=16000)
        
        # Ensure audio is float32 and normalized
        audio = audio.astype(np.float32)
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        # Apply multi-stage noise removal using production system
        # Stage 1: Wiener filtering
        audio_enhanced = AdvancedSpeechEnhancer.wiener_filter_advanced(audio, sr=16000)
        
        # Stage 2: Spectral subtraction (2-4 iterations based on level)
        iterations = {'light': 1, 'medium': 2, 'high': 3, 'maximum': 4}.get(profile, 3)
        alpha_values = {'light': 1.2, 'medium': 1.8, 'high': 2.5, 'maximum': 3.0}
        alpha = alpha_values.get(profile, 2.5)
        
        for _ in range(iterations):
            audio_enhanced = AdvancedSpeechEnhancer.spectral_subtraction_advanced(
                audio_enhanced, alpha=alpha, sr=16000
            )
        
        # Stage 3: Multi-band processing
        audio_enhanced = AdvancedSpeechEnhancer.multiband_processing(audio_enhanced, sr=16000)
        
        # Stage 4: Post-processing and normalization
        audio_enhanced = AdvancedSpeechEnhancer.post_processing_gain(audio_enhanced, target_db=-20)
        
        # Final safety check - ensure no clipping
        audio_enhanced = np.clip(audio_enhanced, -0.99, 0.99)
        
        # Save output at 16kHz
        output_file = f"{timestamp}_enhanced.wav"
        soundfile.write(f'outputs/{output_file}', audio_enhanced, 16000)
        
        return {
            'success': True,
            'output_file': output_file,
            'download_url': f'/download/{output_file}',
            'message': f'✓ Noise removed ({profile} level)'
        }, 200
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return {'error': f'Processing failed: {error_msg}'}, 500

@app.route('/download/<filename>')
def download(filename):
    from flask import send_file
    try:
        return send_file(f'outputs/{filename}', as_attachment=True)
    except:
        return {'error': 'Not found'}, 404

# Export app for gunicorn/Railway - NO app.run() here!
# Gunicorn will handle running the app on the PORT environment variable
if __name__ == '__main__':
    # Only for local development when not using gunicorn
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🎙️ Starting on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


