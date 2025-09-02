#!/usr/bin/with-contenv bashio

# Set default environment variables for minimal config
export LOG_LEVEL="info"
export CORS_ORIGINS=""

# Log startup info
bashio::log.info "Starting Supervisor API Proxy..."

# Check if supervisor token is available
if bashio::var.has_value "${SUPERVISOR_TOKEN}"; then
    bashio::log.info "Supervisor token is available"
else
    bashio::log.warning "Supervisor token is not available!"
fi

# Start the application
bashio::log.info "Starting Flask application on port 8080"
exec python3 app.py