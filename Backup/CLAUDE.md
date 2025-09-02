# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Home Assistant Supervisor API Proxy** - a Flask-based RESTful API proxy that provides easy access to Home Assistant Supervisor functions. The application acts as a middleware between clients and the Home Assistant Supervisor API, offering simplified endpoints for add-on management, backups, system control, and monitoring.

## Architecture

### Single-File Flask Application
- **`app.py`**: Contains all API endpoints and business logic in one comprehensive file
- **Proxy Pattern**: All endpoints forward requests to the Home Assistant Supervisor API at `http://supervisor`
- **Decorator-based Error Handling**: Uses `@handle_supervisor_errors` decorator for consistent error handling across all endpoints

### Key Components
- **`supervisor_request()`**: Core function that handles all HTTP communication with the Supervisor API
- **API Prefix**: All endpoints are prefixed with `/api/v1`
- **Authentication**: Uses Bearer token authentication via `SUPERVISOR_TOKEN` environment variable
- **CORS Support**: Enabled for cross-origin requests

### Endpoint Categories
1. **Add-ons** (`/addons/*`) - Install, start, stop, configure add-ons
2. **Store** (`/store/*`) - Browse and install from Home Assistant Add-on Store
3. **Backups** (`/backups/*`) - Create, restore, manage full/partial backups
4. **System Info** (`/info`, `/supervisor/info`, etc.) - Get system information
5. **System Control** (`/supervisor/restart`, `/host/reboot`, etc.) - Control services
6. **Updates** (`/available_updates`, `/supervisor/update`, etc.) - Manage updates
7. **Statistics** (`/supervisor/stats`, `/core/stats`) - Resource usage monitoring
8. **Logs** (`/supervisor/logs`, `/core/logs`) - Access system logs
9. **Utility** (`/health`, `/endpoints`) - Health checks and endpoint discovery

## Development Commands

### Running the Application
```bash
# Direct Python execution
python app.py

# Using Docker
docker build -t supervisor-api-proxy .
docker run -d -p 8080:8080 -e SUPERVISOR_TOKEN="your_token" supervisor-api-proxy
```

### Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Type Checking
The code uses comprehensive type hints. Run type checking with:
```bash
mypy app.py
```

### Testing
Test the health endpoint to verify the application is running:
```bash
curl -X GET http://localhost:8080/api/v1/health
```

## Home Assistant Add-on Integration

### Configuration Files
- **`config.yaml`**: Add-on manifest with metadata and configuration schema
- **`build.yaml`**: Multi-architecture build configuration for Home Assistant add-ons
- **`run.sh`**: Startup script that handles add-on configuration and launches the Flask app
- **`Dockerfile`**: Container build instructions using Home Assistant base images

### Environment Variables
- **`SUPERVISOR_TOKEN`**: Required. Home Assistant Supervisor API token (automatically provided in add-on context)
- **`LOG_LEVEL`**: Optional. Logging level (default: info)
- **`CORS_ORIGINS`**: Optional. CORS allowed origins

## Important Implementation Details

### Error Handling Strategy
- All endpoints use the `@handle_supervisor_errors` decorator
- Returns 503 for Supervisor API unavailability
- Returns 500 for internal errors
- Provides structured error responses with details

### Request Forwarding
- Preserves HTTP methods (GET, POST, PUT, DELETE)
- Forwards JSON request bodies where applicable
- Maintains content-type headers
- Supports streaming for log endpoints

### Security Considerations
- Bearer token authentication for all Supervisor API calls
- CORS configuration available
- No credential storage in code
- Environment-based configuration

## Code Conventions

### Type Annotations
- Full type hints throughout the codebase using `typing` module
- Function parameters, return types, and variables are typed
- Uses `Union`, `Optional`, `Dict`, `List`, `Any` types appropriately

### Flask Route Patterns
- All routes follow the pattern: `@app.route(f'{API_PREFIX}/path', methods=['METHOD'])`
- Route functions are named descriptively (e.g., `get_addon_info`, `start_addon`)
- Path parameters use descriptive names (e.g., `<addon>`, `<backup>`)

### Response Handling
- Consistent JSON responses using `jsonify()`
- Status codes preserved from Supervisor API responses
- Error responses follow standard format: `{"error": "message", "details": "details"}`