#!/bin/bash
# Entrypoint script for Railway deployment
set -e

# Get PORT from environment or default to 5000
PORT=${PORT:-5000}

echo "Starting Speech Enhancement System..."
echo "PORT: $PORT"

# Run gunicorn
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
