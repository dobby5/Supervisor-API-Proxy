#!/bin/bash

echo "=== Starting Supervisor API Proxy ==="
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"

# Set environment variables with defaults
export LOG_LEVEL="${LOG_LEVEL:-info}"
export CORS_ORIGINS="${CORS_ORIGINS:-}"

echo "Environment:"
echo "  LOG_LEVEL: $LOG_LEVEL"
echo "  CORS_ORIGINS: $CORS_ORIGINS"

# Check for Supervisor token
if [ -n "$SUPERVISOR_TOKEN" ]; then
    echo "✅ Supervisor token is available"
else
    echo "⚠️ WARNING: SUPERVISOR_TOKEN not available!"
fi

echo "🚀 Starting Flask application on port 8080..."
python app-simple.py