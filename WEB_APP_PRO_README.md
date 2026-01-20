# AI Speech Enhancement Pro - Professional Web Application

## 🎯 Overview

A state-of-the-art web application for AI-powered speech enhancement with professional-grade visualizations and analytics.

## ✨ New Features

### Professional UI (`/pro`)
- **Hero Section**: Stunning gradient design with animated waveforms
- **Interactive Visualizations**: Real-time spectrograms and frequency analysis
- **Before/After Comparison**: Side-by-side waveforms with WaveSurfer.js
- **Metrics Dashboard**: Comprehensive quality metrics display
- **Multi-tab Visualizations**: Spectrogram, Frequency Analysis, and Comparison charts
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **Dark Mode Support**: Coming soon!

### Browser Extension
- **Chrome/Firefox Support**: Universal browser compatibility
- **One-Click Enhancement**: Process audio with a single click
- **In-Page Integration**: Enhance audio elements directly on web pages
- **Context Menu**: Right-click to enhance any audio/video element
- **Drag & Drop**: Easy file upload in popup
- **Settings Persistence**: Remembers your preferences

## 🚀 Access the New UI

### Professional Web Interface
Visit: `https://your-app-url.railway.app/pro`

### Original Simple Interface
Visit: `https://your-app-url.railway.app/`

## 📊 Visualizations

### 1. Waveform Comparison
- Interactive waveforms powered by WaveSurfer.js
- Zoom and pan capabilities
- Play/pause synchronized audio

### 2. Spectrogram Analysis
- Before/after spectrogram comparison
- Frequency vs. time visualization
- Visual noise reduction demonstration

### 3. Frequency Domain Charts
- Real-time frequency spectrum comparison
- Chart.js powered interactive graphs
- Export capabilities

### 4. Quality Metrics
- SNR improvement tracking
- Noise detection confidence
- Processing mode indicators
- Duration and file size stats

## 🔧 Installation & Setup

### Web Application

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run locally**:
   ```bash
   python app_production.py
   ```

3. **Access**:
   - Main UI: `http://localhost:8000/`
   - Pro UI: `http://localhost:8000/pro`

### Browser Extension

1. **Navigate to extension folder**:
   ```bash
   cd browser_extension
   ```

2. **Update API URL**:
   - Edit `popup.js`
   - Change `API_URL` to your backend URL

3. **Load in browser**:
   - **Chrome**: `chrome://extensions/` → Load unpacked
   - **Firefox**: `about:debugging` → Load temporary add-on

## 📁 Project Structure

```
├── templates/
│   ├── index.html              # Original UI
│   ├── index_pro.html          # Professional UI ⭐ NEW
│   ├── test.html
│   └── upload_test.html
├── static/
│   ├── css/
│   │   ├── style.css           # Original styles
│   │   └── style_pro.css       # Professional styles ⭐ NEW
│   ├── js/
│   │   ├── app.js              # Original JavaScript
│   │   └── app_pro.js          # Professional JavaScript ⭐ NEW
│   └── spectrograms/           # Generated spectrograms
├── browser_extension/          ⭐ NEW
│   ├── manifest.json           # Extension configuration
│   ├── popup.html              # Extension popup UI
│   ├── popup.js                # Popup logic
│   ├── background.js           # Background service worker
│   ├── content.js              # Content script
│   ├── content.css             # Content styles
│   ├── icons/                  # Extension icons
│   └── README.md               # Extension documentation
├── app_production.py           # Main Flask application
├── simple_processor.py         # Fallback processor
└── requirements.txt            # Python dependencies
```

## 🎨 UI Features

### Navigation
- Sticky navbar with smooth scrolling
- Quick access to all sections
- Mobile-responsive menu

### Hero Section
- Eye-catching gradient background
- Animated waveform visualization
- Key statistics display
- Call-to-action button

### Features Section
- 4 feature cards with icons
- Detailed capability descriptions
- Hover animations

### Demo Section
- Drag & drop file upload
- Real-time processing status
- Progress indicators
- Interactive results display

### Stats Section
- Performance benchmarks
- Chart.js visualizations
- Processing time metrics
- Accuracy statistics

### API Section
- REST API documentation
- Code examples
- Extension download links

## 🔌 API Endpoints

### Process Audio
```http
POST /process
Content-Type: multipart/form-data

{
  "audio_file": <file>,
  "enhancement_level": "low|medium|high|advanced|extreme"
}
```

**Response**:
```json
{
  "success": true,
  "output_file": "timestamp_enhanced.wav",
  "spectrogram": "timestamp_spectrogram.png",
  "noise_type": "vehicle",
  "confidence": "95.0",
  "snr_improvement": "8.50",
  "duration": "5.23",
  "enhancement_level": "high",
  "download_url": "/download/timestamp_enhanced.wav",
  "mode": "simple|standard"
}
```

### Health Check
```http
GET /health
```

### Diagnostics
```http
GET /api/diagnostics
```

### Test Imports
```http
GET /api/test-imports
```

## 🎯 Enhancement Levels

| Level | Description | SNR Improvement | Use Case |
|-------|-------------|-----------------|----------|
| 🔵 Low | Gentle cleanup | 2-3 dB | Podcasts, light noise |
| 🟢 Medium | Balanced removal | 4-5 dB | Interviews, calls |
| 🟡 High | Strong removal | 6-8 dB | Noisy recordings |
| 🟠 Advanced | Maximum cleaning | 10-15 dB | Heavy background noise |
| 🔴 Extreme | Ultra-clarity | 12+ dB | Hard-to-understand speech |

## 🧪 Testing

### Test the Professional UI
```bash
# Start the server
python app_production.py

# Visit in browser
http://localhost:8000/pro
```

### Test the Extension
1. Load extension in browser
2. Click extension icon
3. Upload a test audio file
4. Verify processing completes
5. Download enhanced audio

## 🚀 Deployment

### Railway (Current)
The application is already configured for Railway deployment with:
- `Procfile`
- `railway.json`
- `entrypoint.sh`

### Update for Production
1. **Set API URL in extension**:
   ```javascript
   const API_URL = 'https://your-production-url.railway.app';
   ```

2. **Update footer links**:
   - Edit `index_pro.html`
   - Update social media links
   - Add GitHub repository link

3. **Deploy**:
   ```bash
   git add .
   git commit -m "Add professional UI and browser extension"
   git push
   ```

## 📱 Browser Extension Distribution

### Chrome Web Store
1. Create developer account ($5 one-time fee)
2. Package extension as `.zip`
3. Upload to Chrome Web Store
4. Submit for review

### Firefox Add-ons
1. Create developer account (free)
2. Package extension as `.zip`
3. Upload to addons.mozilla.org
4. Submit for review

## 🎨 Customization

### Colors
Edit CSS variables in `style_pro.css`:
```css
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --accent: #f093fb;
    /* ... */
}
```

### Charts
Modify chart configurations in `app_pro.js`:
```javascript
new Chart(canvas, {
    type: 'line',
    data: { /* ... */ },
    options: { /* ... */ }
});
```

## 🔒 Security

- CORS headers configured
- File size limits enforced (100MB)
- Input validation on all uploads
- Automatic file cleanup
- HTTPS required in production

## 📚 Dependencies

### Python Backend
- Flask 3.0.0
- SciPy 1.12.0
- NumPy 1.26.4
- Matplotlib 3.8.2
- SoundFile 0.12.1

### JavaScript Frontend
- Chart.js 4.4.0
- WaveSurfer.js 7.3.2
- Font Awesome 6.4.0

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

Copyright © 2026 AI Speech Enhancement Team

## 🆘 Support

- Issues: GitHub repository
- Email: support@example.com
- Documentation: `/pro` → API section

---

**Built with ❤️ using Flask, SciPy, and modern web technologies**
