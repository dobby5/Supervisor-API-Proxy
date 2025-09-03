#!/usr/bin/env bashio
# ==============================================================================
# Home Assistant Supervisor API Proxy Add-on
# Starts the Supervisor API Proxy service
# ==============================================================================

set -e

# Default values
DEFAULT_PORT=8099
DEFAULT_LOG_LEVEL="info"
DEFAULT_CORS_ORIGINS="*"

# ==============================================================================
# LOGGING FUNCTIONS
# ==============================================================================

function log_info() {
    bashio::log.info "$1"
}

function log_warning() {
    bashio::log.warning "$1"
}

function log_error() {
    bashio::log.error "$1"
}

function log_debug() {
    bashio::log.debug "$1"
}

function log_fatal() {
    bashio::log.fatal "$1"
}

# ==============================================================================
# CONFIGURATION
# ==============================================================================

function load_config() {
    log_info "Loading add-on configuration..."
    
    # Get configuration values with defaults
    PORT=$(bashio::config 'port' "${DEFAULT_PORT}")
    LOG_LEVEL=$(bashio::config 'log_level' "${DEFAULT_LOG_LEVEL}")
    CORS_ORIGINS=$(bashio::config 'cors_origins' "${DEFAULT_CORS_ORIGINS}")
    SSL_ENABLED=$(bashio::config 'ssl' 'false')
    CERTFILE=$(bashio::config 'certfile' 'fullchain.pem')
    KEYFILE=$(bashio::config 'keyfile' 'privkey.pem')
    
    # Convert CORS origins array to comma-separated string
    if bashio::config.is_list 'cors_origins'; then
        CORS_ORIGINS=""
        for origin in $(bashio::config 'cors_origins'); do
            if [ -z "$CORS_ORIGINS" ]; then
                CORS_ORIGINS="$origin"
            else
                CORS_ORIGINS="$CORS_ORIGINS,$origin"
            fi
        done
    fi
    
    # Export environment variables
    export PORT
    export LOG_LEVEL
    export CORS_ORIGINS
    export SSL_ENABLED
    export CERTFILE
    export KEYFILE
    
    log_info "Configuration loaded:"
    log_info "  - Port: ${PORT}"
    log_info "  - Log Level: ${LOG_LEVEL}"
    log_info "  - CORS Origins: ${CORS_ORIGINS}"
    log_info "  - SSL Enabled: ${SSL_ENABLED}"
}

# ==============================================================================
# SUPERVISOR TOKEN VALIDATION
# ==============================================================================

function validate_supervisor_token() {
    log_info "Validating Supervisor token..."
    
    # Check if SUPERVISOR_TOKEN is set
    if [ -z "${SUPERVISOR_TOKEN}" ]; then
        log_fatal "SUPERVISOR_TOKEN environment variable is not set!"
        log_fatal "This add-on requires access to the Supervisor API."
        exit 1
    fi
    
    # Test Supervisor API connection
    log_debug "Testing Supervisor API connection..."
    
    if curl -s -f \
        -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
        -H "Content-Type: application/json" \
        --max-time 10 \
        "http://supervisor/supervisor/ping" > /dev/null 2>&1; then
        log_info "✓ Supervisor API connection successful"
    else
        log_warning "⚠ Unable to connect to Supervisor API. Service will start anyway."
        log_warning "  Make sure the add-on has proper permissions."
    fi
}

# ==============================================================================
# SSL CONFIGURATION
# ==============================================================================

function setup_ssl() {
    if bashio::config.true 'ssl'; then
        log_info "Setting up SSL configuration..."
        
        local certfile="/ssl/${CERTFILE}"
        local keyfile="/ssl/${KEYFILE}"
        
        # Check if SSL files exist
        if [ ! -f "$certfile" ]; then
            log_warning "SSL certificate file not found: ${certfile}"
            log_warning "Falling back to HTTP mode"
            SSL_ENABLED=false
        elif [ ! -f "$keyfile" ]; then
            log_warning "SSL key file not found: ${keyfile}"
            log_warning "Falling back to HTTP mode"
            SSL_ENABLED=false
        else
            log_info "✓ SSL certificates found"
            export SSL_CERT_FILE="$certfile"
            export SSL_KEY_FILE="$keyfile"
        fi
    else
        log_info "SSL disabled, using HTTP mode"
    fi
}

# ==============================================================================
# APPLICATION STARTUP
# ==============================================================================

function start_application() {
    log_info "Starting Supervisor API Proxy..."
    log_info "Service will be available on port ${PORT}"
    
    # Change to app directory
    cd /app || exit 1
    
    # Determine if we should use gunicorn or flask dev server
    if [ "${LOG_LEVEL}" = "debug" ]; then
        log_info "Starting in development mode with Flask dev server..."
        python3 app.py
    else
        log_info "Starting in production mode with Gunicorn..."
        
        # Gunicorn configuration
        local workers=2
        local timeout=120
        local keepalive=2
        local max_requests=1000
        local max_requests_jitter=100
        
        # SSL arguments
        local ssl_args=""
        if [ "${SSL_ENABLED}" = "true" ]; then
            ssl_args="--certfile=${SSL_CERT_FILE} --keyfile=${SSL_KEY_FILE}"
        fi
        
        # Start gunicorn
        exec gunicorn \
            --bind "0.0.0.0:${PORT}" \
            --workers ${workers} \
            --timeout ${timeout} \
            --keepalive ${keepalive} \
            --max-requests ${max_requests} \
            --max-requests-jitter ${max_requests_jitter} \
            --log-level "${LOG_LEVEL}" \
            --access-logfile - \
            --error-logfile - \
            --capture-output \
            --enable-stdio-inheritance \
            ${ssl_args} \
            app:app
    fi
}

# ==============================================================================
# SIGNAL HANDLERS
# ==============================================================================

function cleanup() {
    log_info "Received termination signal, shutting down gracefully..."
    
    # Kill background processes
    jobs -p | xargs -r kill
    
    log_info "Supervisor API Proxy stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# ==============================================================================
# PRE-FLIGHT CHECKS
# ==============================================================================

function preflight_checks() {
    log_info "Running pre-flight checks..."
    
    # Check Python version
    local python_version=$(python3 --version 2>&1)
    log_info "Python version: ${python_version}"
    
    # Check Flask installation
    if python3 -c "import flask" 2>/dev/null; then
        local flask_version=$(python3 -c "import flask; print(flask.__version__)" 2>/dev/null)
        log_info "Flask version: ${flask_version}"
    else
        log_fatal "Flask is not installed!"
        exit 1
    fi
    
    # Check required Python modules
    local required_modules=("requests" "flask_cors" "gunicorn")
    for module in "${required_modules[@]}"; do
        if python3 -c "import ${module}" 2>/dev/null; then
            log_debug "✓ ${module} module available"
        else
            log_fatal "Required Python module not found: ${module}"
            exit 1
        fi
    done
    
    # Check if app.py exists
    if [ ! -f "/app/app.py" ]; then
        log_fatal "Application file not found: /app/app.py"
        exit 1
    fi
    
    log_info "✓ Pre-flight checks completed"
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

function main() {
    # Print banner
    bashio::log.info
    bashio::log.info "-------------------------------------------"
    bashio::log.info " Home Assistant Supervisor API Proxy"
    bashio::log.info " Version: 1.0.0"
    bashio::log.info "-------------------------------------------"
    bashio::log.info
    
    # Execute startup sequence
    load_config
    preflight_checks
    validate_supervisor_token
    setup_ssl
    
    # Start the application
    start_application
}

# ==============================================================================
# ERROR HANDLING
# ==============================================================================

function error_handler() {
    local exit_code=$?
    local line_number=$1
    
    log_fatal "An error occurred on line ${line_number}. Exit code: ${exit_code}"
    log_fatal "Check the logs above for more details."
    
    exit $exit_code
}

# Set error handler
trap 'error_handler ${LINENO}' ERR

# ==============================================================================
# START APPLICATION
# ==============================================================================

# Execute main function
main "$@"