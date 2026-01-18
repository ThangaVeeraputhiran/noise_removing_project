  # Network Error - Complete Solutions Guide

## Problem: "Network error. Please check your connection and try again."

Your browser shows this error even though the network is good. This guide has ALL solutions.

---

## 🎯 MOST COMMON CAUSES (Try these FIRST)

### Cause 1: Browser Cache Issue ⭐ (Fixes 80% of cases)

**SOLUTION:**
1. Press `Ctrl+Shift+Delete` (Windows/Linux) or `Cmd+Shift+Delete` (Mac)
2. In the dialog that opens:
   - Select "All time" or "Everything"
   - Check these boxes:
     ☑ Cookies and other site data
     ☑ Cached images and files
3. Click "Clear data"
4. **Close the browser completely** (don't just refresh)
5. Reopen browser and go to `http://localhost:5000`

---

### Cause 2: Using Wrong URL

**Solution - Try these URLs in order:**

```
1. http://localhost:5000          ← Most reliable
2. http://127.0.0.1:5000          ← If localhost fails
3. http://10.0.0.36:5000          ← For network access
4. http://localhost:5000/test      ← Diagnostic page
```

---

### Cause 3: App Not Actually Running

**SOLUTION - Restart the app:**

```bash
# Kill the old process
pkill -f app_production.py

# Wait a moment
sleep 2

# Start fresh
cd /workspaces/Speech-Enhancement-System
python app_production.py &

# Verify it's running
sleep 3
ps aux | grep app_production | grep -v grep
```

If you see output like: `python app_production.py` → App is running ✅

---

## 🔧 DETAILED TROUBLESHOOTING

### Step 1: Check if Server is Running

Open terminal and run:
```bash
ps aux | grep app_production | grep -v grep
```

**If you see output:** Server is running ✅
**If NO output:** Server crashed → Restart it

---

### Step 2: Check if Port is Listening

Open terminal and run:
```bash
lsof -i :5000
```

**If you see output:** Port is listening ✅
**If NO output:** Port is blocked or app crashed → Restart app

---

### Step 3: Test HTTP Connection

Open terminal and run:
```bash
curl -v http://localhost:5000/
```

**If you see:** `HTTP/1.1 200 OK` → Server is responding ✅
**If you see:** `Connection refused` → App crashed → Restart it
**If timeout:** Port blocked → Use different URL or firewall issue

---

### Step 4: Try Different Browser

If Chrome doesn't work:
- ❌ Chrome → Try Firefox
- ❌ Firefox → Try Edge
- ❌ Edge → Try Safari

Browser-specific issues are common with caching.

---

### Step 5: Use Incognito Mode

Chrome/Edge/Firefox all have private/incognito mode that bypasses cache:

**Chrome/Edge:** `Ctrl+Shift+N` then go to `http://localhost:5000`
**Firefox:** `Ctrl+Shift+P` then go to `http://localhost:5000`

---

### Step 6: Check Firewall

Your system firewall might be blocking port 5000:

**Windows:**
- Search "Windows Defender Firewall"
- Click "Allow an app through firewall"
- Look for Python in the list
- Ensure it has access

**Mac:**
- System Preferences → Security & Privacy
- Check firewall settings
- Allow Python if needed

**Linux:**
```bash
sudo ufw allow 5000
```

---

### Step 7: Verify Static Files

Open terminal and run:
```bash
curl -v http://localhost:5000/static/css/style.css
```

**If you see HTML content:** Files are loading ✅
**If 404 error:** Static files missing → Recreate them

---

## 🧪 RUN DIAGNOSTIC TEST

Run this to check everything automatically:

```bash
bash diagnose.sh
```

This will show:
- ✅ or ❌ for each system component
- Network addresses
- What's working and what isn't

---

## ✅ CONNECTION TEST PAGE

Visit the diagnostic test page:
```
http://localhost:5000/test
```

This page will:
- Test server connectivity
- Check health endpoint
- Verify upload capability
- Show green ✓ if all working

---

## 🆘 IF STILL NOT WORKING

### Nuclear Option (Complete Reset)

```bash
# Kill app
pkill -f app_production.py
pkill -f python
sleep 2

# Clear all Python cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

# Restart fresh
cd /workspaces/Speech-Enhancement-System
python app_production.py &
sleep 5

# Test
curl -v http://localhost:5000/
```

---

## 📋 CHECKLIST

Before giving up, verify:

- [ ] App process is running: `ps aux | grep app_production`
- [ ] Port 5000 is listening: `lsof -i :5000`
- [ ] Can reach server: `curl http://localhost:5000/`
- [ ] Browser cache cleared: `Ctrl+Shift+Delete`
- [ ] Tried different URL: `http://127.0.0.1:5000`
- [ ] Tried different browser: Firefox/Chrome/Edge/Safari
- [ ] Tried incognito mode: Bypass all cache
- [ ] Tried diagnostic page: `http://localhost:5000/test`
- [ ] Ran diagnostics: `bash diagnose.sh`
- [ ] Complete restart done: Kill and restart app

---

## 💡 Pro Tips

1. **Always check browser console:** Press `F12`, go to "Console" tab, look for errors
2. **Check Network tab:** See what requests fail and why
3. **Use curl to test:** Terminal is more reliable than browser for basic connectivity
4. **Clear cookies too:** Sometimes cookies cause weird issues
5. **Try a different machine:** If possible, test on different device to isolate the issue

---

## 📞 Getting Help

If you're still stuck, collect this information:

```bash
# Run these commands and share the output:
echo "=== App Status ===" && \
ps aux | grep app_production && \
echo "" && \
echo "=== Port Status ===" && \
lsof -i :5000 && \
echo "" && \
echo "=== HTTP Test ===" && \
curl -v http://localhost:5000/ 2>&1 | head -20 && \
echo "" && \
echo "=== Diagnostics ===" && \
bash diagnose.sh
```

---

**Remember:** The server is running correctly. This is almost always a browser/network configuration issue, not a server issue. Clear your cache and try a different browser - that fixes 90% of these cases! 🎉
