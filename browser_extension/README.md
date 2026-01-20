# AI Speech Enhancement Pro - Browser Extension

Transform noisy audio into crystal-clear speech directly in your browser!

## 🎤 Features

- **One-Click Enhancement**: Enhance any audio file with a single click
- **5 Processing Levels**: From gentle cleanup to extreme clarity
- **Real-time Processing**: Fast AI-powered noise removal
- **In-Browser Integration**: Enhance audio elements directly on web pages
- **Privacy-Focused**: All processing happens on our secure servers
- **Download Enhanced Audio**: Save improved audio files instantly

## 📦 Installation

### Chrome/Edge

1. Download or clone this repository
2. Open Chrome/Edge and go to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked"
5. Select the `browser_extension` folder
6. The extension icon will appear in your toolbar!

### Firefox

1. Download or clone this repository
2. Open Firefox and go to `about:debugging#/runtime/this-firefox`
3. Click "Load Temporary Add-on"
4. Select the `manifest.json` file from the `browser_extension` folder
5. The extension is now active!

## 🚀 Usage

### Method 1: Upload Files

1. Click the extension icon in your browser toolbar
2. Click "Select Audio File" or drag and drop an audio file
3. Choose your enhancement level (Low, Medium, High, Advanced, or Extreme)
4. Click "Enhance Audio"
5. Wait for processing (typically 5-15 seconds)
6. Listen to the enhanced audio and download if desired

### Method 2: Enhance Web Audio

1. Navigate to any webpage with audio or video
2. Look for the "🎤 AI Enhance" button that appears near media players
3. Click the button to enhance that audio
4. The audio will be replaced with the enhanced version

### Method 3: Right-Click Menu

1. Right-click on any audio or video element on a webpage
2. Select "Enhance Audio with AI" from the context menu
3. The audio will be processed and enhanced automatically

## ⚙️ Enhancement Levels

- **🔵 Low**: Gentle cleanup, preserves ambience (2-3 dB improvement)
- **🟢 Medium**: Balanced noise removal (4-5 dB improvement)
- **🟡 High**: Strong removal, clear voice (6-8 dB improvement)
- **🟠 Advanced**: Maximum removal, voice boosted (10-15 dB improvement)
- **🔴 Extreme**: Ultra-clarity for hard-to-understand speech (12+ dB improvement)

## 🔧 Configuration

### Update API URL

If you're self-hosting the backend, update the API URL:

1. Open `popup.js`
2. Find `const API_URL = 'https://your-app-url.railway.app';`
3. Replace with your backend URL
4. Save and reload the extension

### Keyboard Shortcuts

- `Ctrl+Shift+E` (Windows/Linux) or `Cmd+Shift+E` (Mac): Open extension popup

## 📋 Supported Formats

- WAV (recommended)
- MP3
- OGG
- FLAC
- M4A

Maximum file size: 100MB

## 🛡️ Privacy & Security

- Your audio files are processed on secure servers
- Files are automatically deleted after processing
- No data is stored permanently
- HTTPS encryption for all transfers

## 🐛 Troubleshooting

### Extension not appearing
- Make sure Developer mode is enabled
- Try reloading the extension
- Check browser console for errors

### Processing fails
- Check your internet connection
- Verify the backend server is running
- Try a smaller file or different format
- Check browser console for error details

### No audio elements found
- Some websites use custom players that aren't detected
- Use the file upload method instead
- Try refreshing the page

## 🔗 Full Web Application

For more features and advanced options, visit the full web application:
**[https://your-app-url.railway.app](https://your-app-url.railway.app)**

## 📝 License

Copyright © 2026 AI Speech Enhancement Team

## 🤝 Support

Having issues? Contact us or visit our GitHub repository for help.

---

**Built with ❤️ using advanced AI and signal processing**
