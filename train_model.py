#!/usr/bin/env python3
"""
Training script for DDAE Speech Enhancement Model
This script trains the Deep Denoising Autoencoder model for speech enhancement
"""

import config_params
from DDAE import DDAE, Train
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import matplotlib.pyplot as plt

def main():
    print("=" * 60)
    print("DDAE Speech Enhancement Training")
    print("=" * 60)
    print(f"Model: {config_params.MODEL_NAME}")
    print(f"Noise Class: {config_params.NOISE_CLASS}")
    print(f"Batch Size: {config_params.BATCH_SIZE}")
    print(f"Epochs: {config_params.EPOCH_NUM}")
    print(f"Optimizer: {config_params.OPTIMIZER}")
    print(f"Training from scratch: {config_params.TRAINING_FROM_SCRATCH}")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    train, test = Train().load_data()
    print("Data loaded successfully!")
    
    # Create model
    print(f"\nCreating {config_params.MODEL} model...")
    model = DDAE((129, 126))
    model.summary()
    
    # Set up callbacks
    print("\nSetting up callbacks...")
    checkpoint = ModelCheckpoint(
        filepath=config_params.PATH_WEIGHTS,
        monitor='val_loss',
        verbose=1,
        save_best_only=True,
        save_weights_only=False,
        mode='auto'
    )
    
    earlystopping = EarlyStopping(
        monitor='val_loss',
        patience=20,
        verbose=1,
        restore_best_weights=True
    )
    
    # Train model
    print("\nStarting training...")
    print("=" * 60)
    history = model.fit(
        train,
        validation_data=test,
        epochs=config_params.EPOCH_NUM,
        batch_size=config_params.BATCH_SIZE,
        verbose=1,
        callbacks=[checkpoint, earlystopping],
        shuffle=True
    )
    
    # Plot training history
    print("\nPlotting training history...")
    loss = history.history.get('loss')
    val_loss = history.history.get('val_loss')
    mse = history.history.get('mse')
    val_mse = history.history.get('val_mse')
    
    plt.figure(figsize=(12, 5))
    plt.subplot(121)
    plt.plot(range(len(loss)), loss, label='Training', linewidth=2)
    plt.plot(range(len(val_loss)), val_loss, label='Validation', linewidth=2)
    plt.title('Huber Loss', fontsize=14)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(122)
    plt.plot(range(len(mse)), mse, label='Training', linewidth=2)
    plt.plot(range(len(val_mse)), val_mse, label='Validation', linewidth=2)
    plt.title('MSE Loss', fontsize=14)
    plt.xlabel('Epoch')
    plt.ylabel('MSE')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(config_params.PATH_CURVE, dpi=300, format='png')
    plt.close()
    
    print(f"\nTraining complete!")
    print(f"Model weights saved to: {config_params.PATH_WEIGHTS}")
    print(f"Training curve saved to: {config_params.PATH_CURVE}")
    print("=" * 60)

if __name__ == '__main__':
    main()
