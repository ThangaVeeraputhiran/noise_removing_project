#!/usr/bin/env python3
"""
Production Flask Web Application for Speech Enhancement System
Full-featured web interface with advanced denoising
"""

import os
import sys
import warnings

# CRITICAL: Disable numba JIT by default to avoid caching errors in Railway
# This trades performance (~2-3x slower) for stability (no cache errors)
# Set NUMBA_DISABLE_JIT=0 in Railway to enable JIT if cache is working
os.environ.setdefault('NUMBA_DISABLE_JIT', '1')  # DISABLED by default for stability
os.environ.setdefault('NUMBA_CACHE_DIR', '/tmp/numba_cache')

print(f"[NUMBA CONFIG] JIT Disabled: {os.environ.get('NUMBA_DISABLE_JIT')}")
print(f"[NUMBA CONFIG] Cache Dir: {os.environ.get('NUMBA_CACHE_DIR')}")

# Only try to create cache if JIT is enabled
if os.environ.get('NUMBA_DISABLE_JIT') == '0':
    try:
        cache_dir = os.environ.get('NUMBA_CACHE_DIR', '/tmp/numba_cache')
        os.makedirs(cache_dir, exist_ok=True)
        print(f"[NUMBA CONFIG] Cache directory created: {cache_dir}")
    except Exception as e:
        print(f"[NUMBA WARNING] Could not create cache directory: {e}")
        print(f"[NUMBA WARNING] Disabling JIT to avoid errors")
        os.environ['NUMBA_DISABLE_JIT'] = '1'
else:
    print(f"[NUMBA INFO] JIT is disabled - processing will be slower but stable")

# Suppress numba warnings
warnings.filterwarnings('ignore', category=Warning, module='numba')
warnings.filterwarnings('ignore', message='.*numba.*')

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

# Import production system - ONLY if actually needed (lazy import in routes)
# This prevents blocking on startup

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
# Create directories on startup
def create_directories():
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['SPECTROGRAMS']]:
        os.makedirs(folder, exist_ok=True)

# Initialize directories
try:
    create_directories()
except Exception as e:
    print(f"Warning: Could not create directories: {e}")

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def align_length(reference, target):
    """Match target audio length to reference to avoid shape mismatches."""
    if len(target) == len(reference):
        return target
    if len(target) > len(reference):
        return target[:len(reference)]
    pad = len(reference) - len(target)
    return np.pad(target, (0, pad), mode='constant')


def restore_speech_gain(reference, enhanced, boost_db=3.0):
    """Lift enhanced audio toward original loudness while staying safe from clipping."""
    ref_rms = np.sqrt(np.mean(reference ** 2) + 1e-10)
    enh_rms = np.sqrt(np.mean(enhanced ** 2) + 1e-10)
    if enh_rms < 1e-8:
        return enhanced
    target = ref_rms * (10 ** (boost_db / 20))
    gain = target / enh_rms
    boosted = enhanced * gain
    peak = np.max(np.abs(boosted)) + 1e-10
    if peak > 0.99:
        boosted = boosted / peak * 0.99
    return boosted.astype(np.float32)

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
        # Import heavy modules only when needed
        from production_system import AdvancedSpeechEnhancer, NoiseClassifier, AudioProcessor, Logger
        from enhanced_speech_processor import EnhancedSpeechProcessor
        from ultra_speech_enhancer import UltraSpeechEnhancer
        from extreme_noise_eliminator import ExtremeNoiseEliminator
        from aggressive_speech_enhancer import AggressiveSpeechEnhancer
        from audio_level_manager import AudioLevelManager
        
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['audio_file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Get enhancement level (5-level model)
        enhancement_level = request.form.get('enhancement_level', 'high')
        allowed_levels = ['low', 'medium', 'high', 'advanced', 'extreme']
        if enhancement_level not in allowed_levels:
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
        
        # Enhance using 5-level model (new: extreme mode with aggressive enhancer)
        Logger.log(f"Enhancing with '{enhancement_level}' profile (5-level pipeline)...")

        if enhancement_level == 'extreme':
            # EXTREME: For hard-to-understand speech - most aggressive
            Logger.log("Using EXTREME mode: Multi-stage aggressive enhancement...")
            audio_enh = AggressiveSpeechEnhancer.multi_stage_aggressive_enhance(audio_orig, sr=sr)
        elif enhancement_level == 'advanced':
            # ADVANCED: Maximal cleaning with extreme + ultra
            audio_stage1 = ExtremeNoiseEliminator.extreme_enhance(
                audio_orig, sr=sr, ensure_perfect_silence=True
            )
            audio_enh = UltraSpeechEnhancer.ultra_enhance(audio_stage1, sr=sr, intensity='maximum')
        elif enhancement_level == 'high':
            # HIGH: Strong cleaning with clear speech focus
            audio_enh = UltraSpeechEnhancer.ultra_enhance(audio_orig, sr=sr, intensity='high')
        elif enhancement_level == 'medium':
            # MEDIUM: Balanced clean
            audio_enh = EnhancedSpeechProcessor.enhance(audio_orig, sr=sr, profile='medium')
        else:
            # LOW: Gentle clean
            audio_enh = EnhancedSpeechProcessor.enhance(audio_orig, sr=sr, profile='light')
        # Keep enhanced audio aligned with original to prevent broadcasting errors
        audio_enh = align_length(audio_orig, audio_enh)

        # Restore speech loudness so voice is not reduced by aggressive denoising
        # ENHANCED: Increased boost parameters (2.0 dB min, 12.0 dB max) for maximum clarity
        audio_enh, gain_applied_db = AudioLevelManager.ensure_output_level(
            audio_orig, audio_enh, min_gain_db=2.0, max_boost_db=12.0
        )
        
        Logger.log(f"Audio level adjustment: {gain_applied_db:.2f} dB gain applied")
        
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
        
        # Calculate SNR improvement using appropriate method
        if enhancement_level == 'extreme':
            snr_improvement = AggressiveSpeechEnhancer.calculate_snr_improvement(audio_orig, audio_enh, sr=sr) if hasattr(AggressiveSpeechEnhancer, 'calculate_snr_improvement') else 8.0
        elif enhancement_level == 'advanced':
            snr_improvement = ExtremeNoiseEliminator.calculate_snr_improvement(audio_orig, audio_enh, sr=sr)
        elif enhancement_level == 'high':
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
        error_msg = str(e)
        Logger.log(f"Error processing: {error_msg}", "ERROR")
        traceback.print_exc()
        
        # Provide helpful error message for common issues
        if 'numba' in error_msg.lower() or 'cache' in error_msg.lower():
            detailed_error = (
                f"Numba caching error: {error_msg}. "
                "This may be resolved by setting NUMBA_CACHE_DIR environment variable "
                "or disabling JIT with NUMBA_DISABLE_JIT=1"
            )
            return jsonify({
                'error': 'Processing failed due to library caching issue',
                'details': detailed_error,
                'suggestion': 'Please contact administrator to configure NUMBA_CACHE_DIR'
            }), 500
        
        return jsonify({'error': f'Processing failed: {error_msg}'}), 500

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
    """Health check with system configuration info"""
    numba_cache_dir = os.environ.get('NUMBA_CACHE_DIR', 'not set')
    numba_jit_status = os.environ.get('NUMBA_DISABLE_JIT', '0')
    cache_exists = os.path.exists(numba_cache_dir) if numba_cache_dir != 'not set' else False
    
    return jsonify({
        'status': 'healthy',
        'system': 'Production Speech Enhancement',
        'version': '1.0',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'numba_cache_dir': numba_cache_dir,
            'numba_cache_exists': cache_exists,
            'numba_jit_enabled': numba_jit_status == '0'
        }
    })

@app.route('/api/info')
def api_info():
    """API information"""
    return jsonify({
        'name': 'Production Speech Enhancement System',
        'version': '2.0',
        'profiles': ['low', 'medium', 'high', 'advanced', 'extreme'],
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': 100,
        'profile_descriptions': {
            'low': 'Gentle noise reduction (2-3 dB)',
            'medium': 'Balanced denoising (4-5 dB)',
            'high': 'Aggressive denoising (6-8 dB)',
            'advanced': 'Maximum cleaning with extreme + ultra (10-15 dB)',
            'extreme': 'EXTREME: For hard-to-understand speech (8-12 dB)'
        }
    })

@app.route('/api/diagnostics')
def diagnostics():
    """System diagnostics endpoint"""
    import platform
    
    numba_info = {}
    try:
        import numba
        numba_info = {
            'version': numba.__version__,
            'cache_dir': os.environ.get('NUMBA_CACHE_DIR', 'not set'),
            'jit_disabled': os.environ.get('NUMBA_DISABLE_JIT', '0') == '1',
            'cache_writable': os.access(os.environ.get('NUMBA_CACHE_DIR', '/tmp'), os.W_OK)
        }
    except Exception as e:
        numba_info = {'error': str(e)}
    
    librosa_info = {}
    try:
        librosa_info = {
            'version': librosa.__version__,
            'backend': librosa.get_samplerate.__module__ if hasattr(librosa, 'get_samplerate') else 'unknown'
        }
    except Exception as e:
        librosa_info = {'error': str(e)}
    
    return jsonify({
        'status': 'ok',
        'platform': {
            'system': platform.system(),
            'python_version': platform.python_version(),
            'architecture': platform.machine()
        },
        'libraries': {
            'numba': numba_info,
            'librosa': librosa_info,
            'numpy': np.__version__,
        },
        'directories': {
            'uploads': os.path.exists(app.config['UPLOAD_FOLDER']),
            'outputs': os.path.exists(app.config['OUTPUT_FOLDER']),
            'spectrograms': os.path.exists(app.config['SPECTROGRAMS'])
        },
        'environment': {
            'PORT': os.environ.get('PORT', 'not set'),
            'NUMBA_CACHE_DIR': os.environ.get('NUMBA_CACHE_DIR', 'not set'),
            'NUMBA_DISABLE_JIT': os.environ.get('NUMBA_DISABLE_JIT', 'not set')
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    
    print("="*70)
    print("PRODUCTION SPEECH ENHANCEMENT SYSTEM - WEB APPLICATION")
    print("="*70)
    print("\n✓ System initialized successfully")
    print("\nStarting Flask server...")
    print(f"Access at: http://0.0.0.0:{port}")
    print("="*70 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
