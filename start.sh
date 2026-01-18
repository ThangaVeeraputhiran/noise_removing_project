#!/bin/bash
# Startup script for Speech Enhancement System Web Application

echo "========================================"
echo "Speech Enhancement System - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 is installed"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install/upgrade requirements
echo ""
echo "Installing/upgrading dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p uploads outputs static/spectrograms sample_audio
echo "✓ Directories created"

# Check for model files
echo ""
echo "Checking for model files..."
if [ ! -d "Integration/model_files" ]; then
    echo "⚠️  Model files directory not found!"
    echo "   Expected: Integration/model_files/"
    echo "   Please ensure pre-trained models are in place."
else
    model_count=$(ls -1 Integration/model_files/*.h5 2>/dev/null | wc -l)
    if [ "$model_count" -gt 0 ]; then
        echo "✓ Found $model_count model file(s)"
    else
        echo "⚠️  No .h5 model files found in Integration/model_files/"
    fi
fi

# Generate sample audio if not exists
echo ""
if [ ! -d "sample_audio" ] || [ -z "$(ls -A sample_audio)" ]; then
    echo "Creating sample audio files for testing..."
    python create_sample_audio.py
else
    echo "✓ Sample audio files already exist"
fi

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Starting Flask web application..."
echo "Access the application at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Start the Flask app
python app.py
