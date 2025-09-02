# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Home Assistant Supervisor API Proxy Add-on** - a Flask-based REST API that provides secure external access to Home Assistant Supervisor functionality. The primary use case is enabling Android apps and other external clients to interact with the Supervisor API through a standardized REST interface.

## Architecture

### Core Components

- **`app.py`** - Main Flask application with proxy endpoints
  - Implements generic `@proxy_request` decorator for consistent API forwarding
  - All endpoints follow `/api/v1/` prefix convention
  - Comprehensive error handling with custom `ProxyError` exception
  - Streaming support for logs and long-running operations

- **`run.sh`** - Production startup script with comprehensive configuration loading
  - Uses `bashio` for Home Assistant add-on configuration management
  - Supports both development (Flask dev server) and production (Gunicorn) modes
  - SSL/TLS configuration with certificate validation
  - Supervisor token validation with connection testing

### Key Patterns

1. **Proxy Pattern**: Uses `@proxy_request('/path/{param}')` decorator to automatically forward requests to `http://supervisor`
2. **Authentication**: All requests require `Authorization: Bearer <supervisor_token>` header
3. **Error Handling**: Consistent error responses with appropriate HTTP status codes
4. **Configuration**: Environment-based config with Home Assistant add-on YAML schema

## Development Commands

### Testing
```bash
# Run all tests (creates venv automatically)
./scripts/run_tests.sh

# Run specific test types
./scripts/run_tests.sh --unit --quality
./scripts/run_tests.sh --api --integration

# Run tests with coverage analysis
./scripts/run_tests.sh --coverage
```

### Building
```bash
# Build for specific architecture
./scripts/build.sh --arch amd64

# Build for all architectures
./scripts/build.sh --multi-arch

# Build and push to registry
./scripts/build.sh --multi-arch --push

# Validate configuration only
./scripts/build.sh --validate
```

### Local Development
```bash
# Run directly (requires SUPERVISOR_TOKEN)
export SUPERVISOR_TOKEN="your_token"
export LOG_LEVEL="debug"
python3 app.py

# Or use Docker
docker build -t supervisor-proxy .
docker run -p 8099:8099 -e SUPERVISOR_TOKEN=your_token supervisor-proxy
```

## Configuration Schema

The add-on uses Home Assistant's configuration schema (`config.yaml`):

- `log_level`: trace|debug|info|notice|warning|error|fatal (default: info)
- `cors_origins`: List of allowed CORS origins (default: ["*"])  
- `port`: API server port 1024-65535 (default: 8099)
- `ssl`: Enable SSL/TLS (default: false)
- `certfile`/`keyfile`: SSL certificate files in `/ssl/` directory

## Home Assistant Integration

### Add-on Permissions
The add-on requires these capabilities (defined in `config.yaml`):
- `hassio_api: true` - Access to Supervisor API
- `homeassistant_api: true` - Access to Home Assistant API
- `supervisor: true` - Supervisor permissions
- `host_network: true` - Network access

### Environment Variables
- `SUPERVISOR_TOKEN` - Automatically provided by Home Assistant
- `LOG_LEVEL`, `PORT`, `CORS_ORIGINS` - Set from add-on configuration

## API Structure

All endpoints follow the pattern:
- Base URL: `/api/v1/`
- Categories: addons, backups, system, store, jobs
- RESTful design with appropriate HTTP methods
- Consistent error responses and status codes
- Streaming support for logs via `stream_response=True`

## Testing Framework

- **pytest** for unit and integration tests
- **Custom shell scripts** for API endpoint testing  
- **Code quality tools**: black, isort, flake8
- **Coverage analysis** with HTML reports
- **Docker build validation**

The test suite automatically creates a Python virtual environment and installs dependencies.