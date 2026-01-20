## 🚀 Railway Environment Variables - Quick Setup

Copy and paste these into your Railway service settings:

### Service Variables (Settings → Variables → New Variable)

#### 1. Healthcheck Timeout (REQUIRED)
```
Variable Name: RAILWAY_HEALTHCHECK_TIMEOUT_SEC
Value: 300
```

#### 2. Python Unbuffered (RECOMMENDED)
```
Variable Name: PYTHONUNBUFFERED
Value: 1
```

#### 3. Numba Cache Directory (AUTO-CONFIGURED)
```
Variable Name: NUMBA_CACHE_DIR
Value: /tmp/numba_cache
```
**Note**: Auto-set in Dockerfile. Only needed if you enable JIT.

#### 4. Numba JIT Control (DEFAULT: DISABLED for stability)
```
Variable Name: NUMBA_DISABLE_JIT
Value: 1 (DISABLED - default, stable)
       0 (ENABLED - faster but may have cache errors)
```
**Current Default**: `1` (disabled) - This avoids ALL caching errors but is 2-3x slower.  
**To enable JIT**: Set to `0` in Railway (faster but requires working cache).

#### 5. Flask App (AUTO-SET in Dockerfile, but can verify)
```
Variable Name: FLASK_APP
Value: app_production.py
```

### ⚠️ DON'T SET THESE (Auto-Injected by Railway):
- ❌ `PORT` - Railway automatically provides this
- ❌ `RAILWAY_ENVIRONMENT` - Auto-set by Railway
- ❌ `RAILWAY_SERVICE_NAME` - Auto-set by Railway

---

## 🏥 Healthcheck Settings (Settings → Deploy)

### In Railway Dashboard:

**Healthcheck Path**:
```
/health
```

**Healthcheck Timeout** (via variable above):
```
RAILWAY_HEALTHCHECK_TIMEOUT_SEC=300
```

---

## 📋 Quick Deploy Checklist

- [x] Set `RAILWAY_HEALTHCHECK_TIMEOUT_SEC=300`
- [x] Set `PYTHONUNBUFFERED=1`
- [x] ✅ `NUMBA_DISABLE_JIT=1` (default - JIT disabled for stability)
- [x] Healthcheck path is `/health`
- [x] Commit and push code changes
- [x] Wait for Railway to auto-deploy
- [x] Monitor deployment logs for healthcheck success

**Note**: With JIT disabled (default), processing is 2-3x slower but 100% stable with NO cache errors!

---

## 🧪 Test After Deployment

```bash
# Test healthcheck endpoint
curl https://your-app.railway.app/health

# Expected response:
{
  "status": "healthy",
  "system": "Production Speech Enhancement",
  "version": "1.0",
  "timestamp": "2026-01-20T..."
}
```

---

## 📊 What Changed (Technical Summary)

### Before (❌ Failed):
- Healthcheck timeout: 100s (too short)
- Gunicorn: `--preload-app` (slow startup)
- Workers: 2 (unnecessary for startup)

### After (✅ Fixed):
- Healthcheck timeout: 300s (5 minutes)
- Gunicorn: No preload (fast startup)
- Workers: 1 with 2 threads (optimized)
- Worker class: `gthread` (better I/O handling)

---

**Files Modified**:
1. `entrypoint.sh` - Optimized gunicorn settings
2. `railway.json` - Increased healthcheck timeout
3. `RAILWAY_HEALTHCHECK_CONFIG.md` - Full documentation (created)
4. `RAILWAY_VARIABLES.md` - This quick reference (created)
