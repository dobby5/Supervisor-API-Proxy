#!/usr/bin/env python3
import os
import sys
import logging
import time
from functools import wraps
from urllib.parse import urljoin
from typing import Dict, Any, Optional, Tuple, List, Callable, Union

import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Configuration
SUPERVISOR_URL = "http://supervisor"
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
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


def error_handler(func: Callable[..., Any]) -> Callable[..., Union[Tuple[Response, int], Response]]:
    """Decorator for error handling"""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[Tuple[Response, int], Response]:
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


def validate_token() -> None:
    """Validate Supervisor token"""
    if not SUPERVISOR_TOKEN:
        logger.error("SUPERVISOR_TOKEN not configured")
        raise ProxyError("Supervisor token not configured", 500)
    
    # Log token info for debugging (first/last 5 chars only)
    token_preview = f"{SUPERVISOR_TOKEN[:5]}...{SUPERVISOR_TOKEN[-5:]}" if len(SUPERVISOR_TOKEN) > 10 else "***"
    logger.debug(f"Using Supervisor token: {token_preview}")


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
        
        # Log detailed error info for debugging
        if response.status_code >= 400:
            logger.error(f"Supervisor API error {response.status_code} for {method} {url}")
            logger.error(f"Request headers: {headers}")
            try:
                error_body = response.text
                logger.error(f"Response body: {error_body}")
            except:
                logger.error("Could not read response body")
                
        return response, response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise ProxyError(f"Request failed: {str(e)}", 502)


def proxy_request(
    supervisor_path: str,
    methods: Optional[List[str]] = None,
    stream_response: bool = False
) -> Callable[[Callable[..., Any]], Callable[..., Union[Tuple[Response, int], Response]]]:
    """Generic proxy request handler"""
    if methods is None:
        methods = ["GET", "POST", "PUT", "DELETE"]
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Union[Tuple[Response, int], Response]]:
        @wraps(func)
        @error_handler
        def wrapper(*args: Any, **kwargs: Any) -> Union[Tuple[Response, int], Response]:
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
def health_check() -> Tuple[Response, int]:
    """Health check endpoint"""
    try:
        # Test Supervisor connection
        response, _ = make_supervisor_request("GET", "/supervisor/ping")
        supervisor_healthy = response.status_code == 200
    except:
        supervisor_healthy = False
    
    health_status: Dict[str, Any] = {
        "status": "healthy" if supervisor_healthy else "unhealthy",
        "timestamp": time.time(),
        "supervisor_connection": supervisor_healthy,
        "version": "1.0.0"
    }
    
    status_code = 200 if supervisor_healthy else 503
    return jsonify(health_status), status_code


# Debug endpoint for testing supervisor access
@app.route('/api/v1/debug/supervisor', methods=['GET'])
@error_handler
def debug_supervisor() -> Tuple[Response, int]:
    """Debug endpoint to test different supervisor endpoints"""
    results = {}
    test_endpoints = [
        "/supervisor/ping",
        "/supervisor/info", 
        "/addons",
        "/core/info"
    ]
    
    for endpoint in test_endpoints:
        try:
            response, status = make_supervisor_request("GET", endpoint)
            results[endpoint] = {
                "status": status,
                "success": status < 400,
                "response_length": len(response.text) if hasattr(response, 'text') else 0
            }
            if status >= 400:
                results[endpoint]["error"] = response.text[:200]  # First 200 chars
        except Exception as e:
            results[endpoint] = {
                "status": "error",
                "success": False,
                "error": str(e)
            }
    
    return jsonify({
        "supervisor_token_configured": bool(SUPERVISOR_TOKEN),
        "supervisor_url": SUPERVISOR_URL,
        "test_results": results
    }), 200


# API discovery endpoint
@app.route('/api/v1/discovery', methods=['GET'])
@error_handler
def api_discovery() -> Tuple[Response, int]:
    """API endpoint discovery"""
    endpoints: Dict[str, Any] = {
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
            "stats": "/api/v1/addons/{slug}/stats",
            "reload": "/api/v1/addons/reload",
            "changelog": "/api/v1/addons/{slug}/changelog",
            "documentation": "/api/v1/addons/{slug}/documentation",
            "icon": "/api/v1/addons/{slug}/icon",
            "logo": "/api/v1/addons/{slug}/logo",
            "options": "/api/v1/addons/{slug}/options",
            "options_validate": "/api/v1/addons/{slug}/options/validate",
            "rebuild": "/api/v1/addons/{slug}/rebuild",
            "security": "/api/v1/addons/{slug}/security",
            "stdin": "/api/v1/addons/{slug}/stdin"
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
        },
        "auth": {
            "authenticate": "/api/v1/auth",
            "reset": "/api/v1/auth/reset"
        },
        "hardware": {
            "info": "/api/v1/hardware/info",
            "audio": "/api/v1/hardware/audio"
        },
        "resolution": {
            "info": "/api/v1/resolution/info",
            "suggestions": "/api/v1/resolution/suggestions"
        },
        "security": {
            "info": "/api/v1/security/info"
        },
        "ingress": {
            "panels": "/api/v1/ingress/panels",
            "session": "/api/v1/ingress/session"
        }
    }
    
    return jsonify({
        "message": "Home Assistant Supervisor API Proxy",
        "version": "1.0.0",
        "endpoints": endpoints
    }), 200


# Add-on management endpoints
@app.route('/api/v1/addons', methods=['GET'])
@proxy_request('/addons')
def addons_list() -> None:
    """List all add-ons"""
    pass


@app.route('/api/v1/addons/reload', methods=['POST'])
@proxy_request('/addons/reload', methods=['POST'])
def addons_reload() -> None:
    """Reload add-ons"""
    pass


@app.route('/api/v1/addons/<slug>', methods=['GET', 'POST'])
@proxy_request('/addons/{slug}')
def addon_info(slug: str) -> None:
    """Get or update add-on information"""
    pass


@app.route('/api/v1/addons/<slug>/install', methods=['POST'])
@proxy_request('/addons/{slug}/install', methods=['POST'])
def addon_install(slug: str) -> None:
    """Install add-on"""
    pass


@app.route('/api/v1/addons/<slug>/uninstall', methods=['POST'])
@proxy_request('/addons/{slug}/uninstall', methods=['POST'])
def addon_uninstall(slug: str) -> None:
    """Uninstall add-on"""
    pass


@app.route('/api/v1/addons/<slug>/start', methods=['POST'])
@proxy_request('/addons/{slug}/start', methods=['POST'])
def addon_start(slug: str) -> None:
    """Start add-on"""
    pass


@app.route('/api/v1/addons/<slug>/stop', methods=['POST'])
@proxy_request('/addons/{slug}/stop', methods=['POST'])
def addon_stop(slug: str) -> None:
    """Stop add-on"""
    pass


@app.route('/api/v1/addons/<slug>/restart', methods=['POST'])
@proxy_request('/addons/{slug}/restart', methods=['POST'])
def addon_restart(slug: str) -> None:
    """Restart add-on"""
    pass


@app.route('/api/v1/addons/<slug>/update', methods=['POST'])
@proxy_request('/addons/{slug}/update', methods=['POST'])
def addon_update(slug: str) -> None:
    """Update add-on"""
    pass


@app.route('/api/v1/addons/<slug>/logs', methods=['GET'])
@proxy_request('/addons/{slug}/logs', stream_response=True)
def addon_logs(slug: str) -> None:
    """Get add-on logs with streaming support"""
    pass


@app.route('/api/v1/addons/<slug>/stats', methods=['GET'])
@proxy_request('/addons/{slug}/stats')
def addon_stats(slug: str) -> None:
    """Get add-on statistics"""
    pass


@app.route('/api/v1/addons/<slug>/changelog', methods=['GET'])
@proxy_request('/addons/{slug}/changelog')
def addon_changelog(slug: str) -> None:
    """Get add-on changelog"""
    pass


@app.route('/api/v1/addons/<slug>/documentation', methods=['GET'])
@proxy_request('/addons/{slug}/documentation')
def addon_documentation(slug: str) -> None:
    """Get add-on documentation"""
    pass


@app.route('/api/v1/addons/<slug>/icon', methods=['GET'])
@proxy_request('/addons/{slug}/icon')
def addon_icon(slug: str) -> None:
    """Get add-on icon"""
    pass


@app.route('/api/v1/addons/<slug>/logo', methods=['GET'])
@proxy_request('/addons/{slug}/logo')
def addon_logo(slug: str) -> None:
    """Get add-on logo"""
    pass


@app.route('/api/v1/addons/<slug>/options', methods=['POST'])
@proxy_request('/addons/{slug}/options', methods=['POST'])
def addon_options(slug: str) -> None:
    """Set add-on options"""
    pass


@app.route('/api/v1/addons/<slug>/options/validate', methods=['POST'])
@proxy_request('/addons/{slug}/options/validate', methods=['POST'])
def addon_options_validate(slug: str) -> None:
    """Validate add-on options"""
    pass


@app.route('/api/v1/addons/<slug>/rebuild', methods=['POST'])
@proxy_request('/addons/{slug}/rebuild', methods=['POST'])
def addon_rebuild(slug: str) -> None:
    """Rebuild add-on"""
    pass


@app.route('/api/v1/addons/<slug>/security', methods=['POST'])
@proxy_request('/addons/{slug}/security', methods=['POST'])
def addon_security(slug: str) -> None:
    """Set add-on security options"""
    pass


@app.route('/api/v1/addons/<slug>/stdin', methods=['POST'])
@proxy_request('/addons/{slug}/stdin', methods=['POST'])
def addon_stdin(slug: str) -> None:
    """Send stdin to add-on"""
    pass


# Backup management endpoints
@app.route('/api/v1/backups', methods=['GET'])
@proxy_request('/backups')
def backups_list() -> None:
    """List backups"""
    pass


@app.route('/api/v1/backups/new/full', methods=['POST'])
@proxy_request('/backups/new/full', methods=['POST'])
def backup_create_full() -> None:
    """Create full backup"""
    pass


@app.route('/api/v1/backups/new/partial', methods=['POST'])
@proxy_request('/backups/new/partial', methods=['POST'])
def backup_create_partial() -> None:
    """Create partial backup"""
    pass


@app.route('/api/v1/backups/<slug>', methods=['GET', 'DELETE'])
@proxy_request('/backups/{slug}')
def backup_info(slug: str) -> None:
    """Get backup info or delete backup"""
    pass


@app.route('/api/v1/backups/<slug>/download', methods=['GET'])
@proxy_request('/backups/{slug}/download')
def backup_download(slug: str) -> None:
    """Download backup"""
    pass


@app.route('/api/v1/backups/<slug>/restore/full', methods=['POST'])
@proxy_request('/backups/{slug}/restore/full', methods=['POST'])
def backup_restore_full(slug: str) -> None:
    """Full backup restore"""
    pass


@app.route('/api/v1/backups/<slug>/restore/partial', methods=['POST'])
@proxy_request('/backups/{slug}/restore/partial', methods=['POST'])
def backup_restore_partial(slug: str) -> None:
    """Partial backup restore"""
    pass


@app.route('/api/v1/backups/info', methods=['GET'])
@proxy_request('/backups/info')
def backups_info() -> None:
    """Get backups info"""
    pass


@app.route('/api/v1/backups/options', methods=['POST'])
@proxy_request('/backups/options', methods=['POST'])
def backups_options() -> None:
    """Set backup options"""
    pass


@app.route('/api/v1/backups/reload', methods=['POST'])
@proxy_request('/backups/reload', methods=['POST'])
def backups_reload() -> None:
    """Reload backups"""
    pass


# System information endpoints
@app.route('/api/v1/supervisor/info', methods=['GET'])
@proxy_request('/supervisor/info')
def supervisor_info() -> None:
    """Get Supervisor information"""
    pass


@app.route('/api/v1/supervisor/update', methods=['POST'])
@proxy_request('/supervisor/update', methods=['POST'])
def supervisor_update() -> None:
    """Update Supervisor"""
    pass


@app.route('/api/v1/core/api', methods=['GET', 'POST'])
@proxy_request('/core/api')
def core_api() -> None:
    """Core API access"""
    pass


@app.route('/api/v1/core/check', methods=['POST'])
@proxy_request('/core/check', methods=['POST'])
def core_check() -> None:
    """Check Core"""
    pass


@app.route('/api/v1/core/info', methods=['GET'])
@proxy_request('/core/info')
def core_info() -> None:
    """Get Home Assistant Core information"""
    pass


@app.route('/api/v1/core/logs', methods=['GET'])
@proxy_request('/core/logs')
def core_logs() -> None:
    """Get Core logs"""
    pass


@app.route('/api/v1/core/options', methods=['POST'])
@proxy_request('/core/options', methods=['POST'])
def core_options() -> None:
    """Set Core options"""
    pass


@app.route('/api/v1/core/stats', methods=['GET'])
@proxy_request('/core/stats')
def core_stats() -> None:
    """Get Core statistics"""
    pass


@app.route('/api/v1/core/update', methods=['POST'])
@proxy_request('/core/update', methods=['POST'])
def core_update() -> None:
    """Update Home Assistant Core"""
    pass


@app.route('/api/v1/core/restart', methods=['POST'])
@proxy_request('/core/restart', methods=['POST'])
def core_restart() -> None:
    """Restart Home Assistant Core"""
    pass


@app.route('/api/v1/host/info', methods=['GET'])
@proxy_request('/host/info')
def host_info() -> None:
    """Get host information"""
    pass


@app.route('/api/v1/host/logs', methods=['GET'])
@proxy_request('/host/logs')
def host_logs() -> None:
    """Get host logs"""
    pass


@app.route('/api/v1/host/options', methods=['POST'])
@proxy_request('/host/options', methods=['POST'])
def host_options() -> None:
    """Set host options"""
    pass


@app.route('/api/v1/host/services', methods=['GET'])
@proxy_request('/host/services')
def host_services() -> None:
    """Get host services"""
    pass


@app.route('/api/v1/host/reboot', methods=['POST'])
@proxy_request('/host/reboot', methods=['POST'])
def host_reboot() -> None:
    """Reboot host"""
    pass


@app.route('/api/v1/host/shutdown', methods=['POST'])
@proxy_request('/host/shutdown', methods=['POST'])
def host_shutdown() -> None:
    """Shutdown host"""
    pass


@app.route('/api/v1/os/info', methods=['GET'])
@proxy_request('/os/info')
def os_info() -> None:
    """Get OS information"""
    pass


@app.route('/api/v1/os/update', methods=['POST'])
@proxy_request('/os/update', methods=['POST'])
def os_update() -> None:
    """Update OS"""
    pass


@app.route('/api/v1/os/config/sync', methods=['POST'])
@proxy_request('/os/config/sync', methods=['POST'])
def os_config_sync() -> None:
    """Sync OS config"""
    pass


@app.route('/api/v1/os/boot-slot', methods=['POST'])
@proxy_request('/os/boot-slot', methods=['POST'])
def os_boot_slot() -> None:
    """Set OS boot slot"""
    pass


@app.route('/api/v1/os/config/swap', methods=['GET', 'POST'])
@proxy_request('/os/config/swap')
def os_config_swap() -> None:
    """Get or set OS swap config"""
    pass


@app.route('/api/v1/os/datadisk/list', methods=['GET'])
@proxy_request('/os/datadisk/list')
def os_datadisk_list() -> None:
    """List OS data disks"""
    pass


@app.route('/api/v1/os/datadisk/move', methods=['POST'])
@proxy_request('/os/datadisk/move', methods=['POST'])
def os_datadisk_move() -> None:
    """Move OS data disk"""
    pass


@app.route('/api/v1/os/datadisk/wipe', methods=['POST'])
@proxy_request('/os/datadisk/wipe', methods=['POST'])
def os_datadisk_wipe() -> None:
    """Wipe OS data disk"""
    pass


@app.route('/api/v1/os/boards/<board>', methods=['GET'])
@proxy_request('/os/boards/{board}')
def os_board_info(board: str) -> None:
    """Get OS board information"""
    pass


@app.route('/api/v1/os/boards/yellow', methods=['GET', 'POST'])
@proxy_request('/os/boards/yellow')
def os_boards_yellow() -> None:
    """Yellow board operations"""
    pass


@app.route('/api/v1/os/boards/green', methods=['GET', 'POST'])
@proxy_request('/os/boards/green')
def os_boards_green() -> None:
    """Green board operations"""
    pass


@app.route('/api/v1/network/info', methods=['GET'])
@proxy_request('/network/info')
def network_info() -> None:
    """Get network information"""
    pass


@app.route('/api/v1/network/reload', methods=['POST'])
@proxy_request('/network/reload', methods=['POST'])
def network_reload() -> None:
    """Reload network"""
    pass


@app.route('/api/v1/network/interface/<interface>/info', methods=['GET'])
@proxy_request('/network/interface/{interface}/info')
def network_interface_info(interface: str) -> None:
    """Get network interface information"""
    pass


@app.route('/api/v1/network/interface/<interface>/update', methods=['POST'])
@proxy_request('/network/interface/{interface}/update', methods=['POST'])
def network_interface_update(interface: str) -> None:
    """Update network interface"""
    pass


@app.route('/api/v1/network/interface/<interface>/accesspoints', methods=['GET'])
@proxy_request('/network/interface/{interface}/accesspoints')
def network_interface_accesspoints(interface: str) -> None:
    """Get network interface access points"""
    pass


@app.route('/api/v1/network/interface/<interface>/vlan/<vlan_id>', methods=['POST'])
@proxy_request('/network/interface/{interface}/vlan/{vlan_id}', methods=['POST'])
def network_interface_vlan(interface: str, vlan_id: str) -> None:
    """Configure network interface VLAN"""
    pass


# Store endpoints
@app.route('/api/v1/store', methods=['GET'])
@proxy_request('/store')
def store_info() -> None:
    """Get store information"""
    pass


@app.route('/api/v1/store/repositories', methods=['GET', 'POST'])
@proxy_request('/store/repositories')
def store_repositories() -> None:
    """List or add repositories"""
    pass


@app.route('/api/v1/store/repositories/<slug>', methods=['DELETE'])
@proxy_request('/store/repositories/{slug}', methods=['DELETE'])
def store_repository_delete(slug: str) -> None:
    """Delete repository"""
    pass


@app.route('/api/v1/store/addons', methods=['GET'])
@proxy_request('/store/addons')
def store_addons() -> None:
    """List store add-ons"""
    pass


@app.route('/api/v1/store/addons/<slug>', methods=['GET'])
@proxy_request('/store/addons/{slug}')
def store_addon_info(slug: str) -> None:
    """Get store add-on information"""
    pass


@app.route('/api/v1/store/addons/<slug>/install', methods=['POST'])
@proxy_request('/store/addons/{slug}/install', methods=['POST'])
def store_addon_install(slug: str) -> None:
    """Install store add-on"""
    pass


@app.route('/api/v1/store/addons/<slug>/update', methods=['POST'])
@proxy_request('/store/addons/{slug}/update', methods=['POST'])
def store_addon_update(slug: str) -> None:
    """Update store add-on"""
    pass


@app.route('/api/v1/store/addons/<slug>/changelog', methods=['GET'])
@proxy_request('/store/addons/{slug}/changelog')
def store_addon_changelog(slug: str) -> None:
    """Get store add-on changelog"""
    pass


@app.route('/api/v1/store/addons/<slug>/documentation', methods=['GET'])
@proxy_request('/store/addons/{slug}/documentation')
def store_addon_documentation(slug: str) -> None:
    """Get store add-on documentation"""
    pass


@app.route('/api/v1/store/addons/<slug>/icon', methods=['GET'])
@proxy_request('/store/addons/{slug}/icon')
def store_addon_icon(slug: str) -> None:
    """Get store add-on icon"""
    pass


# Job management endpoints
@app.route('/api/v1/jobs', methods=['GET'])
@proxy_request('/jobs')
def jobs_list() -> None:
    """List jobs"""
    pass


@app.route('/api/v1/jobs/info', methods=['GET'])
@proxy_request('/jobs/info')
def jobs_info() -> None:
    """Get jobs info"""
    pass


@app.route('/api/v1/jobs/options', methods=['POST'])
@proxy_request('/jobs/options', methods=['POST'])
def jobs_options() -> None:
    """Set jobs options"""
    pass


@app.route('/api/v1/jobs/reset', methods=['POST'])
@proxy_request('/jobs/reset', methods=['POST'])
def jobs_reset() -> None:
    """Reset jobs"""
    pass


@app.route('/api/v1/jobs/<uuid>', methods=['GET'])
@proxy_request('/jobs/{uuid}')
def job_info(uuid: str) -> None:
    """Get job information"""
    pass


# Audio endpoints
@app.route('/api/v1/audio/info', methods=['GET'])
@proxy_request('/audio/info')
def audio_info() -> None:
    """Get audio information"""
    pass


@app.route('/api/v1/audio/logs', methods=['GET'])
@proxy_request('/audio/logs')
def audio_logs() -> None:
    """Get audio logs"""
    pass


@app.route('/api/v1/audio/default/input', methods=['POST'])
@proxy_request('/audio/default/input', methods=['POST'])
def audio_default_input() -> None:
    """Set default audio input"""
    pass


@app.route('/api/v1/audio/default/output', methods=['POST'])
@proxy_request('/audio/default/output', methods=['POST'])
def audio_default_output() -> None:
    """Set default audio output"""
    pass


@app.route('/api/v1/audio/mute/input', methods=['POST'])
@proxy_request('/audio/mute/input', methods=['POST'])
def audio_mute_input() -> None:
    """Mute audio input"""
    pass


@app.route('/api/v1/audio/mute/output', methods=['POST'])
@proxy_request('/audio/mute/output', methods=['POST'])
def audio_mute_output() -> None:
    """Mute audio output"""
    pass


@app.route('/api/v1/audio/volume/input', methods=['POST'])
@proxy_request('/audio/volume/input', methods=['POST'])
def audio_volume_input() -> None:
    """Set audio input volume"""
    pass


@app.route('/api/v1/audio/volume/output', methods=['POST'])
@proxy_request('/audio/volume/output', methods=['POST'])
def audio_volume_output() -> None:
    """Set audio output volume"""
    pass


@app.route('/api/v1/audio/profile', methods=['POST'])
@proxy_request('/audio/profile', methods=['POST'])
def audio_profile() -> None:
    """Set audio profile"""
    pass


@app.route('/api/v1/audio/reload', methods=['POST'])
@proxy_request('/audio/reload', methods=['POST'])
def audio_reload() -> None:
    """Reload audio"""
    pass


@app.route('/api/v1/audio/restart', methods=['POST'])
@proxy_request('/audio/restart', methods=['POST'])
def audio_restart() -> None:
    """Restart audio"""
    pass


@app.route('/api/v1/audio/update', methods=['POST'])
@proxy_request('/audio/update', methods=['POST'])
def audio_update() -> None:
    """Update audio"""
    pass


# Discovery endpoints
@app.route('/api/v1/discovery', methods=['GET', 'POST'])
@proxy_request('/discovery')
def discovery() -> None:
    """Get or add discoveries"""
    pass


@app.route('/api/v1/discovery/<uuid>', methods=['GET', 'DELETE'])
@proxy_request('/discovery/{uuid}')
def discovery_item(uuid: str) -> None:
    """Get or delete discovery"""
    pass


# DNS endpoints
@app.route('/api/v1/dns/info', methods=['GET'])
@proxy_request('/dns/info')
def dns_info() -> None:
    """Get DNS information"""
    pass


@app.route('/api/v1/dns/logs', methods=['GET'])
@proxy_request('/dns/logs')
def dns_logs() -> None:
    """Get DNS logs"""
    pass


@app.route('/api/v1/dns/options', methods=['POST'])
@proxy_request('/dns/options', methods=['POST'])
def dns_options() -> None:
    """Set DNS options"""
    pass


@app.route('/api/v1/dns/restart', methods=['POST'])
@proxy_request('/dns/restart', methods=['POST'])
def dns_restart() -> None:
    """Restart DNS"""
    pass


@app.route('/api/v1/dns/stats', methods=['GET'])
@proxy_request('/dns/stats')
def dns_stats() -> None:
    """Get DNS statistics"""
    pass


@app.route('/api/v1/dns/update', methods=['POST'])
@proxy_request('/dns/update', methods=['POST'])
def dns_update() -> None:
    """Update DNS"""
    pass


# Services endpoints  
@app.route('/api/v1/services', methods=['GET'])
@proxy_request('/services')
def services_list() -> None:
    """List services"""
    pass


@app.route('/api/v1/services/<service>', methods=['GET'])
@proxy_request('/services/{service}')
def service_info(service: str) -> None:
    """Get service information"""
    pass


@app.route('/api/v1/services/mqtt', methods=['GET', 'POST', 'DELETE'])
@proxy_request('/services/mqtt')
def services_mqtt() -> None:
    """MQTT service operations"""
    pass


@app.route('/api/v1/services/mysql', methods=['GET', 'POST', 'DELETE'])
@proxy_request('/services/mysql')
def services_mysql() -> None:
    """MySQL service operations"""
    pass


# Auth endpoints
@app.route('/api/v1/auth', methods=['POST'])
@proxy_request('/auth', methods=['POST'])
def auth() -> None:
    """Authenticate"""
    pass


@app.route('/api/v1/auth/reset', methods=['POST'])
@proxy_request('/auth/reset', methods=['POST'])
def auth_reset() -> None:
    """Reset authentication"""
    pass


@app.route('/api/v1/auth', methods=['GET'])
@proxy_request('/auth')
def auth_info() -> None:
    """Get auth info"""
    pass


@app.route('/api/v1/auth/cache', methods=['DELETE'])
@proxy_request('/auth/cache', methods=['DELETE'])
def auth_cache_delete() -> None:
    """Delete auth cache"""
    pass


@app.route('/api/v1/auth/list', methods=['GET'])
@proxy_request('/auth/list')
def auth_list() -> None:
    """List auth entries"""
    pass


# Hardware endpoints
@app.route('/api/v1/hardware/info', methods=['GET'])
@proxy_request('/hardware/info')
def hardware_info() -> None:
    """Get hardware information"""
    pass


@app.route('/api/v1/hardware/audio', methods=['GET'])
@proxy_request('/hardware/audio')
def hardware_audio() -> None:
    """Get audio hardware information"""
    pass


# Resolution endpoints
@app.route('/api/v1/resolution/info', methods=['GET'])
@proxy_request('/resolution/info')
def resolution_info() -> None:
    """Get resolution information"""
    pass


@app.route('/api/v1/resolution/suggestions', methods=['GET'])
@proxy_request('/resolution/suggestions')
def resolution_suggestions() -> None:
    """Get resolution suggestions"""
    pass


@app.route('/api/v1/resolution/suggestion/<uuid>', methods=['POST', 'DELETE'])
@proxy_request('/resolution/suggestion/{uuid}')
def resolution_suggestion(uuid: str) -> None:
    """Handle resolution suggestion"""
    pass


@app.route('/api/v1/resolution/issue/<uuid>/suggestions', methods=['GET'])
@proxy_request('/resolution/issue/{uuid}/suggestions')
def resolution_issue_suggestions(uuid: str) -> None:
    """Get resolution issue suggestions"""
    pass


@app.route('/api/v1/resolution/issue/<uuid>', methods=['DELETE'])
@proxy_request('/resolution/issue/{uuid}', methods=['DELETE'])
def resolution_issue_delete(uuid: str) -> None:
    """Delete resolution issue"""
    pass


@app.route('/api/v1/resolution/healthcheck', methods=['POST'])
@proxy_request('/resolution/healthcheck', methods=['POST'])
def resolution_healthcheck() -> None:
    """Run resolution healthcheck"""
    pass


@app.route('/api/v1/resolution/check/<slug>/options', methods=['POST'])
@proxy_request('/resolution/check/{slug}/options', methods=['POST'])
def resolution_check_options(slug: str) -> None:
    """Set resolution check options"""
    pass


@app.route('/api/v1/resolution/check/<slug>/run', methods=['POST'])
@proxy_request('/resolution/check/{slug}/run', methods=['POST'])
def resolution_check_run(slug: str) -> None:
    """Run resolution check"""
    pass


# Supervisor category endpoints
@app.route('/api/v1/supervisor/logs', methods=['GET'])
@proxy_request('/supervisor/logs')
def supervisor_logs() -> None:
    """Get Supervisor logs"""
    pass


@app.route('/api/v1/supervisor/options', methods=['POST'])
@proxy_request('/supervisor/options', methods=['POST'])
def supervisor_options() -> None:
    """Set Supervisor options"""
    pass


@app.route('/api/v1/supervisor/reload', methods=['POST'])
@proxy_request('/supervisor/reload', methods=['POST'])
def supervisor_reload() -> None:
    """Reload Supervisor"""
    pass


@app.route('/api/v1/supervisor/repair', methods=['POST'])
@proxy_request('/supervisor/repair', methods=['POST'])
def supervisor_repair() -> None:
    """Repair Supervisor"""
    pass


@app.route('/api/v1/supervisor/restart', methods=['POST'])
@proxy_request('/supervisor/restart', methods=['POST'])
def supervisor_restart() -> None:
    """Restart Supervisor"""
    pass


@app.route('/api/v1/supervisor/stats', methods=['GET'])
@proxy_request('/supervisor/stats')
def supervisor_stats() -> None:
    """Get Supervisor statistics"""
    pass


# Security endpoints
@app.route('/api/v1/security/info', methods=['GET'])
@proxy_request('/security/info')
def security_info() -> None:
    """Get security information"""
    pass


# Ingress endpoints
@app.route('/api/v1/ingress/panels', methods=['GET'])
@proxy_request('/ingress/panels')
def ingress_panels() -> None:
    """List ingress panels"""
    pass


@app.route('/api/v1/ingress/session', methods=['POST'])
@proxy_request('/ingress/session', methods=['POST'])
def ingress_session() -> None:
    """Create ingress session"""
    pass


@app.route('/api/v1/ingress/validate_session', methods=['POST'])
@proxy_request('/ingress/validate_session', methods=['POST'])
def ingress_validate_session() -> None:
    """Validate ingress session"""
    pass


# CLI endpoints
@app.route('/api/v1/cli/info', methods=['GET'])
@proxy_request('/cli/info')
def cli_info() -> None:
    """Get CLI information"""
    pass


@app.route('/api/v1/cli/stats', methods=['GET'])
@proxy_request('/cli/stats')
def cli_stats() -> None:
    """Get CLI statistics"""
    pass


@app.route('/api/v1/cli/update', methods=['POST'])
@proxy_request('/cli/update', methods=['POST'])
def cli_update() -> None:
    """Update CLI"""
    pass


# Docker endpoints
@app.route('/api/v1/docker/info', methods=['GET'])
@proxy_request('/docker/info')
def docker_info() -> None:
    """Get Docker information"""
    pass


@app.route('/api/v1/docker/options', methods=['POST'])
@proxy_request('/docker/options', methods=['POST'])
def docker_options() -> None:
    """Set Docker options"""
    pass


@app.route('/api/v1/docker/registries', methods=['GET', 'POST'])
@proxy_request('/docker/registries')
def docker_registries() -> None:
    """Get or add Docker registries"""
    pass


@app.route('/api/v1/docker/registries/<registry>', methods=['DELETE'])
@proxy_request('/docker/registries/{registry}', methods=['DELETE'])
def docker_registry_delete(registry: str) -> None:
    """Delete Docker registry"""
    pass


# Mounts endpoints
@app.route('/api/v1/mounts', methods=['GET', 'POST'])
@proxy_request('/mounts')
def mounts() -> None:
    """Get or create mounts"""
    pass


@app.route('/api/v1/mounts/options', methods=['POST'])
@proxy_request('/mounts/options', methods=['POST'])
def mounts_options() -> None:
    """Set mounts options"""
    pass


@app.route('/api/v1/mounts/<name>', methods=['PUT', 'DELETE'])
@proxy_request('/mounts/{name}')
def mount_item(name: str) -> None:
    """Update or delete mount"""
    pass


@app.route('/api/v1/mounts/<name>/reload', methods=['POST'])
@proxy_request('/mounts/{name}/reload', methods=['POST'])
def mount_reload(name: str) -> None:
    """Reload mount"""
    pass


# Multicast endpoints
@app.route('/api/v1/multicast/info', methods=['GET'])
@proxy_request('/multicast/info')
def multicast_info() -> None:
    """Get multicast information"""
    pass


@app.route('/api/v1/multicast/logs', methods=['GET'])
@proxy_request('/multicast/logs')
def multicast_logs() -> None:
    """Get multicast logs"""
    pass


@app.route('/api/v1/multicast/restart', methods=['POST'])
@proxy_request('/multicast/restart', methods=['POST'])
def multicast_restart() -> None:
    """Restart multicast"""
    pass


@app.route('/api/v1/multicast/stats', methods=['GET'])
@proxy_request('/multicast/stats')
def multicast_stats() -> None:
    """Get multicast statistics"""
    pass


@app.route('/api/v1/multicast/update', methods=['POST'])
@proxy_request('/multicast/update', methods=['POST'])
def multicast_update() -> None:
    """Update multicast"""
    pass


# Observer endpoints
@app.route('/api/v1/observer/info', methods=['GET'])
@proxy_request('/observer/info')
def observer_info() -> None:
    """Get observer information"""
    pass


@app.route('/api/v1/observer/stats', methods=['GET'])
@proxy_request('/observer/stats')
def observer_stats() -> None:
    """Get observer statistics"""
    pass


@app.route('/api/v1/observer/update', methods=['POST'])
@proxy_request('/observer/update', methods=['POST'])
def observer_update() -> None:
    """Update observer"""
    pass


# Error handlers
@app.errorhandler(400)
def bad_request(error: Any) -> Tuple[Response, int]:
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(401)
def unauthorized(error: Any) -> Tuple[Response, int]:
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(404)
def not_found(error: Any) -> Tuple[Response, int]:
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error: Any) -> Tuple[Response, int]:
    return jsonify({"error": "Internal server error"}), 500


# Startup validation
def validate_environment() -> None:
    """Validate required environment variables"""
    if not SUPERVISOR_TOKEN:
        logger.error("SUPERVISOR_TOKEN environment variable is required")
        sys.exit(1)
    
    logger.info(f"Supervisor API Proxy starting on port {PORT}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")
    logger.info(f"Log level: {LOG_LEVEL}")


if __name__ == '__main__':
    validate_environment()
    
    # Check if running under Ingress (environment variable set by Home Assistant)
    ingress_path = os.getenv('HASSIO_INGRESS_PATH', '').rstrip('/')
    
    if ingress_path:
        logger.info(f"Running under Home Assistant Ingress with path: {ingress_path}")
        
        # For Ingress, we need to handle the base path
        from werkzeug.middleware.dispatcher import DispatcherMiddleware
        from werkzeug.wrappers import Response as WerkzeugResponse
        
        def simple_app(environ, start_response):
            response = WerkzeugResponse('API is available at /api/v1/', status=200, mimetype='text/plain')
            return response(environ, start_response)
        
        # Mount the Flask app at the ingress path
        application = DispatcherMiddleware(simple_app, {
            '/api/v1': app
        })
        
        from werkzeug.serving import run_simple
        run_simple(
            hostname='0.0.0.0',
            port=PORT,
            application=application,
            use_reloader=False,
            use_debugger=(LOG_LEVEL == "DEBUG")
        )
    else:
        # Development server (direct access)
        logger.info("Running in development mode (direct access)")
        app.run(
            host='0.0.0.0',
            port=PORT,
            debug=(LOG_LEVEL == "DEBUG")
        )