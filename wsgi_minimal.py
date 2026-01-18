#!/usr/bin/env python
"""
Minimal test app for Railway
"""
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Speech Enhancement System</title></head>
    <body>
        <h1>✓ Speech Enhancement System is Running</h1>
        <p>The app is successfully deployed on Railway!</p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
