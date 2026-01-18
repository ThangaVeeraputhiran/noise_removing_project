#!/usr/bin/env python
"""
WSGI entry point for Railway deployment - Minimal Production Version
"""
import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the full production app
    from app_production import app, create_directories
    print("✓ Loaded full app_production")
    
    # Create directories on startup
    create_directories()
    
except Exception as e:
    # Fallback to minimal app if production app fails
    print(f"Warning: Could not load full app: {e}")
    print("Starting minimal app...")
    
    from flask import Flask, render_template
    
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['OUTPUT_FOLDER'] = 'outputs'
    app.config['SPECTROGRAMS'] = 'static/spectrograms'
    
    # Create directories
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['SPECTROGRAMS']]:
        os.makedirs(folder, exist_ok=True)
    
    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except:
            return '<h1>Speech Enhancement System</h1><p>App is running</p>'

    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

# The app is ready for WSGI/gunicorn
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


