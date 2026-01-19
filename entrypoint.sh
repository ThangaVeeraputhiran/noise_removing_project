#!/bin/bash
# Entrypoint script for Railway deployment
set -e

# Get PORT from environment or default to 5000
PORT=${PORT:-5000}

echo "========================================="
echo "Starting AI Speech Enhancement System v2.1"
echo "========================================="
echo "PORT: $PORT"
echo "Environment: Production"
echo "Python: $(python --version)"
echo "========================================="

# Run gunicorn with proper error handling
exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --preload-app \
    --log-level info \
    app_production:app
