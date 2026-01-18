# Railway Deployment Guide

## Quick Deploy to Railway

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository: `ThangaVeeraputhiran/noise_removing_project`
   - Railway will auto-detect and deploy

3. **Environment Variables** (Optional)
   - `PORT` - Auto-set by Railway
   - No additional config needed!

4. **Access Your App**
   - Railway will provide a URL like: `https://your-app.railway.app`
   - Open the URL to use the speech enhancement system

## What's Included

- ✅ Procfile - Tells Railway how to run the app
- ✅ runtime.txt - Specifies Python version
- ✅ requirements.txt - Dependencies (optimized for Railway)
- ✅ .railwayignore - Excludes unnecessary files
- ✅ PORT environment variable support

## Local Testing

Test before deployment:
```bash
python app_production.py
```

## Troubleshooting

- **Build fails**: Check Railway build logs for missing dependencies
- **App crashes**: Ensure all required Python packages are in requirements.txt
- **Port issues**: Railway auto-sets PORT, no manual config needed

## Features

- Web-based audio upload
- Real-time noise reduction
- Multiple enhancement profiles
- Visual spectrogram comparison
- Download processed audio
