#!/usr/bin/with-contenv bashio

# Set default environment variables for minimal config
export LOG_LEVEL="info"
export CORS_ORIGINS=""

# Log startup info
bashio::log.info "Starting Supervisor API Proxy..."
bashio::log.info "Version: 1.2.0"

# Check if supervisor token is available
if bashio::var.has_value "${SUPERVISOR_TOKEN}"; then
    bashio::log.info "Supervisor token is available"
else
    bashio::log.warning "Supervisor token is not available!"
fi

# Start the application
bashio::log.info "Starting Flask application on port 8080..."
bashio::log.info "API will be available at: http://homeassistant:8080/api/v1/"

# Start Python app in background to capture startup
python3 app.py &
APP_PID=$!

# Wait a moment for startup
sleep 2

# Check if the application is still running
if kill -0 $APP_PID 2>/dev/null; then
    bashio::log.info "✅ Supervisor API Proxy started successfully!"
    bashio::log.info "🌐 API endpoints available at: http://homeassistant:8080/api/v1/"
    bashio::log.info "📋 Health check: http://homeassistant:8080/api/v1/health"
    bashio::log.info "📋 Available endpoints: http://homeassistant:8080/api/v1/endpoints"
    
    # Wait for the background process
    wait $APP_PID
else
    bashio::log.error "❌ Failed to start Supervisor API Proxy!"
    exit 1
fi