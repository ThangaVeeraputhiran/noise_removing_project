/**
 * AI Speech Enhancement - Browser Extension Popup
 */

// Configuration
const API_URL = 'https://your-app-url.railway.app'; // Update with your Railway URL
const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

// State
let selectedFile = null;
let processingData = null;

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const audioFile = document.getElementById('audioFile');
const processBtn = document.getElementById('processBtn');
const captureBtn = document.getElementById('captureBtn');
const enhancementLevel = document.getElementById('enhancementLevel');

const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

const statusText = document.getElementById('statusText');
const errorText = document.getElementById('errorText');
const resultsData = document.getElementById('resultsData');
const enhancedAudio = document.getElementById('enhancedAudio');

const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const retryBtn = document.getElementById('retryBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadSettings();
});

function initializeEventListeners() {
    // File upload
    uploadBox.addEventListener('click', () => audioFile.click());
    
    audioFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFileSelect(file);
    });

    // Process button
    processBtn.addEventListener('click', processAudio);

    // Capture from tab
    captureBtn.addEventListener('click', captureFromTab);

    // Download button
    downloadBtn.addEventListener('click', downloadEnhanced);

    // Reset button
    resetBtn.addEventListener('click', resetUI);

    // Retry button
    retryBtn.addEventListener('click', resetUI);

    // Save settings on change
    enhancementLevel.addEventListener('change', saveSettings);
}

function handleFileSelect(file) {
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
        showError('File size exceeds 100MB limit');
        return;
    }

    // Validate file type
    const validTypes = ['audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/flac', 'audio/x-m4a'];
    const validExtensions = /\.(wav|mp3|ogg|flac|m4a)$/i;
    
    if (!validTypes.includes(file.type) && !validExtensions.test(file.name)) {
        showError('Invalid file type. Please select a valid audio file.');
        return;
    }

    selectedFile = file;

    // Update UI
    uploadBox.innerHTML = `
        <i class="icon-microphone"></i>
        <h3>✅ ${file.name}</h3>
        <p>${(file.size / 1024 / 1024).toFixed(2)} MB</p>
    `;

    processBtn.disabled = false;
}

async function processAudio() {
    if (!selectedFile) {
        showError('Please select a file first');
        return;
    }

    // Show processing
    showSection('processing');
    animateStatus();

    // Create form data
    const formData = new FormData();
    formData.append('audio_file', selectedFile);
    formData.append('enhancement_level', enhancementLevel.value);

    try {
        const response = await fetch(`${API_URL}/process`, {
            method: 'POST',
            body: formData
        });

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Invalid server response');
        }

        const data = await response.json();

        if (response.ok && data.success) {
            processingData = data;
            showResults(data);
        } else {
            throw new Error(data.error || data.message || 'Processing failed');
        }

    } catch (error) {
        console.error('Processing error:', error);
        showError(error.message || 'Failed to process audio. Please try again.');
    }
}

function animateStatus() {
    const statuses = [
        'Analyzing audio...',
        'Classifying noise...',
        'Applying enhancement...',
        'Finalizing...'
    ];

    let index = 0;
    const interval = setInterval(() => {
        if (statusText && index < statuses.length) {
            statusText.textContent = statuses[index];
            index++;
        } else {
            clearInterval(interval);
        }
    }, 1000);

    // Store for cleanup
    window.statusInterval = interval;
}

function showResults(data) {
    // Clear interval
    if (window.statusInterval) {
        clearInterval(window.statusInterval);
    }

    // Display metrics
    resultsData.innerHTML = `
        <div class="metric">
            <span class="metric-label">SNR Improvement</span>
            <span class="metric-value">+${data.snr_improvement} dB</span>
        </div>
        <div class="metric">
            <span class="metric-label">Noise Type</span>
            <span class="metric-value">${formatNoiseType(data.noise_type)}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Confidence</span>
            <span class="metric-value">${data.confidence}%</span>
        </div>
        <div class="metric">
            <span class="metric-label">Duration</span>
            <span class="metric-value">${data.duration}s</span>
        </div>
        ${data.mode ? `
        <div class="metric">
            <span class="metric-label">Processing Mode</span>
            <span class="metric-value">${data.mode}</span>
        </div>
        ` : ''}
    `;

    // Set audio source
    enhancedAudio.src = `${API_URL}${data.download_url}`;

    // Store download URL
    downloadBtn.dataset.url = `${API_URL}${data.download_url}`;
    downloadBtn.dataset.filename = `enhanced_${selectedFile.name.replace(/\.[^/.]+$/, '')}.wav`;

    showSection('results');
}

function downloadEnhanced() {
    const url = downloadBtn.dataset.url;
    const filename = downloadBtn.dataset.filename;

    if (!url) return;

    // Use chrome.downloads API
    chrome.downloads.download({
        url: url,
        filename: filename,
        saveAs: true
    });
}

async function captureFromTab() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        // Inject content script to find audio elements
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: findAudioElements
        });

        if (results && results[0] && results[0].result) {
            const audioUrls = results[0].result;
            
            if (audioUrls.length === 0) {
                showError('No audio elements found on this page');
                return;
            }

            // For now, alert user - full implementation would allow selection
            alert(`Found ${audioUrls.length} audio element(s) on this page. Full capture feature coming soon!`);
        }

    } catch (error) {
        console.error('Capture error:', error);
        showError('Failed to capture audio from tab');
    }
}

function findAudioElements() {
    const audioElements = document.querySelectorAll('audio, video');
    const urls = [];
    
    audioElements.forEach(element => {
        if (element.src) {
            urls.push(element.src);
        }
    });
    
    return urls;
}

function formatNoiseType(type) {
    if (!type) return 'Unknown';
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

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

function showError(message) {
    errorText.textContent = message;
    showSection('error');
}

function resetUI() {
    selectedFile = null;
    processingData = null;
    
    audioFile.value = '';
    processBtn.disabled = true;
    
    uploadBox.innerHTML = `
        <i class="icon-microphone"></i>
        <h3>Select Audio File</h3>
        <p>WAV, MP3, OGG, FLAC (Max 100MB)</p>
    `;
    
    showSection('upload');
}

function saveSettings() {
    chrome.storage.sync.set({
        enhancementLevel: enhancementLevel.value
    });
}

function loadSettings() {
    chrome.storage.sync.get(['enhancementLevel'], (result) => {
        if (result.enhancementLevel) {
            enhancementLevel.value = result.enhancementLevel;
        }
    });
}

// Drag and drop support
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#4F46E5';
    uploadBox.style.background = '#f9fafb';
});

uploadBox.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#667eea';
    uploadBox.style.background = '';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#667eea';
    uploadBox.style.background = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});
