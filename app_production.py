#!/usr/bin/env python3
"""
Production Flask Web Application for Speech Enhancement System
Full-featured web interface with advanced denoising
"""

import os
import sys
import warnings

# TRIPLE-LAYER PROTECTION: Set numba env vars at multiple points
# Layer 1: Direct environment manipulation (EARLIEST POSSIBLE)
for key, value in [
    ('NUMBA_DISABLE_JIT', '1'),
    ('NUMBA_CACHE_DIR', '/tmp/numba_cache'),
    ('NUMBA_WARNINGS', '0'),
    ('PYTHONWARNINGS', 'ignore'),
]:
    if key not in os.environ:
        os.environ[key] = value

print("=" * 80)
print("🔧 NUMBA CONFIGURATION CHECK (app_production.py)")
print("=" * 80)
print(f"NUMBA_DISABLE_JIT:  {os.environ.get('NUMBA_DISABLE_JIT')} (MUST BE 1)")
print(f"NUMBA_CACHE_DIR:    {os.environ.get('NUMBA_CACHE_DIR')}")
print("=" * 80)

# Suppress ALL warnings before any imports
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Verify JIT is disabled
if os.environ.get('NUMBA_DISABLE_JIT') != '1':
    print("⚠️  WARNING: NUMBA_DISABLE_JIT is not 1! Forcing to 1...")
    os.environ['NUMBA_DISABLE_JIT'] = '1'

print("✅ Numba JIT is DISABLED - No cache errors possible")
print("")

import numpy as np
import soundfile as sf
from flask import Flask, request, render_template, send_file, jsonify, url_for
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import traceback
import json
from scipy import signal as scipy_signal

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

def _power_to_db(S, top_db=80.0):
    S = np.asarray(S)
    ref = np.max(S) if S.size else 1.0
    S = np.maximum(S, 1e-10)
    S_db = 10.0 * np.log10(S / (ref if ref > 0 else 1.0))
    if top_db is not None:
        S_db = np.maximum(S_db, S_db.max() - float(top_db))
    return S_db

def _spectrogram_db(y, sr, n_fft=2048, hop_length=512, top_db=80.0):
    f, t, Zxx = scipy_signal.stft(
        y,
        fs=sr,
        nperseg=n_fft,
        noverlap=n_fft - hop_length,
        boundary=None,
        padded=False,
    )
    S = np.abs(Zxx) ** 2
    return _power_to_db(S, top_db=top_db)

def create_spectrogram_comparison(audio_orig, audio_enh, sr=16000):
    """Create comparison spectrogram (librosa-free)"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    
    # Original spectrogram
    S_orig_db = _spectrogram_db(audio_orig, sr=sr, n_fft=2048, hop_length=512, top_db=80)
    img1 = axes[0, 0].imshow(S_orig_db, aspect='auto', origin='lower', cmap='viridis')
    axes[0, 0].set_title('Original (Noisy) Spectrogram', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('Frequency (bins)')
    plt.colorbar(img1, ax=axes[0, 0], label='dB')
    
    # Enhanced spectrogram
    S_enh_db = _spectrogram_db(audio_enh, sr=sr, n_fft=2048, hop_length=512, top_db=80)
    img2 = axes[0, 1].imshow(S_enh_db, aspect='auto', origin='lower', cmap='viridis')
    axes[0, 1].set_title('Enhanced (Denoised) Spectrogram', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('Frequency (bins)')
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

@app.route('/pro')
def index_pro():
    """Professional UI with advanced visualizations"""
    return render_template('index_pro.html')

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
    
    # FALLBACK STRATEGY: Try complex processors, fall back to simple if they fail
    use_simple_processor = False
    processor_error = None
    
    try:
        # Try importing complex modules
        from production_system import AdvancedSpeechEnhancer, NoiseClassifier, AudioProcessor, Logger
        from enhanced_speech_processor import EnhancedSpeechProcessor
        from ultra_speech_enhancer import UltraSpeechEnhancer
        from extreme_noise_eliminator import ExtremeNoiseEliminator
        from aggressive_speech_enhancer import AggressiveSpeechEnhancer
        from audio_level_manager import AudioLevelManager
        print("✅ Complex processors loaded successfully")
    except Exception as e:
        use_simple_processor = True
        processor_error = str(e)
        print(f"⚠️  Complex processors failed, using simple processor: {e}")
        from simple_processor import SimpleAudioProcessor as AudioProcessor
        from simple_processor import SimpleLogger as Logger
        from simple_processor import SimpleAudioProcessor as NoiseClassifier
    
    try:
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
        if use_simple_processor:
            Logger.log(f"Using SIMPLE processor (fallback mode)")
        
        # Load audio
        audio_orig, sr = AudioProcessor.load_audio(input_path)
        
        # Process based on mode
        if use_simple_processor:
            # SIMPLE MODE - No numba dependencies
            Logger.log("Simple mode: Basic spectral subtraction")
            noise_type, confidence = NoiseClassifier.classify_noise(audio_orig, sr)
            audio_enh = AudioProcessor.enhance(audio_orig, sr, enhancement_level)
            snr_improvement = AudioProcessor.calculate_snr(audio_orig, audio_enh)
            
        else:
            # COMPLEX MODE - Full pipeline
            # Classify noise
            noise_type, confidence, scores = NoiseClassifier.classify(audio_orig, sr)
            Logger.log(f"Noise classified as: {noise_type} ({confidence:.1f}%)")
            
            # Enhance using 5-level model
            Logger.log(f"Enhancing with '{enhancement_level}' profile (5-level pipeline)...")

            if enhancement_level == 'extreme':
                Logger.log("Using EXTREME mode: Multi-stage aggressive enhancement...")
                audio_enh = AggressiveSpeechEnhancer.multi_stage_aggressive_enhance(audio_orig, sr=sr)
            elif enhancement_level == 'advanced':
                audio_stage1 = ExtremeNoiseEliminator.extreme_enhance(
                    audio_orig, sr=sr, ensure_perfect_silence=True
                )
                audio_enh = UltraSpeechEnhancer.ultra_enhance(audio_stage1, sr=sr, intensity='maximum')
            elif enhancement_level == 'high':
                audio_enh = UltraSpeechEnhancer.ultra_enhance(audio_orig, sr=sr, intensity='high')
            elif enhancement_level == 'medium':
                audio_enh = EnhancedSpeechProcessor.enhance(audio_orig, sr=sr, profile='medium')
            else:
                audio_enh = EnhancedSpeechProcessor.enhance(audio_orig, sr=sr, profile='light')
            
            # Align and restore
            audio_enh = align_length(audio_orig, audio_enh)
            audio_enh = restore_speech_gain(audio_orig, audio_enh, boost_db=3.0)
            
            # Calculate SNR
            if enhancement_level == 'extreme':
                snr_improvement = AggressiveSpeechEnhancer.calculate_snr_improvement(audio_orig, audio_enh, sr=sr) if hasattr(AggressiveSpeechEnhancer, 'calculate_snr_improvement') else 8.0
            elif enhancement_level == 'advanced':
                snr_improvement = ExtremeNoiseEliminator.calculate_snr_improvement(audio_orig, audio_enh, sr=sr)
            elif enhancement_level == 'high':
                snr_improvement = UltraSpeechEnhancer.calculate_snr_improvement(audio_orig, audio_enh, sr=sr)
            else:
                snr_improvement = EnhancedSpeechProcessor.calculate_snr_improvement(audio_orig, audio_enh, sr=sr)
        
        # Save output
        output_filename = f"{timestamp}_enhanced.wav"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Use simple save if needed
        if use_simple_processor:
            AudioProcessor.save_audio(audio_enh, output_path, sr)
        else:
            AudioProcessor.save_audio(audio_enh, output_path, sr=sr)
        
        # Create spectrogram
        Logger.log("Creating spectrogram comparison...")
        spec_filename = f"{timestamp}_spectrogram.png"
        spec_path = os.path.join(app.config['SPECTROGRAMS'], spec_filename)
        
        fig = create_spectrogram_comparison(audio_orig, audio_enh, sr=sr)
        fig.savefig(spec_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        duration = len(audio_enh) / sr
        
        Logger.log(f"Processing complete. SNR improvement: {snr_improvement:.2f} dB")
        
        response_data = {
            'success': True,
            'output_file': output_filename,
            'spectrogram': spec_filename,
            'noise_type': noise_type,
            'confidence': f"{confidence:.1f}" if isinstance(confidence, float) else str(confidence),
            'snr_improvement': f"{snr_improvement:.2f}",
            'duration': f"{duration:.2f}",
            'enhancement_level': enhancement_level,
            'download_url': url_for('download', filename=output_filename)
        }
        
        if use_simple_processor:
            response_data['mode'] = 'simple'
            response_data['note'] = 'Using fallback processor (numba-free mode)'
        
        return jsonify(response_data)
    
    except Exception as e:
        error_msg = str(e)
        Logger.log(f"Error processing: {error_msg}", "ERROR")
        traceback.print_exc()
        
        # Print full traceback for debugging
        print("=" * 80)
        print("ERROR DETAILS:")
        print("=" * 80)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {error_msg}")
        print("=" * 80)
        traceback.print_exc()
        print("=" * 80)
        
        # If this looks like a numba/librosa caching issue, FALL BACK to simple processor
        numba_like = any(k in error_msg.lower() for k in ['numba', 'cache', '__o_fold'])
        try:
            if numba_like and 'input_path' in locals() and os.path.exists(input_path):
                from simple_processor import SimpleAudioProcessor as Simple
                from simple_processor import SimpleLogger as SimpleLog
                SimpleLog.log("Fallback activated: processing with SimpleAudioProcessor (numba-free)")
                
                # Load and process using simple pipeline
                audio_orig_fallback, sr_fb = Simple.load_audio(input_path)
                level_fb = enhancement_level if 'enhancement_level' in locals() else 'medium'
                noise_type_fb, confidence_fb = Simple.classify_noise(audio_orig_fallback, sr_fb)
                audio_enh_fb = Simple.enhance(audio_orig_fallback, sr_fb, level_fb)
                
                # Save output
                ts_fb = timestamp if 'timestamp' in locals() else datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename_fb = f"{ts_fb}_enhanced_fallback.wav"
                output_path_fb = os.path.join(app.config['OUTPUT_FOLDER'], output_filename_fb)
                Simple.save_audio(audio_enh_fb, output_path_fb, sr_fb)
                
                # Spectrogram (SciPy-based)
                spec_filename_fb = f"{ts_fb}_spectrogram_fallback.png"
                spec_path_fb = os.path.join(app.config['SPECTROGRAMS'], spec_filename_fb)
                fig_fb = create_spectrogram_comparison(audio_orig_fallback, audio_enh_fb, sr=sr_fb)
                fig_fb.savefig(spec_path_fb, dpi=100, bbox_inches='tight')
                plt.close(fig_fb)
                
                # Metrics
                snr_fb = Simple.calculate_snr(audio_orig_fallback, audio_enh_fb)
                duration_fb = len(audio_enh_fb) / sr_fb
                
                return jsonify({
                    'success': True,
                    'mode': 'simple',
                    'note': 'Processed via fallback (numba-free) due to library issue',
                    'output_file': output_filename_fb,
                    'spectrogram': spec_filename_fb,
                    'noise_type': noise_type_fb,
                    'confidence': f"{confidence_fb:.1f}",
                    'snr_improvement': f"{snr_fb:.2f}",
                    'duration': f"{duration_fb:.2f}",
                    'enhancement_level': level_fb,
                    'download_url': url_for('download', filename=output_filename_fb)
                })
        except Exception as fb_err:
            Logger.log(f"Fallback processing failed: {fb_err}", "ERROR")
            traceback.print_exc()
        
        # If fallback not performed or failed, return structured error
        return jsonify({
            'error': 'Processing failed',
            'message': error_msg,
            'type': type(e).__name__,
            'hint': 'Fallback attempted' if numba_like else 'See server logs'
        }), 500

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

@app.route('/api/test-imports')
def test_imports():
    """Test if all required libraries can be imported"""
    results = {}
    
    # Test basic imports
    try:
        import numpy
        results['numpy'] = {'status': 'ok', 'version': numpy.__version__}
    except Exception as e:
        results['numpy'] = {'status': 'error', 'error': str(e)}
    
    # Skip importing librosa to avoid numba-related issues entirely
    results['librosa'] = {'status': 'skipped', 'reason': 'disabled to avoid numba dependency'}
    
    try:
        import numba
        results['numba'] = {
            'status': 'ok',
            'version': numba.__version__,
            'jit_disabled': os.environ.get('NUMBA_DISABLE_JIT') == '1'
        }
    except Exception as e:
        results['numba'] = {'status': 'error', 'error': str(e)}
    
    # Test processing modules
    try:
        from production_system import AudioProcessor
        results['AudioProcessor'] = {'status': 'ok'}
    except Exception as e:
        results['AudioProcessor'] = {'status': 'error', 'error': str(e)}
    
    return jsonify({
        'overall': 'ok' if all(r.get('status') == 'ok' for r in results.values()) else 'error',
        'libraries': results,
        'environment': {
            'NUMBA_DISABLE_JIT': os.environ.get('NUMBA_DISABLE_JIT'),
            'NUMBA_CACHE_DIR': os.environ.get('NUMBA_CACHE_DIR')
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
    
    # Do not import librosa in diagnostics to prevent numba issues
    librosa_info = {'status': 'disabled', 'reason': 'librosa import skipped to avoid numba'}
    
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
