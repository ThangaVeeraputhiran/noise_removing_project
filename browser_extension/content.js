/**
 * Content Script for AI Speech Enhancement
 * Runs on all web pages to detect and enhance audio elements
 */

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'enhanceMediaElement') {
        enhanceMediaElement(request.srcUrl);
    }
});

// Add enhancement button to audio/video players
function addEnhancementButtons() {
    const mediaElements = document.querySelectorAll('audio, video');
    
    mediaElements.forEach((element, index) => {
        // Skip if button already added
        if (element.dataset.enhancementAdded) return;
        
        element.dataset.enhancementAdded = 'true';
        
        // Create enhancement button
        const button = document.createElement('button');
        button.className = 'ai-enhance-btn';
        button.innerHTML = '🎤 AI Enhance';
        button.title = 'Enhance audio quality with AI';
        
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            enhanceMediaElement(element.src || element.currentSrc);
        });
        
        // Insert button near the element
        element.parentElement.insertBefore(button, element.nextSibling);
    });
}

async function enhanceMediaElement(srcUrl) {
    if (!srcUrl) {
        alert('No audio source found');
        return;
    }
    
    try {
        // Show loading indicator
        showLoadingIndicator();
        
        // Download the audio file
        const response = await fetch(srcUrl);
        const blob = await response.blob();
        
        // Convert to File object
        const file = new File([blob], 'audio.mp3', { type: blob.type });
        
        // Send to background for processing
        chrome.runtime.sendMessage({
            action: 'processAudio',
            data: { file: file }
        }, (response) => {
            hideLoadingIndicator();
            
            if (response.success) {
                // Replace the audio source with enhanced version
                replaceAudioSource(response.data.download_url);
            } else {
                alert('Enhancement failed: ' + response.error);
            }
        });
        
    } catch (error) {
        console.error('Error enhancing media:', error);
        alert('Failed to enhance audio: ' + error.message);
        hideLoadingIndicator();
    }
}

function replaceAudioSource(newSrc) {
    // Find the current playing element and replace its source
    const currentElement = document.querySelector('audio:not([data-enhanced]), video:not([data-enhanced])');
    
    if (currentElement) {
        currentElement.src = newSrc;
        currentElement.dataset.enhanced = 'true';
        currentElement.load();
        
        // Add visual indicator
        addEnhancedBadge(currentElement);
    }
}

function addEnhancedBadge(element) {
    const badge = document.createElement('div');
    badge.className = 'ai-enhanced-badge';
    badge.innerHTML = '✨ AI Enhanced';
    element.parentElement.insertBefore(badge, element);
}

function showLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'ai-enhance-loading';
    indicator.className = 'ai-loading-indicator';
    indicator.innerHTML = `
        <div class="ai-loading-content">
            <div class="ai-spinner"></div>
            <p>Enhancing audio with AI...</p>
        </div>
    `;
    document.body.appendChild(indicator);
}

function hideLoadingIndicator() {
    const indicator = document.getElementById('ai-enhance-loading');
    if (indicator) {
        indicator.remove();
    }
}

// Run on page load and when DOM changes
const observer = new MutationObserver(() => {
    addEnhancementButtons();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Initial run
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addEnhancementButtons);
} else {
    addEnhancementButtons();
}
