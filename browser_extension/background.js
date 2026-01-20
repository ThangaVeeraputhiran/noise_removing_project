/**
 * Background Service Worker for AI Speech Enhancement Extension
 */

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('AI Speech Enhancement Extension installed');
        
        // Set default settings
        chrome.storage.sync.set({
            enhancementLevel: 'high',
            apiUrl: 'https://your-app-url.railway.app'
        });
        
        // Open welcome page
        chrome.tabs.create({
            url: 'https://your-app-url.railway.app'
        });
    }
});

// Handle messages from content scripts or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'processAudio') {
        // Handle audio processing request
        processAudioInBackground(request.data)
            .then(result => sendResponse({ success: true, data: result }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Keep channel open for async response
    }
    
    if (request.action === 'getSettings') {
        chrome.storage.sync.get(['enhancementLevel', 'apiUrl'], (result) => {
            sendResponse(result);
        });
        return true;
    }
});

async function processAudioInBackground(data) {
    // Get API URL from settings
    const settings = await chrome.storage.sync.get(['apiUrl']);
    const apiUrl = settings.apiUrl || 'https://your-app-url.railway.app';
    
    // Process audio through API
    const response = await fetch(`${apiUrl}/process`, {
        method: 'POST',
        body: data.formData
    });
    
    if (!response.ok) {
        throw new Error('Processing failed');
    }
    
    return await response.json();
}

// Context menu for right-click on audio/video elements
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: 'enhanceAudio',
        title: 'Enhance Audio with AI',
        contexts: ['audio', 'video']
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'enhanceAudio') {
        // Send message to content script
        chrome.tabs.sendMessage(tab.id, {
            action: 'enhanceMediaElement',
            srcUrl: info.srcUrl
        });
    }
});

// Handle keyboard shortcuts
chrome.commands.onCommand.addListener((command) => {
    if (command === 'open-extension') {
        chrome.action.openPopup();
    }
});
