# Speech Enhancement System - Setup Guide

## Project Overview
This project implements a Deep Learning-based Speech Enhancement System that can:
1. **Classify environmental noise** using a Noise Classifier (NC)
2. **Reduce noise and enhance speech** using a Deep Denoising Autoencoder (DDAE)

The system is designed to help hearing aid users by adapting to different environmental noise types.

## Noise Categories
- **Household Appliances**: Vacuum cleaners, washing machines, etc.
- **TV/Radio**: Television and radio sounds
- **Vehicles**: Car engines, traffic noise
- **Verbal Human**: Human speech noise (conversations, etc.)

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Directory Structure
```bash
chmod +x setup_directories.sh
./setup_directories.sh
```

### 3. Prepare Dataset
You need two types of audio data:
- **Clean Voice**: TIMIT dataset or similar clean speech recordings
- **Noise**: AudioSet or custom environmental noise recordings

Place files in:
```
Dataset/Source/Train/Noise/<category>/  # Training noise files
Dataset/Source/Train/Voice/             # Training voice files
Dataset/Source/Test/Noise/<category>/   # Testing noise files
Dataset/Source/Test/Voice/              # Testing voice files
```

**Note**: You can download sample datasets from:
- TIMIT: [https://catalog.ldc.upenn.edu/LDC93S1](https://catalog.ldc.upenn.edu/LDC93S1)
- AudioSet: [https://research.google.com/audioset/](https://research.google.com/audioset/)
- Pre-prepared dataset: [Google Drive Link](https://drive.google.com/file/d/1eiRYFSOqBTPAJabmzAV5s0pQaqCE-OVg/view?usp=sharing)

### 4. Run the Complete Pipeline
```bash
# Run everything: prepare data, train model, and predict
python run.py --mode all

# Or run steps individually:
python run.py --mode prepare  # Prepare dataset
python run.py --mode train    # Train model
python run.py --mode predict  # Run prediction
```

## Manual Step-by-Step Process

### Step 1: Configure Parameters
Edit [config_params.py](config_params.py) to set:
- `NOISE_CLASS`: Choose which noise category to train ('Household_Appliance', 'TVnRadio', 'Vechicles', 'Verbal_Human')
- `MODEL`: Choose architecture ('FC' for Fully Connected or 'GRU' for Recurrent)
- `BATCH_SIZE`, `EPOCH_NUM`, etc.

### Step 2: Prepare Data
```bash
python prepare_data.py
```
This script will:
- Load and normalize audio files
- Mix clean voice with noise at various SNR levels
- Generate spectrograms
- Save preprocessed data to `.h5` format

### Step 3: Train the Model
```bash
python train_model.py
# OR
python DDAE.py
```
This will:
- Load the prepared dataset
- Build the DDAE model
- Train the model
- Save weights to `Training_results/Weights/`
- Save training curves to `Training_results/Curve/`

### Step 4: Test/Predict
```bash
python prediction_denoise.py
```
This will:
- Load the trained model
- Process test audio files
- Generate denoised output
- Save results with spectrograms

## Project Structure
```
Speech-Enhancement-System/
├── config_params.py          # Configuration parameters
├── data_tools.py             # Audio processing utilities
├── prepare_data.py           # Dataset preparation script
├── DDAE.py                   # Model definition and training
├── train_model.py            # Standalone training script
├── prediction_denoise.py     # Inference script
├── run.py                    # Quick start script
├── requirements.txt          # Python dependencies
├── setup_directories.sh      # Directory setup script
├── Dataset/                  # Dataset directory
│   ├── Source/              # Raw audio files
│   ├── Train/               # Processed training data
│   └── Test/                # Processed test data
├── Training_results/         # Training outputs
│   ├── Curve/               # Training curves
│   └── Weights/             # Model weights
├── Predictions/              # Prediction outputs
└── Integration/              # Integration scripts
```

## Model Architectures

### DDAE - Fully Connected (FC)
- 5 Dense layers with 500 units each
- BatchNormalization and Dropout
- Suitable for faster training

### DDAE - GRU (Recurrent)
- 10 GRU layers with varying units
- Better for sequential audio data
- Higher accuracy but slower training

## Key Parameters

### Audio Processing
- `SAMPLE_RATE`: 16000 Hz
- `N_FFT`: 256 (FFT size)
- `HOP_LENGTH_FFT`: 128
- `TARGET_dBFS`: -30.0 (normalization level)

### Training
- `BATCH_SIZE`: 150 (FC) or 53 (GRU)
- `EPOCH_NUM`: 500
- `OPTIMIZER`: Adam
- Loss: Huber Loss

## Expected Results

### Training
- The model will learn to denoise audio at various SNR levels (-10dB to 15dB)
- Training curves show decreasing loss over epochs
- Best model is automatically saved

### Prediction
- Input: Noisy audio (voice + environmental noise)
- Output: Denoised audio with enhanced speech
- Visual: Spectrograms showing noise reduction

## Troubleshooting

### Out of Memory
- Reduce `BATCH_SIZE` in [config_params.py](config_params.py)
- Use 'FC' model instead of 'GRU'

### No Audio Files Found
- Ensure `.wav` files are in correct directories
- Check file paths in [config_params.py](config_params.py)

### Model Not Training
- Check if `.h5` dataset file exists
- Verify TensorFlow GPU is available (optional)
- Check data shapes match model input

## Integration

The [Integration/](Integration/) folder contains scripts for:
- Model inference with pre-trained weights
- Noise classification
- VGGish-based preprocessing
- Integration with the complete pipeline

## Pre-trained Models
Pre-trained model weights are available in:
- `Training_results/Weights/` (your trained models)
- `Integration/model_files/` (pre-trained models for integration)

## For College Project Submission

### What to Include:
1. **Code**: All Python scripts
2. **Documentation**: This SETUP_GUIDE.md and README.md
3. **Results**: 
   - Training curves from `Training_results/Curve/`
   - Sample denoised audio files
   - Spectrograms showing before/after comparison
4. **Report**: Explain the methodology, architecture, and results
5. **Presentation**: Demo video or slides

### Key Points to Explain:
- Problem: Hearing aid users struggle with environmental noise
- Solution: Deep learning-based adaptive noise reduction
- Dataset: TIMIT (voice) + AudioSet (noise)
- Model: Deep Denoising Autoencoder (DDAE)
- Results: Show SNR improvements and spectrogram comparisons

## References
- Original Paper: Deep Denoising Autoencoder
- TIMIT Dataset: Texas Instruments/MIT corpus
- AudioSet: Google's audio event dataset
- VGGish: Audio feature extraction

## License
This project is for educational purposes.

## Contact
For questions and issues, refer to the original repository or your instructor.
