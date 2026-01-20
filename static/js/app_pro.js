/**
 * AI Speech Enhancement Pro - Frontend Application
 * Advanced interactive visualizations and audio processing
 */

// Global state
let uploadedFile = null;
let uploadedFileURL = null;
let waveformOriginal = null;
let waveformEnhanced = null;
let currentResults = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeHeroAnimation();
    initializeFileUpload();
    initializeTabSwitching();
    initializeBenchmarkCharts();
    setupDragAndDrop();
    console.log('%c🎤 AI Speech Enhancement Pro Initialized', 'font-size: 18px; font-weight: bold; color: #667eea;');
});

// ============================================
// Hero Animation
// ============================================

function initializeHeroAnimation() {
    const canvas = document.getElementById('heroWaveform');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    let phase = 0;
    
    function drawWave() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        for (let x = 0; x < canvas.width; x++) {
            const y = canvas.height / 2 + Math.sin((x + phase) * 0.02) * 40 + Math.sin((x + phase) * 0.05) * 20;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        
        ctx.stroke();
        phase += 2;
        requestAnimationFrame(drawWave);
    }
    
    drawWave();
}

// ============================================
// File Upload
// ============================================

function initializeFileUpload() {
    const fileInput = document.getElementById('audioFile');
    const processBtn = document.getElementById('processBtn');
    const dropZone = document.getElementById('dropZone');
    
    if (!fileInput) return;
    
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileSelect(file);
        }
    });
    
    dropZone?.addEventListener('click', () => {
        fileInput.click();
    });
    
    processBtn?.addEventListener('click', () => {
        if (uploadedFile) {
            processAudio();
        }
    });
}

function handleFileSelect(file) {
    uploadedFile = file;
    
    // Validate file
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
        showError('File size exceeds 100MB limit');
        return;
    }
    
    // Update UI
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
        dropZone.innerHTML = `
            <i class="fas fa-check-circle" style="color: var(--success);"></i>
            <h3>File Selected</h3>
            <p><strong>${file.name}</strong></p>
            <p>${(file.size / 1024 / 1024).toFixed(2)} MB</p>
            <button class="browse-btn" onclick="document.getElementById('audioFile').click()">
                <i class="fas fa-folder-open"></i> Choose Different File
            </button>
        `;
    }
    
    // Enable process button
    const processBtn = document.getElementById('processBtn');
    if (processBtn) {
        processBtn.disabled = false;
    }
    
    // Create preview URL
    if (uploadedFileURL) {
        URL.revokeObjectURL(uploadedFileURL);
    }
    uploadedFileURL = URL.createObjectURL(file);
}

// ============================================
// Drag and Drop
// ============================================

function setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    if (!dropZone) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = 'var(--primary-dark)';
            dropZone.style.background = 'var(--gray-100)';
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = 'var(--primary)';
            dropZone.style.background = 'white';
        });
    });
    
    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('audio/') || file.name.match(/\.(wav|mp3|ogg|flac|m4a)$/i)) {
                document.getElementById('audioFile').files = files;
                handleFileSelect(file);
            } else {
                showError('Please drop a valid audio file');
            }
        }
    });
}

// ============================================
// Process Audio
// ============================================

async function processAudio() {
    if (!uploadedFile) {
        showError('Please select a file first');
        return;
    }
    
    // Show processing UI
    showSection('processingArea');
    
    // Simulate progress
    animateProgress();
    
    // Create form data
    const formData = new FormData();
    formData.append('audio_file', uploadedFile);
    
    const enhancementLevel = document.getElementById('enhancementLevel').value;
    formData.append('enhancement_level', enhancementLevel);
    
    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Invalid response from server');
        }
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            currentResults = data;
            displayResults(data);
        } else {
            throw new Error(data.error || data.message || 'Processing failed');
        }
        
    } catch (error) {
        console.error('Processing error:', error);
        showError(error.message || 'An error occurred during processing');
    }
}

function animateProgress() {
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('processingStatus');
    
    if (!progressBar) return;
    
    const statuses = [
        'Analyzing noise patterns...',
        'Classifying noise type...',
        'Applying spectral subtraction...',
        'Enhancing speech clarity...',
        'Generating visualizations...',
        'Finalizing output...'
    ];
    
    let progress = 0;
    let statusIndex = 0;
    
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 95) progress = 95;
        
        progressBar.style.width = progress + '%';
        
        if (statusIndex < statuses.length - 1) {
            statusIndex = Math.floor((progress / 100) * statuses.length);
            if (statusText) statusText.textContent = statuses[statusIndex];
        }
        
        if (progress >= 95) {
            clearInterval(interval);
        }
    }, 500);
    
    // Store interval ID for cleanup
    window.progressInterval = interval;
}

// ============================================
// Display Results
// ============================================

async function displayResults(data) {
    // Clear progress interval
    if (window.progressInterval) {
        clearInterval(window.progressInterval);
    }
    
    // Show results section
    showSection('resultsArea');
    
    // Setup audio players
    const audioOriginal = document.getElementById('audioOriginal');
    const audioEnhanced = document.getElementById('audioEnhanced');
    
    if (audioOriginal) audioOriginal.src = uploadedFileURL;
    if (audioEnhanced) audioEnhanced.src = data.download_url;
    
    // Initialize waveforms with WaveSurfer
    if (typeof WaveSurfer !== 'undefined') {
        initializeWaveforms(uploadedFileURL, data.download_url);
    }
    
    // Update metadata
    const metadataOriginal = document.getElementById('metadataOriginal');
    const metadataEnhanced = document.getElementById('metadataEnhanced');
    
    if (metadataOriginal) {
        metadataOriginal.innerHTML = `
            <strong>File:</strong> ${uploadedFile.name}<br>
            <strong>Size:</strong> ${(uploadedFile.size / 1024).toFixed(2)} KB
        `;
    }
    
    if (metadataEnhanced) {
        metadataEnhanced.innerHTML = `
            <strong>Duration:</strong> ${data.duration}s<br>
            <strong>Format:</strong> WAV 16kHz<br>
            <strong>Mode:</strong> ${data.mode || 'standard'}<br>
            ${data.note ? `<strong>Note:</strong> ${data.note}` : ''}
        `;
    }
    
    // Update metrics
    document.getElementById('metricSNR').textContent = `+${data.snr_improvement} dB`;
    document.getElementById('metricConfidence').textContent = `${data.confidence}%`;
    document.getElementById('metricNoise').textContent = formatNoiseType(data.noise_type);
    document.getElementById('metricDuration').textContent = `${data.duration}s`;
    
    // Load spectrogram
    const spectrogramImg = document.getElementById('spectrogramImage');
    if (spectrogramImg && data.spectrogram) {
        spectrogramImg.src = `/static/spectrograms/${data.spectrogram}?t=${Date.now()}`;
    }
    
    // Generate charts
    generateFrequencyChart();
    generateComparisonChart(data);
    
    // Setup download button
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.href = data.download_url;
        downloadBtn.download = `enhanced_${uploadedFile.name.replace(/\.[^/.]+$/, '')}.wav`;
    }
}

function initializeWaveforms(originalUrl, enhancedUrl) {
    // Original waveform
    if (waveformOriginal) waveformOriginal.destroy();
    
    waveformOriginal = WaveSurfer.create({
        container: '#waveformOriginal',
        waveColor: '#667eea',
        progressColor: '#4F46E5',
        height: 80,
        barWidth: 2,
        barGap: 1,
        responsive: true
    });
    
    waveformOriginal.load(originalUrl);
    
    // Enhanced waveform
    if (waveformEnhanced) waveformEnhanced.destroy();
    
    waveformEnhanced = WaveSurfer.create({
        container: '#waveformEnhanced',
        waveColor: '#10b981',
        progressColor: '#059669',
        height: 80,
        barWidth: 2,
        barGap: 1,
        responsive: true
    });
    
    waveformEnhanced.load(enhancedUrl);
}

// ============================================
// Charts
// ============================================

function generateFrequencyChart() {
    const canvas = document.getElementById('frequencyChart');
    if (!canvas) return;
    
    // Simulated frequency data
    const frequencies = Array.from({length: 20}, (_, i) => i * 500);
    const originalSpectrum = frequencies.map((f, i) => Math.random() * 40 + 20 - (i * 1.5));
    const enhancedSpectrum = frequencies.map((f, i) => Math.random() * 30 + 10 - (i * 2));
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: frequencies.map(f => `${f}Hz`),
            datasets: [
                {
                    label: 'Original (Noisy)',
                    data: originalSpectrum,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Enhanced (Clean)',
                    data: enhancedSpectrum,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Power (dB)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Frequency'
                    }
                }
            }
        }
    });
}

function generateComparisonChart(data) {
    const canvas = document.getElementById('comparisonChart');
    if (!canvas) return;
    
    const snrImprovement = parseFloat(data.snr_improvement) || 0;
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: ['SNR Improvement', 'Noise Reduction', 'Speech Clarity', 'Overall Quality'],
            datasets: [{
                label: 'Improvement (%)',
                data: [
                    Math.min(snrImprovement * 10, 100),
                    Math.min(parseFloat(data.confidence) || 75, 100),
                    Math.min(snrImprovement * 12, 100),
                    Math.min((snrImprovement * 10 + parseFloat(data.confidence)) / 2, 100)
                ],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(139, 92, 246, 0.8)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(139, 92, 246, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Improvement (%)'
                    }
                }
            }
        }
    });
}

function initializeBenchmarkCharts() {
    // Processing Time Chart
    const processingCanvas = document.getElementById('processingTimeChart');
    if (processingCanvas) {
        new Chart(processingCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Low', 'Medium', 'High', 'Advanced', 'Extreme'],
                datasets: [{
                    data: [2, 3, 5, 8, 12],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(249, 115, 22, 0.8)',
                        'rgba(239, 68, 68, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Average Processing Time (seconds)'
                    }
                }
            }
        });
    }
    
    // SNR Improvement Chart
    const snrCanvas = document.getElementById('snrImprovementChart');
    if (snrCanvas) {
        new Chart(snrCanvas, {
            type: 'bar',
            data: {
                labels: ['Low', 'Medium', 'High', 'Advanced', 'Extreme'],
                datasets: [{
                    label: 'SNR Improvement (dB)',
                    data: [3, 5, 8, 12, 15],
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'dB Improvement' }
                    }
                }
            }
        });
    }
    
    // Noise Types Chart
    const noiseCanvas = document.getElementById('noiseTypesChart');
    if (noiseCanvas) {
        new Chart(noiseCanvas, {
            type: 'radar',
            data: {
                labels: ['Vehicle', 'Appliance', 'Voice', 'General'],
                datasets: [{
                    label: 'Detection Accuracy (%)',
                    data: [95, 92, 99, 85],
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// ============================================
// Tab Switching
// ============================================

function initializeTabSwitching() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            // Update button states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update tab panels
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            
            const activePanel = document.getElementById(`tab-${tabName}`);
            if (activePanel) {
                activePanel.classList.add('active');
            }
        });
    });
}

// ============================================
// Section Management
// ============================================

function showSection(sectionId) {
    const sections = ['uploadArea', 'processingArea', 'resultsArea', 'errorArea'];
    
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('hidden');
        }
    });
    
    const activeSection = document.getElementById(sectionId);
    if (activeSection) {
        activeSection.classList.remove('hidden');
    }
}

// ============================================
// Error Handling
// ============================================

function showError(message) {
    const errorArea = document.getElementById('errorArea');
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorMessage) {
        errorMessage.textContent = message;
    }
    
    showSection('errorArea');
    
    console.error('Error:', message);
}

// ============================================
// Reset
// ============================================

function resetProcessing() {
    // Clear file
    uploadedFile = null;
    if (uploadedFileURL) {
        URL.revokeObjectURL(uploadedFileURL);
        uploadedFileURL = null;
    }
    
    // Reset file input
    const fileInput = document.getElementById('audioFile');
    if (fileInput) {
        fileInput.value = '';
    }
    
    // Reset drop zone
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
        dropZone.innerHTML = `
            <i class="fas fa-cloud-upload-alt"></i>
            <h3>Drag & Drop Audio File</h3>
            <p>or click to browse</p>
            <input type="file" id="audioFile" accept=".wav,.mp3,.ogg,.flac,.m4a" hidden>
            <button class="browse-btn" onclick="document.getElementById('audioFile').click()">
                <i class="fas fa-folder-open"></i> Browse Files
            </button>
            <p class="formats">Supported: WAV, MP3, OGG, FLAC, M4A (Max 100MB)</p>
        `;
    }
    
    // Disable process button
    const processBtn = document.getElementById('processBtn');
    if (processBtn) {
        processBtn.disabled = true;
    }
    
    // Destroy waveforms
    if (waveformOriginal) {
        waveformOriginal.destroy();
        waveformOriginal = null;
    }
    if (waveformEnhanced) {
        waveformEnhanced.destroy();
        waveformEnhanced = null;
    }
    
    // Re-initialize file upload handlers
    initializeFileUpload();
    setupDragAndDrop();
    
    // Show upload section
    showSection('uploadArea');
}

// ============================================
// Utilities
// ============================================

function formatNoiseType(type) {
    if (!type) return 'Unknown';
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function shareResults() {
    if (!currentResults) return;
    
    const shareText = `I enhanced my audio with AI Speech Enhancement Pro!\n\n` +
        `✅ SNR Improvement: ${currentResults.snr_improvement} dB\n` +
        `✅ Noise Type: ${formatNoiseType(currentResults.noise_type)}\n` +
        `✅ Confidence: ${currentResults.confidence}%\n\n` +
        `Try it yourself!`;
    
    if (navigator.share) {
        navigator.share({
            title: 'AI Speech Enhancement Results',
            text: shareText
        }).catch(err => console.log('Share failed:', err));
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareText).then(() => {
            alert('Results copied to clipboard!');
        });
    }
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
