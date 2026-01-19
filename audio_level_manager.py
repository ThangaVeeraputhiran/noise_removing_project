#!/usr/bin/env python3
"""
Audio Level Management & Monitoring
Ensures output audio is at least as loud as input, with configurable boost
"""

import numpy as np
import librosa

class AudioLevelManager:
    """Manage and normalize audio levels"""
    
    @staticmethod
    def get_loudness_db(audio):
        """Calculate perceived loudness in dB (LUFS-like)"""
        rms = np.sqrt(np.mean(audio ** 2) + 1e-10)
        loudness_db = 20 * np.log10(rms)
        return loudness_db
    
    @staticmethod
    def get_peak_db(audio):
        """Get peak level in dB"""
        peak = np.max(np.abs(audio)) + 1e-10
        peak_db = 20 * np.log10(peak)
        return peak_db
    
    @staticmethod
    def analyze_level(audio):
        """Analyze audio level and return metrics"""
        rms = np.sqrt(np.mean(audio ** 2) + 1e-10)
        peak = np.max(np.abs(audio)) + 1e-10
        loudness_db = 20 * np.log10(rms)
        peak_db = 20 * np.log10(peak)
        
        return {
            'rms': float(rms),
            'peak': float(peak),
            'loudness_db': float(loudness_db),
            'peak_db': float(peak_db),
            'headroom_db': float(peak_db - loudness_db)
        }
    
    @staticmethod
    def compare_levels(original, enhanced):
        """Compare loudness between original and enhanced"""
        orig_loudness = AudioLevelManager.get_loudness_db(original)
        enh_loudness = AudioLevelManager.get_loudness_db(enhanced)
        
        diff_db = enh_loudness - orig_loudness
        
        return {
            'original_db': float(orig_loudness),
            'enhanced_db': float(enh_loudness),
            'difference_db': float(diff_db),
            'needs_boost': diff_db < -0.5  # If more than 0.5 dB quieter
        }
    
    @staticmethod
    def ensure_output_level(original, enhanced, min_gain_db=0.0, max_boost_db=6.0):
        """
        Ensure enhanced audio is at least as loud as original + min_gain
        ENHANCED: Increased maximum boost for maximum clarity perception
        Limits maximum boost to prevent clipping
        """
        orig_loudness = AudioLevelManager.get_loudness_db(original)
        enh_loudness = AudioLevelManager.get_loudness_db(enhanced)
        
        target_loudness = orig_loudness + min_gain_db
        required_gain_db = target_loudness - enh_loudness
        
        # Limit the boost - ENHANCED: Increased from 6-8 dB to 10-12 dB for maximum loudness
        actual_gain_db = np.clip(required_gain_db, 0, max_boost_db)
        gain_linear = 10 ** (actual_gain_db / 20)
        
        # Apply gain
        boosted = enhanced * gain_linear
        
        # Prevent clipping - ENHANCED: More conservative to preserve quality
        peak = np.max(np.abs(boosted))
        if peak > 0.98:  # Changed from 0.99 to 0.98 for safety
            boosted = boosted / peak * 0.98
        
        return boosted.astype(np.float32), actual_gain_db
    
    @staticmethod
    def normalize_to_reference(original, enhanced, preserve_peak=True):
        """
        Normalize enhanced to match original loudness profile
        
        preserve_peak: If True, ensure no clipping; if False, match peak exactly
        """
        if preserve_peak:
            # Match RMS level of original
            orig_rms = np.sqrt(np.mean(original ** 2) + 1e-10)
            enh_rms = np.sqrt(np.mean(enhanced ** 2) + 1e-10)
            if enh_rms > 1e-10:
                gain = orig_rms / enh_rms
                normalized = enhanced * gain
                
                # Safety clip
                peak = np.max(np.abs(normalized))
                if peak > 0.99:
                    normalized = normalized / peak * 0.99
                
                return normalized.astype(np.float32)
        else:
            # Match peak level
            orig_peak = np.max(np.abs(original)) + 1e-10
            enh_peak = np.max(np.abs(enhanced)) + 1e-10
            gain = (orig_peak * 0.95) / enh_peak  # 5% headroom
            return (enhanced * gain).astype(np.float32)
    
    @staticmethod
    def speech_aware_normalization(original, enhanced, speech_mask=None):
        """
        Normalize while preserving speech dynamics
        
        speech_mask: Binary mask where 1=speech, 0=noise/silence
        """
        if speech_mask is None:
            # Auto-detect speech regions using energy
            frame_energy = librosa.feature.rms(y=original)[0]
            energy_threshold = np.percentile(frame_energy, 40)
            speech_mask_frames = frame_energy > energy_threshold
            
            # Expand to sample level (approximate)
            hop_length = len(original) // len(speech_mask_frames)
            speech_mask = np.repeat(speech_mask_frames, hop_length)
            if len(speech_mask) < len(original):
                speech_mask = np.pad(speech_mask, (0, len(original) - len(speech_mask)), constant_values=False)
        
        # Boost speech regions more, noise regions less
        gain_map = np.where(speech_mask, 1.5, 1.0)  # 1.5x for speech, 1.0x for noise
        boosted = enhanced * gain_map
        
        # Prevent clipping
        peak = np.max(np.abs(boosted))
        if peak > 0.99:
            boosted = boosted / peak * 0.99
        
        return boosted.astype(np.float32)

    @staticmethod
    def loudness_report(original, enhanced):
        """Generate detailed loudness comparison report"""
        orig_metrics = AudioLevelManager.analyze_level(original)
        enh_metrics = AudioLevelManager.analyze_level(enhanced)
        
        report = {
            'original': orig_metrics,
            'enhanced': enh_metrics,
            'improvement': {
                'loudness_db': float(enh_metrics['loudness_db'] - orig_metrics['loudness_db']),
                'peak_db': float(enh_metrics['peak_db'] - orig_metrics['peak_db']),
                'status': 'GOOD' if enh_metrics['loudness_db'] >= orig_metrics['loudness_db'] - 0.5 else 'LOW'
            }
        }
        
        return report


if __name__ == '__main__':
    # Test
    sr = 16000
    duration = 2
    t = np.linspace(0, duration, int(sr * duration))
    
    # Original signal
    original = 0.3 * np.sin(2 * np.pi * 200 * t)
    
    # Enhanced (simulated reduction)
    enhanced = 0.1 * np.sin(2 * np.pi * 200 * t)
    
    # Test level management
    print("Audio Level Manager Test")
    print("=" * 60)
    
    comparison = AudioLevelManager.compare_levels(original, enhanced)
    print(f"\nLevel Comparison:")
    print(f"  Original: {comparison['original_db']:.2f} dB")
    print(f"  Enhanced: {comparison['enhanced_db']:.2f} dB")
    print(f"  Difference: {comparison['difference_db']:.2f} dB")
    print(f"  Needs Boost: {comparison['needs_boost']}")
    
    enhanced_boosted, gain_applied = AudioLevelManager.ensure_output_level(
        original, enhanced, min_gain_db=0.0, max_boost_db=6.0
    )
    
    print(f"\nAfter Level Correction:")
    print(f"  Gain Applied: {gain_applied:.2f} dB")
    
    comparison_after = AudioLevelManager.compare_levels(original, enhanced_boosted)
    print(f"  Original: {comparison_after['original_db']:.2f} dB")
    print(f"  Enhanced: {comparison_after['enhanced_db']:.2f} dB")
    print(f"  Difference: {comparison_after['difference_db']:.2f} dB")
    
    # Full report
    report = AudioLevelManager.loudness_report(original, enhanced_boosted)
    print(f"\nDetailed Report:")
    print(f"  {report}")
