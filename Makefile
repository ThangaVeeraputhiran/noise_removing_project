# Makefile for Speech Enhancement System

.PHONY: help install setup prepare train predict demo clean test

help:
	@echo "Speech Enhancement System - Available Commands:"
	@echo ""
	@echo "  make install     - Install all dependencies"
	@echo "  make setup       - Create directory structure"
	@echo "  make prepare     - Prepare dataset"
	@echo "  make train       - Train the model"
	@echo "  make predict     - Run prediction on test set"
	@echo "  make demo        - Run demo on single file"
	@echo "  make all         - Run complete pipeline (prepare + train + predict)"
	@echo "  make clean       - Clean generated files"
	@echo "  make test        - Run basic tests"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed!"

setup:
	@echo "Setting up directory structure..."
	chmod +x setup_directories.sh
	./setup_directories.sh
	@echo "✓ Directory structure created!"

prepare:
	@echo "Preparing dataset..."
	python prepare_data.py
	@echo "✓ Dataset prepared!"

train:
	@echo "Training model..."
	python train_model.py
	@echo "✓ Training complete!"

predict:
	@echo "Running prediction..."
	python prediction_denoise.py
	@echo "✓ Prediction complete!"

demo:
	@echo "Running demo..."
	python demo.py
	@echo "✓ Demo complete!"

all: prepare train predict
	@echo "✓ Complete pipeline executed!"

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✓ Cleaned!"

test:
	@echo "Running basic tests..."
	python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
	python -c "import librosa; print('Librosa:', librosa.__version__)"
	python -c "import numpy; print('NumPy:', numpy.__version__)"
	@echo "✓ Basic imports successful!"

# Download sample data (if available)
download-data:
	@echo "Please download dataset from:"
	@echo "https://drive.google.com/file/d/1eiRYFSOqBTPAJabmzAV5s0pQaqCE-OVg/view?usp=sharing"
	@echo "And extract to the root directory"

# Quick start for college project
quickstart: install setup
	@echo ""
	@echo "✓ Setup complete! Next steps:"
	@echo ""
	@echo "1. Download datasets (TIMIT + AudioSet) or use pre-prepared data"
	@echo "2. Place audio files in Dataset/Source/Train/ and Dataset/Source/Test/"
	@echo "3. Run: make prepare"
	@echo "4. Run: make train"
	@echo "5. Run: make predict"
	@echo ""
