#!/usr/bin/env python
"""
Ultra-minimal WSGI for Railway - No dependencies
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify

app = Flask(__name__)

# Create directories
for folder in ['uploads', 'outputs', 'static/spectrograms']:
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    """Main page - HTML inline, no templates"""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Speech Enhancement System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .status { color: #28a745; font-weight: bold; }
        .form-group { margin: 15px 0; }
        label { display: block; margin: 5px 0; font-weight: bold; }
        input, select { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        #result { margin-top: 20px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Speech Enhancement System</h1>
        <p class="status">✓ System is running and ready</p>
        
        <div class="form-group">
            <label>Upload Audio File:</label>
            <input type="file" id="audioFile" accept=".wav,.mp3,.ogg,.flac,.m4a">
        </div>
        
        <div class="form-group">
            <label>Enhancement Level:</label>
            <select id="level">
                <option value="light">Light</option>
                <option value="medium">Medium</option>
                <option value="high" selected>High</option>
                <option value="maximum">Maximum</option>
                <option value="extreme">Extreme</option>
            </select>
        </div>
        
        <button onclick="processAudio()">Process Audio</button>
        
        <div id="result"></div>
    </div>
    
    <script>
        async function processAudio() {
            const file = document.getElementById('audioFile').files[0];
            if (!file) {
                alert('Please select a file');
                return;
            }
            
            const formData = new FormData();
            formData.append('audio_file', file);
            formData.append('enhancement_level', document.getElementById('level').value);
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                const result = document.getElementById('result');
                
                if (data.success) {
                    result.innerHTML = `<p style="color: green;">✓ Processing complete!</p><a href="${data.download_url}">Download Enhanced Audio</a>`;
                } else {
                    result.innerHTML = `<p style="color: red;">✗ Error: ${data.error}</p>`;
                }
                result.style.display = 'block';
            } catch (e) {
                document.getElementById('result').innerHTML = `<p style="color: red;">✗ Error: ${e.message}</p>`;
                document.getElementById('result').style.display = 'block';
            }
        }
    </script>
</body>
</html>'''
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/process', methods=['POST'])
def process():
    """Audio processing - lazy load heavy modules"""
    try:
        from flask import request
        from werkzeug.utils import secure_filename
        from datetime import datetime
        import librosa
        import soundfile
        
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No file'}), 400
        
        file = request.files['audio_file']
        if not file.filename:
            return jsonify({'error': 'No filename'}), 400
        
        level = request.form.get('enhancement_level', 'high')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        input_path = f'uploads/{timestamp}_{filename}'
        
        file.save(input_path)
        audio, sr = librosa.load(input_path, sr=16000)
        
        # Import processing modules only when needed
        from enhanced_speech_processor import EnhancedSpeechProcessor
        
        audio_enhanced = EnhancedSpeechProcessor.enhance(audio, sr=sr, profile=level)
        
        output_filename = f"{timestamp}_enhanced.wav"
        soundfile.write(f'outputs/{output_filename}', audio_enhanced, sr)
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'download_url': f'/download/{output_filename}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    from flask import send_file
    try:
        return send_file(f'outputs/{filename}', as_attachment=True)
    except:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)


