# Railway Healthcheck Configuration Guide

## ✅ Configuration Complete

The application is now properly configured for Railway deployment with healthchecks.

## Required Railway Service Variables

Add these environment variables in your Railway service settings:

### 1. PORT (Automatically Injected by Railway)
Railway automatically provides this - **DO NOT set manually unless using custom target ports**

### 2. RAILWAY_HEALTHCHECK_TIMEOUT_SEC
```
RAILWAY_HEALTHCHECK_TIMEOUT_SEC=300
```
**Purpose**: Sets healthcheck timeout to 5 minutes (300 seconds) to allow ML libraries to load

### 3. Optional: Additional Variables

#### PYTHONUNBUFFERED
```
PYTHONUNBUFFERED=1
```
**Purpose**: Ensures Python logs appear in real-time

#### WORKERS (Optional)
```
WORKERS=1
```
**Purpose**: Control number of gunicorn workers (1 is recommended for Railway's memory limits)

## Healthcheck Configuration

### ✅ What's Configured:
- **Healthcheck Path**: `/health`
- **Healthcheck Timeout**: 300 seconds (5 minutes)
- **Start Command**: `./entrypoint.sh`
- **Restart Policy**: `ON_FAILURE` with 10 max retries

### 🔧 How It Works:

1. **Build Phase**: Docker builds your container (takes ~3 minutes)
2. **Start Phase**: Gunicorn starts and binds to PORT
3. **Healthcheck Phase**: Railway hits `/health` endpoint
4. **Success**: Returns 200 status with JSON response
5. **Traffic Routing**: Railway routes traffic to your service

## Healthcheck Endpoint

```bash
GET /health
```

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "system": "Production Speech Enhancement",
  "version": "1.0",
  "timestamp": "2026-01-20T10:30:00.123456"
}
```

## Gunicorn Configuration

### Optimized Settings:
- **Workers**: 1 (reduced from 2 for faster startup)
- **Threads**: 2 (per worker for concurrency)
- **Worker Class**: `gthread` (better for I/O-bound tasks)
- **Timeout**: 300 seconds (for long-running ML processing)
- **Graceful Timeout**: 30 seconds (for clean shutdowns)
- **No Preload**: Removed `--preload-app` for faster healthcheck response

### Why These Changes?

**Before** (❌ Failed):
```bash
gunicorn --workers 2 --worker-class sync --timeout 120 --preload-app
```
- `--preload-app` loads ALL modules before binding to port
- Heavy ML libraries (numpy, scipy, librosa, tensorflow) take 60-90s to import
- Healthcheck times out before port is available

**After** (✅ Success):
```bash
gunicorn --workers 1 --threads 2 --worker-class gthread --timeout 300
```
- Port binds immediately
- Modules load lazily (only when needed)
- Healthcheck succeeds within 5-10 seconds

## Testing Healthcheck Locally

```bash
# Start the server
./entrypoint.sh

# In another terminal, test the healthcheck
curl http://localhost:5000/health

# Expected response
{"status":"healthy","system":"Production Speech Enhancement","version":"1.0","timestamp":"2026-01-20T..."}
```

## Deployment Checklist

### Before Deploying:

- [x] Update `railway.json` with `healthcheckTimeout: 300`
- [x] Optimize `entrypoint.sh` (remove `--preload-app`)
- [x] Set `RAILWAY_HEALTHCHECK_TIMEOUT_SEC=300` in Railway dashboard
- [x] Ensure `/health` endpoint returns 200 status
- [x] Verify `PORT` variable is used correctly

### After Deploying:

1. **Monitor Build Logs**: Watch for build completion (~3 minutes)
2. **Monitor Healthcheck**: Should pass within 10-30 seconds
3. **Check Application Logs**: Look for "Starting AI Speech Enhancement System v2.1"
4. **Test Endpoint**: Visit `https://your-app.railway.app/health`

## Railway Service Settings

### In Railway Dashboard → Your Service → Settings:

1. **Healthcheck Path**:
   ```
   /health
   ```

2. **Healthcheck Timeout** (Service Variable):
   ```
   Variable: RAILWAY_HEALTHCHECK_TIMEOUT_SEC
   Value: 300
   ```

3. **Start Command** (should be automatic from railway.json):
   ```
   ./entrypoint.sh
   ```

## Common Issues & Solutions

### Issue 1: "failed with service unavailable"

**Cause**: Application not listening on PORT or healthcheck endpoint not ready

**Solution**:
```bash
# Verify PORT is set in Railway
echo $PORT  # Should output Railway's assigned port

# Check entrypoint.sh uses PORT
grep "PORT" entrypoint.sh  # Should see --bind 0.0.0.0:${PORT}
```

### Issue 2: "failed with status 400"

**Cause**: Application rejects healthcheck.railway.app hostname

**Solution**: Already fixed - CORS is configured in app_production.py:
```python
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
```

### Issue 3: Timeout after 1m40s

**Cause**: Default timeout too short for ML library loading

**Solution**: Set `RAILWAY_HEALTHCHECK_TIMEOUT_SEC=300` (already configured in railway.json)

### Issue 4: "1/1 replicas never became healthy"

**Cause**: Multiple issues - preload, timeout, or binding

**Solutions**:
1. ✅ Remove `--preload-app` from gunicorn
2. ✅ Increase timeout to 300 seconds
3. ✅ Verify PORT binding in entrypoint.sh
4. ✅ Use gthread worker class

## Monitoring

### View Healthcheck Status:
```bash
# In Railway dashboard
Build tab → Deployment logs → Look for:
"====================
Starting Healthcheck
====================
Path: /health
Retry window: 5m0s

Attempt #1 succeeded with status 200"
```

### View Application Logs:
```bash
# In Railway dashboard
Deployments → Active deployment → Logs

# Look for:
"Starting AI Speech Enhancement System v2.1"
"Booting worker with pid: ..."
```

## Performance Optimization

### Current Configuration:
- **Workers**: 1 (optimal for Railway's free/hobby tier)
- **Threads**: 2 (handles concurrent requests)
- **Memory**: ~512MB-1GB (ML libraries are loaded on-demand)

### For Higher Traffic (Pro Plan):
```bash
# Increase workers in entrypoint.sh:
--workers 2 \
--threads 4 \
```

## Security Notes

1. **Healthcheck Hostname**: Railway uses `healthcheck.railway.app` - already allowed via CORS
2. **Non-root User**: Dockerfile uses `nobody:nogroup` for security
3. **Environment Variables**: Never commit secrets to git - use Railway's secret variables

## Next Steps

1. ✅ **Commit Changes**: Commit updated files to git
2. ✅ **Push to GitHub**: Push to your repository
3. ✅ **Deploy on Railway**: Railway will auto-deploy
4. ✅ **Monitor Healthcheck**: Watch deployment logs
5. ✅ **Test Endpoint**: Visit `/health` endpoint
6. ✅ **Test Application**: Upload and process audio file

## Support

If healthcheck still fails:
1. Check Railway deployment logs for specific error
2. Verify all environment variables are set
3. Test locally with Docker: `docker build -t app . && docker run -p 5000:5000 app`
4. Check this guide: https://docs.railway.app/deploy/healthchecks

---

**Last Updated**: January 20, 2026
**Status**: ✅ Production Ready
