#!/bin/bash
# Entrypoint script for Railway deployment
set -e

# Get PORT from environment or default to 5000
PORT=${PORT:-5000}

# Fix numba caching issues in production
# Default: JIT DISABLED (1) for stability - set to 0 in Railway to enable
export NUMBA_DISABLE_JIT=${NUMBA_DISABLE_JIT:-1}
export NUMBA_CACHE_DIR=${NUMBA_CACHE_DIR:-/tmp/numba_cache}

echo "NUMBA_DISABLE_JIT: $NUMBA_DISABLE_JIT"
echo "NUMBA_CACHE_DIR: $NUMBA_CACHE_DIR"

# Only create cache dir if JIT is enabled
if [ "$NUMBA_DISABLE_JIT" = "0" ]; then
    mkdir -p "$NUMBA_CACHE_DIR"
    echo "Numba cache directory created (JIT enabled)"
else
    echo "Numba JIT disabled - no cache needed (slower but stable)"
fi

echo "========================================="
echo "Starting AI Speech Enhancement System v2.1"
echo "========================================="
echo "PORT: $PORT"
echo "Environment: Production"
echo "Python: $(python --version)"
echo "Directory: $(pwd)"
echo "========================================="

# Create necessary directories
mkdir -p uploads outputs static/spectrograms

# Run gunicorn with optimized settings for Railway
# Removed --preload-app for faster startup and better healthcheck response
exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 1 \
    --threads 2 \
    --worker-class gthread \
    --timeout 300 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    app_production:app
