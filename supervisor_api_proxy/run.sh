#!/usr/bin/with-contenv bashio

# Get options from add-on configuration
LOG_LEVEL=$(bashio::config 'log_level' 'info')
CORS_ORIGINS=$(bashio::config 'cors_origins')

# Set environment variables
export LOG_LEVEL="${LOG_LEVEL}"
export CORS_ORIGINS="${CORS_ORIGINS}"

# Log startup info
bashio::log.info "Starting Supervisor API Proxy..."
bashio::log.info "Log level: ${LOG_LEVEL}"
bashio::log.info "CORS origins: ${CORS_ORIGINS}"

# Check if supervisor token is available
if bashio::var.has_value "${SUPERVISOR_TOKEN}"; then
    bashio::log.info "Supervisor token is available"
else
    bashio::log.warning "Supervisor token is not available!"
fi

# Start the application
bashio::log.info "Starting Flask application on port 8080"
python3 app.py