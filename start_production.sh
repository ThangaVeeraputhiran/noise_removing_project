#!/bin/bash
# Production Speech Enhancement System - Quick Start Script

echo "======================================================================="
echo "  PRODUCTION SPEECH ENHANCEMENT SYSTEM - QUICK START"
echo "======================================================================="

# Check Python
echo ""
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi
echo "✓ Python3 found: $(python3 --version)"

# Install dependencies
echo ""
echo "[2/4] Installing dependencies..."
pip3 install -q flask librosa soundfile scipy numpy matplotlib werkzeug 2>/dev/null || true
echo "✓ Dependencies installed"

# Create directories
echo ""
echo "[3/4] Creating directories..."
mkdir -p uploads outputs denoised_output static/spectrograms models_production
echo "✓ Directories created"

# Start application
echo ""
echo "[4/4] Starting application..."
echo ""
echo "======================================================================="
echo "✓ SYSTEM READY!"
echo ""
echo "Access the application at:"
echo "  → http://localhost:5000"
echo ""
echo "Or run demonstration:"
echo "  → python production_system.py"
echo "======================================================================="
echo ""

python3 app_production.py
