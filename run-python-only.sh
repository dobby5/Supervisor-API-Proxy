#!/bin/sh
# Simple startup script using only sh (no bash dependencies)

echo "=================================================="
echo " Home Assistant Supervisor API Proxy"
echo " Version: 1.0.0" 
echo "=================================================="

# Set default values
PORT=8099
LOG_LEVEL=info
CORS_ORIGINS="*"

# Load configuration from options.json if available
if [ -f "/data/options.json" ]; then
    echo "Loading configuration from options.json..."
    
    # Use jq to extract values
    PORT=$(jq -r '.port // 8099' /data/options.json 2>/dev/null || echo "8099")
    LOG_LEVEL=$(jq -r '.log_level // "info"' /data/options.json 2>/dev/null || echo "info")
    SSL_ENABLED=$(jq -r '.ssl // false' /data/options.json 2>/dev/null || echo "false")
    
    # Handle CORS origins array
    CORS_ORIGINS=$(jq -r '.cors_origins[]?' /data/options.json 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo "*")
    if [ -z "$CORS_ORIGINS" ]; then
        CORS_ORIGINS="*"
    fi
else
    echo "No options.json found, using defaults..."
fi

# Export environment variables for Python app
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

echo "Testing Supervisor API connection..."
if curl -s -f -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
   --max-time 10 "http://supervisor/supervisor/ping" >/dev/null 2>&1; then
    echo "✓ Supervisor API connection successful"
else
    echo "⚠ Warning: Unable to connect to Supervisor API"
    echo "  Service will start anyway..."
fi

# Change to app directory
cd /app

echo "Starting Supervisor API Proxy on port $PORT..."

# Start with Python directly (simpler than Gunicorn for troubleshooting)
exec python3 app.py