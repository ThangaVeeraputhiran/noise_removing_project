#!/bin/bash
# Script to create the necessary directory structure for the Speech Enhancement System

echo "Creating dataset directory structure..."

# Create main dataset directories
mkdir -p Dataset/Source/Train/Noise/Household_Appliance
mkdir -p Dataset/Source/Train/Noise/TVnRadio
mkdir -p Dataset/Source/Train/Noise/Vechicles
mkdir -p Dataset/Source/Train/Noise/Verbal_Human
mkdir -p Dataset/Source/Train/Voice

mkdir -p Dataset/Source/Test/Noise/Household_Appliance
mkdir -p Dataset/Source/Test/Noise/TVnRadio
mkdir -p Dataset/Source/Test/Noise/Vechicles
mkdir -p Dataset/Source/Test/Noise/Verbal_Human
mkdir -p Dataset/Source/Test/Voice

# Create training output directories (will be auto-created by scripts, but good to have)
mkdir -p Dataset/Train
mkdir -p Dataset/Test

# Create prediction output directories
mkdir -p Predictions

# Create model directories
mkdir -p Training_results/Curve
mkdir -p Training_results/Weights

echo "Directory structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Place your training noise files in Dataset/Source/Train/Noise/<category>/"
echo "2. Place your training voice files in Dataset/Source/Train/Voice/"
echo "3. Place your test noise files in Dataset/Source/Test/Noise/<category>/"
echo "4. Place your test voice files in Dataset/Source/Test/Voice/"
