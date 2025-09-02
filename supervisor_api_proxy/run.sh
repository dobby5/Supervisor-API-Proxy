#!/usr/bin/with-contenv bashio

# Set default environment variables for minimal config
export LOG_LEVEL="info"
export CORS_ORIGINS=""

# Log startup info
bashio::log.info "🚀 Starting Supervisor API Proxy v1.2.0"

# Check if supervisor token is available
if bashio::var.has_value "${SUPERVISOR_TOKEN}"; then
    bashio::log.info "✅ Supervisor token is available"
else
    bashio::log.warning "⚠️ Supervisor token is not available!"
fi

# Log port and API info
bashio::log.info "🌐 Starting on port 8080"
bashio::log.info "📡 API available at: http://homeassistant:8080/api/v1/"

# Change to app directory and start the application
cd /app
exec python3 app.py