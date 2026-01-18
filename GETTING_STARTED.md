# Quick Start Guide for College Project

## 🎯 Project Overview
You've forked a **Speech Enhancement System** that uses Deep Learning to:
- Remove environmental noise from audio
- Enhance speech quality
- Classify different types of noise

This is perfect for a college project on Machine Learning/Deep Learning!

---

## 📋 Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.8+ installed
- [ ] 10GB+ free disk space
- [ ] Internet connection (for downloading dependencies)
- [ ] (Optional) GPU for faster training

---

## 🚀 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
# Install all required Python packages
pip install -r requirements.txt
```

**What gets installed:**
- TensorFlow (Deep Learning framework)
- Librosa (Audio processing)
- NumPy, SciPy (Math operations)
- Matplotlib (Visualization)
- And more...

⏱️ **Time**: 5-10 minutes

---

### Step 2: Create Directory Structure

```bash
# Make the script executable and run it
chmod +x setup_directories.sh
./setup_directories.sh
```

Or use Make:
```bash
make setup
```

**This creates:**
```
Dataset/
├── Source/
│   ├── Train/
│   │   ├── Noise/
│   │   │   ├── Household_Appliance/
│   │   │   ├── TVnRadio/
│   │   │   ├── Vechicles/
│   │   │   └── Verbal_Human/
│   │   └── Voice/
│   └── Test/ (similar structure)
```

⏱️ **Time**: < 1 minute

---

### Step 3: Get Dataset

You have **3 options**:

#### Option A: Download Pre-prepared Dataset (EASIEST ✅)
1. Download from: [Google Drive Link](https://drive.google.com/file/d/1eiRYFSOqBTPAJabmzAV5s0pQaqCE-OVg/view?usp=sharing)
2. Extract to project root directory
3. Skip to Step 4!

⏱️ **Time**: 10-20 minutes (depending on internet)

#### Option B: Use Your Own Audio Files
1. Collect clean voice recordings (.wav format)
2. Collect noise recordings (.wav format)
3. Place in respective folders:
   - Voice → `Dataset/Source/Train/Voice/`
   - Noise → `Dataset/Source/Train/Noise/<category>/`

⏱️ **Time**: Varies

#### Option C: Download Public Datasets
- **Voice**: [TIMIT Dataset](https://catalog.ldc.upenn.edu/LDC93S1) (paid)
- **Noise**: [AudioSet](https://research.google.com/audioset/) (free)

⏱️ **Time**: 1-2 hours

---

### Step 4: Prepare Data

```bash
python prepare_data.py
```

Or:
```bash
make prepare
```

**What this does:**
1. Loads audio files
2. Normalizes volume levels
3. Mixes voice + noise at different SNR levels
4. Generates spectrograms
5. Saves to `.h5` format for training

⏱️ **Time**: 30-60 minutes (depending on dataset size)

**Output:** `Dataset/Train/<NOISE_CLASS>/spectrogram/amp_db.h5`

---

### Step 5: Train the Model

```bash
python train_model.py
```

Or:
```bash
make train
```

**What happens:**
1. Loads prepared dataset
2. Builds DDAE neural network
3. Trains for up to 500 epochs (with early stopping)
4. Saves best model weights
5. Generates training curves

⏱️ **Time**: 
- With GPU: 6-8 hours (FC model)
- Without GPU: 12-24 hours

**Outputs:**
- Model: `Training_results/Weights/DDAE_*.h5`
- Curves: `Training_results/Curve/DDAE_*.png`

**💡 Tip:** You can stop training anytime (Ctrl+C) and use the saved weights!

---

### Step 6: Test the Model

```bash
python prediction_denoise.py
```

Or:
```bash
make predict
```

**What this does:**
1. Loads trained model
2. Processes test audio files
3. Generates denoised output
4. Creates spectrograms for comparison

⏱️ **Time**: 5-15 minutes

**Output:** `Predictions/<NOISE_CLASS>/`

---

## 🎬 Quick Demo

Test on a single audio file:

```bash
# 1. Place your test audio as demo_input.wav
# 2. Run demo
python demo.py
```

This will create:
- `demo_output_denoised.wav` (cleaned audio)
- `demo_comparison.png` (visual comparison)

---

## 🎓 For Your College Submission

### What to Submit:

1. **Code** ✅
   - All Python files (already done!)
   - Configuration files
   - Scripts

2. **Documentation** ✅
   - README.md (overview)
   - SETUP_GUIDE.md (detailed setup)
   - PROJECT_REPORT_TEMPLATE.md (fill this out!)

3. **Results** 📊
   - Training curves from `Training_results/Curve/`
   - Sample spectrograms
   - Before/after audio samples
   - Performance metrics

4. **Presentation** 🎤
   - Use PRESENTATION_OUTLINE.md as guide
   - Include demo video or live demo
   - Explain methodology and results

5. **Report** 📄
   - Use PROJECT_REPORT_TEMPLATE.md
   - Add your analysis
   - Include references

---

## ⚡ Quick Commands Reference

```bash
# Complete pipeline (if you have dataset ready)
make all

# Individual steps
make install    # Install dependencies
make setup      # Create directories
make prepare    # Prepare dataset
make train      # Train model
make predict    # Run prediction
make demo       # Demo on single file

# Utilities
make clean      # Clean temporary files
make test       # Test installation
make help       # Show all commands
```

---

## 🔧 Configuration

Edit `config_params.py` to change:

```python
# Choose noise category
NOISE_CLASS = 'Verbal_Human'  # or 'Household_Appliance', 'Vechicles', 'TVnRadio'

# Choose model architecture
MODEL = "FC"  # or "GRU" (slower but better)

# Training parameters
BATCH_SIZE = 150  # Reduce if out of memory
EPOCH_NUM = 500   # Max epochs (early stopping will stop sooner)
```

---

## ❗ Common Issues & Solutions

### Issue 1: Out of Memory
**Solution:** Reduce `BATCH_SIZE` in config_params.py
```python
BATCH_SIZE = 50  # Instead of 150
```

### Issue 2: No GPU Found
**Solution:** It's OK! Training will use CPU (just slower)

### Issue 3: TensorFlow Not Installing
**Solution:** Try specific version
```bash
pip install tensorflow==2.10.0
```

### Issue 4: Audio Files Not Found
**Solution:** Check file paths and ensure `.wav` format

### Issue 5: Training Too Slow
**Solutions:**
- Use pre-trained weights (download from Integration/model_files/)
- Use FC model instead of GRU
- Reduce dataset size
- Use Google Colab (free GPU!)

---

## 🌟 Tips for Success

1. **Start Small**
   - Use a small dataset first (~100 files)
   - Test the complete pipeline
   - Then scale up

2. **Use Pre-trained Models**
   - Check `Integration/model_files/` for pre-trained weights
   - You can use these for demonstration

3. **Document Everything**
   - Take screenshots of each step
   - Save all outputs
   - Record any errors and solutions

4. **Understand the Code**
   - Read through DDAE.py (model architecture)
   - Understand data_tools.py (preprocessing)
   - Know what each parameter does

5. **Prepare Good Demo**
   - Use clear audio samples
   - Show before/after comparison
   - Explain the improvement

---

## 📊 Expected Results

After completing the project, you should have:

✅ Working speech enhancement system  
✅ Trained model with ~4-5 dB SNR improvement  
✅ Visual spectrograms showing noise reduction  
✅ Training curves showing model learning  
✅ Denoised audio samples  

---

## 🆘 Need Help?

1. Check error messages carefully
2. Read the documentation files
3. Search for the error online
4. Ask your instructor/TA
5. Check original repo issues

---

## 📚 Learning Resources

**To understand the project better:**

1. **Deep Learning Basics**
   - Coursera: Deep Learning Specialization
   - YouTube: 3Blue1Brown Neural Networks

2. **Audio Processing**
   - Librosa documentation
   - Understanding spectrograms

3. **Autoencoders**
   - What are autoencoders?
   - Denoising autoencoders explained

4. **TensorFlow/Keras**
   - Official TensorFlow tutorials
   - Keras documentation

---

## ⏰ Timeline Suggestion

**Week 1:**
- Day 1-2: Setup environment, install dependencies
- Day 3-4: Download and prepare dataset
- Day 5-7: Start training (can run overnight)

**Week 2:**
- Day 1-2: Complete training, run predictions
- Day 3-4: Analyze results, create visualizations
- Day 5-6: Write report
- Day 7: Prepare presentation

**Week 3:**
- Day 1-2: Finalize documentation
- Day 3-4: Practice demo
- Day 5: Final review
- Day 6-7: Buffer for any issues

---

## ✅ Checklist Before Submission

- [ ] Code runs without errors
- [ ] All dependencies listed in requirements.txt
- [ ] README.md is clear and complete
- [ ] Training results are saved
- [ ] Report is complete with your analysis
- [ ] Presentation is ready
- [ ] Demo works
- [ ] All files are organized
- [ ] References are cited
- [ ] Your name/details are added

---

## 🎉 You're All Set!

You now have everything you need to complete this project. Good luck! 🚀

**Remember:** The goal is not just to make it work, but to **understand** how it works!

---

**Last Updated:** January 2026
