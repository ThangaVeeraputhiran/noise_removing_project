# Network Troubleshooting Guide

## Access URLs

Your Speech Enhancement System is running on:

### Local Access (From this container):
```
http://localhost:5000
http://127.0.0.1:5000
```

### Network Access (From your host machine or other network):
```
http://10.0.0.36:5000
```

### If using GitHub Codespaces:
The browser preview should work automatically, or use the forwarded port URL.

---

## Troubleshooting Steps

### 1. Check if app is running:
```bash
ps aux | grep app_production
```

### 2. Check if port 5000 is listening:
```bash
lsof -i :5000
```

### 3. Test connection from terminal:
```bash
curl -v http://localhost:5000/
```

### 4. Browser Console Check:
- Press `F12` or `Ctrl+Shift+I` to open Developer Tools
- Go to "Console" tab
- Check for any JavaScript errors

### 5. Network Tab:
- Go to "Network" tab in Developer Tools
- Upload a file and watch for request details
- Check response status codes

### 6. Common Issues:

**Issue: "Network error"**
- Solution: Make sure port 5000 is accessible from your browser's location
- Check firewall settings
- Try a different browser

**Issue: "Cannot reach server"**
- Solution: Restart the app:
  ```bash
  # Kill old process
  pkill -f app_production.py
  
  # Restart
  cd /workspaces/Speech-Enhancement-System
  python app_production.py &
  ```

**Issue: Uploads not processing**
- Check browser console for JavaScript errors
- Check Flask logs for backend errors
- Ensure `uploads/` and `outputs/` directories exist

### 7. How to use the app:

1. Open http://localhost:5000 (or appropriate URL above)
2. Click "Choose Audio File" or drag-drop an audio file
3. Select enhancement level (Light/Medium/High/Maximum)
4. Click "Process Audio"
5. Wait for processing to complete
6. Download enhanced audio

### 8. Restart the application:

```bash
# From /workspaces/Speech-Enhancement-System

# Kill existing process
pkill -f app_production.py

# Start fresh
python app_production.py
```

---

## If Still Not Working:

Run this diagnostic script:
```bash
python -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 5000))
if result == 0:
    print('✓ Port 5000 is open and listening')
else:
    print('✗ Port 5000 is NOT listening')
sock.close()
"
```

---

**Status**: The application is running and ready to use!
**Access**: http://localhost:5000 or http://10.0.0.36:5000
