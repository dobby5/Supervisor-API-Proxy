#!/bin/bash
# ==============================================================================
# Simple startup script without s6-overlay dependencies
# ==============================================================================

set -e

# Default values
DEFAULT_PORT=8099
DEFAULT_LOG_LEVEL="info"
DEFAULT_CORS_ORIGINS="*"

echo "=================================================="
echo " Home Assistant Supervisor API Proxy"
echo " Version: 1.0.0"
echo "=================================================="

# Load configuration from options.json if available
if [ -f "/data/options.json" ]; then
    echo "Loading configuration from options.json..."
    
    PORT=$(jq -r '.port // 8099' /data/options.json)
    LOG_LEVEL=$(jq -r '.log_level // "info"' /data/options.json)
    CORS_ORIGINS_RAW=$(jq -r '.cors_origins[]?' /data/options.json)
    SSL_ENABLED=$(jq -r '.ssl // false' /data/options.json)
    
    # Convert CORS origins array to comma-separated string
    if [ -n "$CORS_ORIGINS_RAW" ]; then
        CORS_ORIGINS=$(echo "$CORS_ORIGINS_RAW" | tr '\n' ',' | sed 's/,$//')
    else
        CORS_ORIGINS="*"
    fi
else
    echo "No options.json found, using defaults..."
    PORT=$DEFAULT_PORT
    LOG_LEVEL=$DEFAULT_LOG_LEVEL
    CORS_ORIGINS=$DEFAULT_CORS_ORIGINS
    SSL_ENABLED=false
fi

# Export environment variables
export PORT
export LOG_LEVEL
export CORS_ORIGINS

echo "Configuration:"
echo "  - Port: $PORT"
echo "  - Log Level: $LOG_LEVEL"
echo "  - CORS Origins: $CORS_ORIGINS"
echo "  - SSL Enabled: $SSL_ENABLED"

# Validate Supervisor token
if [ -z "${SUPERVISOR_TOKEN}" ]; then
    echo "ERROR: SUPERVISOR_TOKEN environment variable is not set!"
    echo "This add-on requires access to the Supervisor API."
    exit 1
fi

# Test Supervisor API connection
echo "Testing Supervisor API connection..."
if curl -s -f \
    -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
    -H "Content-Type: application/json" \
    --max-time 10 \
    "http://supervisor/supervisor/ping" > /dev/null 2>&1; then
    echo "✓ Supervisor API connection successful"
else
    echo "⚠ Warning: Unable to connect to Supervisor API"
    echo "  Service will start anyway..."
fi

# Start the application
echo "Starting Supervisor API Proxy..."
echo "Service will be available on port $PORT"

cd /app

if [ "$LOG_LEVEL" = "debug" ]; then
    echo "Starting in development mode..."
    python3 app.py
else
    echo "Starting in production mode with Gunicorn..."
    exec gunicorn \
        --bind "0.0.0.0:$PORT" \
        --workers 2 \
        --timeout 120 \
        --keepalive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --log-level "$LOG_LEVEL" \
        --access-logfile - \
        --error-logfile - \
        --capture-output \
        --enable-stdio-inheritance \
        app:app
fi