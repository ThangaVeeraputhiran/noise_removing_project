// Speech Enhancement System - Frontend JavaScript

// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const audioFileInput = document.getElementById('audioFile');
const fileNameDisplay = document.getElementById('fileName');
const processBtn = document.getElementById('processBtn');

const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

let uploadedFile = null;
let uploadedFileURL = null;

// File input change handler
audioFileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        uploadedFile = file;
        fileNameDisplay.textContent = file.name;
        processBtn.disabled = false;
        
        // Create URL for original audio preview
        if (uploadedFileURL) {
            URL.revokeObjectURL(uploadedFileURL);
        }
        uploadedFileURL = URL.createObjectURL(file);
    } else {
        fileNameDisplay.textContent = 'Choose Audio File';
        processBtn.disabled = true;
    }
});

// Form submission handler
uploadForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!uploadedFile) {
        showError('Please select an audio file');
        return;
    }
    
    // Show processing section
    showSection('processing');
    
    // Create FormData
    const formData = new FormData();
    formData.append('audio_file', uploadedFile);
    
    // Get enhancement level from dropdown
    const enhancementLevel = document.getElementById('enhancementLevel').value;
    formData.append('enhancement_level', enhancementLevel);
    
    console.log('Enhancement level:', enhancementLevel);
    
    try {
        // Send request to server
        console.log('Starting file upload...');
        const response = await fetch('/process', {
            method: 'POST',
            body: formData,
            timeout: 300000 // 5 minute timeout
        });
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Invalid response type:', contentType);
            showError('Server error: Invalid response. Please check console.');
            return;
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (response.ok && data.success) {
            // Show results
            displayResults(data);
        } else {
            showError(data.error || 'Processing failed: ' + (data.message || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Fetch error:', error);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        showError('Processing error: ' + error.message + '. Check browser console for details.');
    }
});

// Display results
function displayResults(data) {
    console.log('Displaying results with data:', data);
    
    try {
        // Set audio players
        const originalAudio = document.getElementById('originalAudio');
        const enhancedAudio = document.getElementById('enhancedAudio');
        
        originalAudio.src = uploadedFileURL;
        enhancedAudio.src = data.download_url;
        
        // Set audio info
        document.getElementById('originalInfo').textContent = `File: ${uploadedFile.name}`;
        document.getElementById('enhancedInfo').textContent = `Duration: ${data.duration}s | Format: WAV`;
        
        // Set metrics with safety checks
        const noiseCategory = data.noise_type || data.noise_category || 'Unknown';
        document.getElementById('noiseCategory').textContent = formatNoiseCategory(noiseCategory);
        document.getElementById('confidence').textContent = `${data.confidence}%`;
        document.getElementById('snrImprovement').textContent = `${data.snr_improvement} dB`;
        document.getElementById('duration').textContent = `${data.duration}s`;
        
        // Set spectrogram
        const spectrogramImage = document.getElementById('spectrogramImage');
        if (data.spectrogram) {
            spectrogramImage.src = `/static/spectrograms/${data.spectrogram}?t=${Date.now()}`;
        }
        
        // Set download button
        const downloadBtn = document.getElementById('downloadBtn');
        downloadBtn.href = data.download_url;
        if (uploadedFile && uploadedFile.name) {
            downloadBtn.download = `enhanced_${uploadedFile.name.replace(/\.[^/.]+$/, '')}.wav`;
        }
        
        // Show results section
        showSection('results');
    } catch (error) {
        console.error('Error displaying results:', error);
        showError('Error displaying results: ' + error.message);
    }
}

// Format noise category for display
function formatNoiseCategory(category) {
    if (!category) return 'Unknown';
    if (typeof category !== 'string') return String(category);
    const formatted = category.replace(/_/g, ' ');
    return formatted.charAt(0).toUpperCase() + formatted.slice(1);
}

// Show specific section
function showSection(section) {
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    switch(section) {
        case 'upload':
            uploadSection.classList.remove('hidden');
            break;
        case 'processing':
            processingSection.classList.remove('hidden');
            break;
        case 'results':
            resultsSection.classList.remove('hidden');
            break;
        case 'error':
            errorSection.classList.remove('hidden');
            break;
    }
}

// Show error message
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    showSection('error');
}

// Reset to upload section
function resetUpload() {
    // Clear file input
    audioFileInput.value = '';
    fileNameDisplay.textContent = 'Choose Audio File';
    processBtn.disabled = true;
    uploadedFile = null;
    
    // Revoke object URL
    if (uploadedFileURL) {
        URL.revokeObjectURL(uploadedFileURL);
        uploadedFileURL = null;
    }
    
    // Show upload section
    showSection('upload');
}

// Drag and drop support (bonus feature)
const uploadBox = document.querySelector('.upload-box');

uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = 'var(--primary-dark)';
    uploadBox.style.backgroundColor = 'rgba(79, 70, 229, 0.05)';
});

uploadBox.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = 'var(--primary-color)';
    uploadBox.style.backgroundColor = '';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = 'var(--primary-color)';
    uploadBox.style.backgroundColor = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        // Check if it's an audio file
        if (file.type.startsWith('audio/') || 
            file.name.match(/\.(wav|mp3|ogg|flac)$/i)) {
            audioFileInput.files = files;
            audioFileInput.dispatchEvent(new Event('change'));
        } else {
            showError('Please drop a valid audio file');
        }
    }
});

// Add smooth scroll animation
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

// Console welcome message
console.log('%c🎤 Speech Enhancement System', 'font-size: 20px; font-weight: bold; color: #4F46E5;');
console.log('%cPowered by Deep Learning & TensorFlow', 'font-size: 12px; color: #6B7280;');
