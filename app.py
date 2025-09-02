#!/usr/bin/env python3
"""
Home Assistant Supervisor API Proxy
A Flask-based REST API proxy for Home Assistant Supervisor
"""

import os
import sys
import logging
import json
import time
from functools import wraps
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, Optional, Tuple

import requests
from flask import Flask, request, jsonify, Response, stream_template_string
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound, InternalServerError

# Configuration
SUPERVISOR_URL = "http://supervisor"
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
PORT = int(os.getenv("PORT", 8099))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Flask app setup
app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS)

# Logging setup
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request timeout
REQUEST_TIMEOUT = 30


class ProxyError(Exception):
    """Custom exception for proxy errors"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def error_handler(func):
    """Decorator for error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ProxyError as e:
            logger.error(f"Proxy error: {e.message}")
            return jsonify({"error": e.message}), e.status_code
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return jsonify({"error": "Request timeout"}), 504
        except requests.exceptions.ConnectionError:
            logger.error("Connection error to Supervisor")
            return jsonify({"error": "Unable to connect to Supervisor"}), 503
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    return wrapper


def validate_token():
    """Validate Supervisor token"""
    if not SUPERVISOR_TOKEN:
        logger.error("SUPERVISOR_TOKEN not configured")
        raise ProxyError("Supervisor token not configured", 500)


def get_auth_headers() -> Dict[str, str]:
    """Get authorization headers for Supervisor API"""
    validate_token()
    return {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json"
    }


def make_supervisor_request(
    method: str,
    path: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    stream: bool = False
) -> Tuple[requests.Response, int]:
    """Make request to Supervisor API"""
    url = urljoin(SUPERVISOR_URL, path)
    headers = get_auth_headers()
    
    # Remove Content-Type for GET requests
    if method.upper() == "GET":
        headers.pop("Content-Type", None)
    
    logger.debug(f"Making {method} request to {url}")
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data if data else None,
            params=params,
            timeout=REQUEST_TIMEOUT,
            stream=stream
        )
        
        logger.debug(f"Supervisor response status: {response.status_code}")
        return response, response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise ProxyError(f"Request failed: {str(e)}", 502)


def proxy_request(
    supervisor_path: str,
    methods: list = None,
    stream_response: bool = False
):
    """Generic proxy request handler"""
    if methods is None:
        methods = ["GET", "POST", "PUT", "DELETE"]
    
    def decorator(func):
        @wraps(func)
        @error_handler
        def wrapper(*args, **kwargs):
            method = request.method
            if method not in methods:
                return jsonify({"error": f"Method {method} not allowed"}), 405
            
            # Get request data
            data = None
            if method in ["POST", "PUT"] and request.is_json:
                data = request.get_json()
            
            # Get query parameters
            params = dict(request.args)
            
            # Make request to Supervisor
            response, status_code = make_supervisor_request(
                method=method,
                path=supervisor_path.format(**kwargs),
                data=data,
                params=params,
                stream=stream_response
            )
            
            if stream_response:
                return Response(
                    response.iter_content(chunk_size=1024),
                    status=status_code,
                    headers=dict(response.headers),
                    mimetype=response.headers.get('content-type', 'text/plain')
                )
            
            try:
                return jsonify(response.json()), status_code
            except ValueError:
                return Response(response.text, status=status_code)
        
        return wrapper
    return decorator


# Health check endpoint
@app.route('/api/v1/health', methods=['GET'])
@error_handler
def health_check():
    """Health check endpoint"""
    try:
        # Test Supervisor connection
        response, _ = make_supervisor_request("GET", "/supervisor/ping")
        supervisor_healthy = response.status_code == 200
    except:
        supervisor_healthy = False
    
    health_status = {
        "status": "healthy" if supervisor_healthy else "unhealthy",
        "timestamp": time.time(),
        "supervisor_connection": supervisor_healthy,
        "version": "1.0.0"
    }
    
    status_code = 200 if supervisor_healthy else 503
    return jsonify(health_status), status_code


# API discovery endpoint
@app.route('/api/v1/discovery', methods=['GET'])
@error_handler
def api_discovery():
    """API endpoint discovery"""
    endpoints = {
        "health": "/api/v1/health",
        "discovery": "/api/v1/discovery",
        "addons": {
            "list": "/api/v1/addons",
            "info": "/api/v1/addons/{slug}",
            "install": "/api/v1/addons/{slug}/install",
            "uninstall": "/api/v1/addons/{slug}/uninstall",
            "start": "/api/v1/addons/{slug}/start",
            "stop": "/api/v1/addons/{slug}/stop",
            "restart": "/api/v1/addons/{slug}/restart",
            "update": "/api/v1/addons/{slug}/update",
            "logs": "/api/v1/addons/{slug}/logs",
            "stats": "/api/v1/addons/{slug}/stats"
        },
        "backups": {
            "list": "/api/v1/backups",
            "info": "/api/v1/backups/{slug}",
            "create": "/api/v1/backups",
            "restore_full": "/api/v1/backups/{slug}/restore/full",
            "restore_partial": "/api/v1/backups/{slug}/restore/partial",
            "delete": "/api/v1/backups/{slug}"
        },
        "system": {
            "supervisor": "/api/v1/supervisor/info",
            "core": "/api/v1/core/info",
            "host": "/api/v1/host/info",
            "os": "/api/v1/os/info",
            "network": "/api/v1/network/info"
        },
        "store": {
            "repositories": "/api/v1/store/repositories",
            "addons": "/api/v1/store/addons"
        },
        "jobs": {
            "list": "/api/v1/jobs",
            "info": "/api/v1/jobs/{uuid}"
        }
    }
    
    return jsonify({
        "message": "Home Assistant Supervisor API Proxy",
        "version": "1.0.0",
        "endpoints": endpoints
    })


# Add-on management endpoints
@app.route('/api/v1/addons', methods=['GET'])
@proxy_request('/addons')
def addons_list():
    """List all add-ons"""
    pass


@app.route('/api/v1/addons/<slug>', methods=['GET', 'POST'])
@proxy_request('/addons/{slug}')
def addon_info(slug):
    """Get or update add-on information"""
    pass


@app.route('/api/v1/addons/<slug>/install', methods=['POST'])
@proxy_request('/addons/{slug}/install', methods=['POST'])
def addon_install(slug):
    """Install add-on"""
    pass


@app.route('/api/v1/addons/<slug>/uninstall', methods=['POST'])
@proxy_request('/addons/{slug}/uninstall', methods=['POST'])
def addon_uninstall(slug):
    """Uninstall add-on"""
    pass


@app.route('/api/v1/addons/<slug>/start', methods=['POST'])
@proxy_request('/addons/{slug}/start', methods=['POST'])
def addon_start(slug):
    """Start add-on"""
    pass


@app.route('/api/v1/addons/<slug>/stop', methods=['POST'])
@proxy_request('/addons/{slug}/stop', methods=['POST'])
def addon_stop(slug):
    """Stop add-on"""
    pass


@app.route('/api/v1/addons/<slug>/restart', methods=['POST'])
@proxy_request('/addons/{slug}/restart', methods=['POST'])
def addon_restart(slug):
    """Restart add-on"""
    pass


@app.route('/api/v1/addons/<slug>/update', methods=['POST'])
@proxy_request('/addons/{slug}/update', methods=['POST'])
def addon_update(slug):
    """Update add-on"""
    pass


@app.route('/api/v1/addons/<slug>/logs', methods=['GET'])
@proxy_request('/addons/{slug}/logs', stream_response=True)
def addon_logs(slug):
    """Get add-on logs with streaming support"""
    pass


@app.route('/api/v1/addons/<slug>/stats', methods=['GET'])
@proxy_request('/addons/{slug}/stats')
def addon_stats(slug):
    """Get add-on statistics"""
    pass


# Backup management endpoints
@app.route('/api/v1/backups', methods=['GET', 'POST'])
@proxy_request('/backups')
def backups():
    """List backups or create new backup"""
    pass


@app.route('/api/v1/backups/<slug>', methods=['GET', 'DELETE'])
@proxy_request('/backups/{slug}')
def backup_info(slug):
    """Get backup info or delete backup"""
    pass


@app.route('/api/v1/backups/<slug>/restore/full', methods=['POST'])
@proxy_request('/backups/{slug}/restore/full', methods=['POST'])
def backup_restore_full(slug):
    """Full backup restore"""
    pass


@app.route('/api/v1/backups/<slug>/restore/partial', methods=['POST'])
@proxy_request('/backups/{slug}/restore/partial', methods=['POST'])
def backup_restore_partial(slug):
    """Partial backup restore"""
    pass


# System information endpoints
@app.route('/api/v1/supervisor/info', methods=['GET'])
@proxy_request('/supervisor/info')
def supervisor_info():
    """Get Supervisor information"""
    pass


@app.route('/api/v1/supervisor/update', methods=['POST'])
@proxy_request('/supervisor/update', methods=['POST'])
def supervisor_update():
    """Update Supervisor"""
    pass


@app.route('/api/v1/core/info', methods=['GET'])
@proxy_request('/core/info')
def core_info():
    """Get Home Assistant Core information"""
    pass


@app.route('/api/v1/core/update', methods=['POST'])
@proxy_request('/core/update', methods=['POST'])
def core_update():
    """Update Home Assistant Core"""
    pass


@app.route('/api/v1/core/restart', methods=['POST'])
@proxy_request('/core/restart', methods=['POST'])
def core_restart():
    """Restart Home Assistant Core"""
    pass


@app.route('/api/v1/host/info', methods=['GET'])
@proxy_request('/host/info')
def host_info():
    """Get host information"""
    pass


@app.route('/api/v1/host/reboot', methods=['POST'])
@proxy_request('/host/reboot', methods=['POST'])
def host_reboot():
    """Reboot host"""
    pass


@app.route('/api/v1/host/shutdown', methods=['POST'])
@proxy_request('/host/shutdown', methods=['POST'])
def host_shutdown():
    """Shutdown host"""
    pass


@app.route('/api/v1/os/info', methods=['GET'])
@proxy_request('/os/info')
def os_info():
    """Get OS information"""
    pass


@app.route('/api/v1/os/update', methods=['POST'])
@proxy_request('/os/update', methods=['POST'])
def os_update():
    """Update OS"""
    pass


@app.route('/api/v1/network/info', methods=['GET'])
@proxy_request('/network/info')
def network_info():
    """Get network information"""
    pass


# Store endpoints
@app.route('/api/v1/store/repositories', methods=['GET', 'POST'])
@proxy_request('/store/repositories')
def store_repositories():
    """List or add repositories"""
    pass


@app.route('/api/v1/store/repositories/<slug>', methods=['DELETE'])
@proxy_request('/store/repositories/{slug}', methods=['DELETE'])
def store_repository_delete(slug):
    """Delete repository"""
    pass


@app.route('/api/v1/store/addons', methods=['GET'])
@proxy_request('/store/addons')
def store_addons():
    """List store add-ons"""
    pass


@app.route('/api/v1/store/addons/<slug>', methods=['GET'])
@proxy_request('/store/addons/{slug}')
def store_addon_info(slug):
    """Get store add-on information"""
    pass


# Job management endpoints
@app.route('/api/v1/jobs', methods=['GET'])
@proxy_request('/jobs')
def jobs_list():
    """List jobs"""
    pass


@app.route('/api/v1/jobs/<uuid>', methods=['GET'])
@proxy_request('/jobs/{uuid}')
def job_info(uuid):
    """Get job information"""
    pass


# Audio endpoints
@app.route('/api/v1/audio/info', methods=['GET'])
@proxy_request('/audio/info')
def audio_info():
    """Get audio information"""
    pass


# DNS endpoints
@app.route('/api/v1/dns/info', methods=['GET'])
@proxy_request('/dns/info')
def dns_info():
    """Get DNS information"""
    pass


@app.route('/api/v1/dns/options', methods=['POST'])
@proxy_request('/dns/options', methods=['POST'])
def dns_options():
    """Set DNS options"""
    pass


# Services endpoints  
@app.route('/api/v1/services', methods=['GET'])
@proxy_request('/services')
def services_list():
    """List services"""
    pass


@app.route('/api/v1/services/<service>', methods=['GET'])
@proxy_request('/services/{service}')
def service_info(service):
    """Get service information"""
    pass


# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Startup validation
def validate_environment():
    """Validate required environment variables"""
    if not SUPERVISOR_TOKEN:
        logger.error("SUPERVISOR_TOKEN environment variable is required")
        sys.exit(1)
    
    logger.info(f"Supervisor API Proxy starting on port {PORT}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")
    logger.info(f"Log level: {LOG_LEVEL}")


if __name__ == '__main__':
    validate_environment()
    
    # Development server
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=(LOG_LEVEL == "DEBUG")
    )