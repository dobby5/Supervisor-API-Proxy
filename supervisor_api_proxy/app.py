from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
from functools import wraps
from typing import Tuple, Dict, Any, Optional, List, Union, Callable

app = Flask(__name__)
CORS(app)

SUPERVISOR_TOKEN: Optional[str] = os.environ.get('SUPERVISOR_TOKEN')
SUPERVISOR_URL: str = "http://supervisor"
API_PREFIX: str = "/api/v1"

def handle_supervisor_errors(f: Callable[..., Any]) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Supervisor API unavailable", "details": str(e)}), 503
        except Exception as e:
            return jsonify({"error": "Internal error", "details": str(e)}), 500
    return decorated_function

def supervisor_request(endpoint: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None, stream: bool = False, **kwargs: Any) -> Union[Tuple[Dict[str, Any], int], requests.Response, Tuple[Dict[str, str], int]]:
    headers: Dict[str, str] = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url: str = f"{SUPERVISOR_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, stream=stream, **kwargs)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, stream=stream, **kwargs)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, **kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, **kwargs)
        else:
            return {"error": "Unsupported method"}, 400
        
        if stream:
            return response
        
        if response.headers.get('content-type', '').startswith('application/json'):
            return response.json(), response.status_code
        else:
            return {"data": response.text}, response.status_code
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}, 503

@app.route(f'{API_PREFIX}/addons', methods=['GET'])
@handle_supervisor_errors
def get_addons():
    data, status = supervisor_request('/addons')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/addons/reload', methods=['POST'])
@handle_supervisor_errors
def reload_addons():
    data, status = supervisor_request('/addons/reload', 'POST')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/addons/<addon>/info', methods=['GET'])
@handle_supervisor_errors
def get_addon_info(addon: str):
    data, status = supervisor_request(f'/addons/{addon}/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/addons/<addon>/logs', methods=['GET'])
@handle_supervisor_errors
def get_addon_logs(addon: str):
    data, status = supervisor_request(f'/addons/{addon}/logs')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/addons/<addon>/stats', methods=['GET'])
@handle_supervisor_errors
def get_addon_stats(addon: str):
    data, status = supervisor_request(f'/addons/{addon}/stats')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/addons/<addon>/start', methods=['POST'])
@handle_supervisor_errors
def start_addon(addon: str):
    data, status = supervisor_request(f'/addons/{addon}/start', 'POST')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/addons/<addon>/stop', methods=['POST'])
@handle_supervisor_errors
def stop_addon(addon: str):
    data, status = supervisor_request(f'/addons/{addon}/stop', 'POST')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/addons/<addon>/restart', methods=['POST'])
@handle_supervisor_errors
def restart_addon(addon: str):
    data, status = supervisor_request(f'/addons/{addon}/restart', 'POST')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/addons/<addon>/uninstall', methods=['POST'])
@handle_supervisor_errors
def uninstall_addon(addon: str):
    request_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request(f'/addons/{addon}/uninstall', 'POST', request_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/addons/<addon>/options', methods=['POST'])
@handle_supervisor_errors
def configure_addon(addon: str):
    options_data: Optional[Dict[str, Any]] = request.get_json()
    if not options_data:
        return jsonify({"error": "Options data required"}), 400
    
    data, status = supervisor_request(f'/addons/{addon}/options', 'POST', options_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/store', methods=['GET'])
@handle_supervisor_errors
def get_store():
    data, status = supervisor_request('/store')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/store/addons', methods=['GET'])
@handle_supervisor_errors
def get_store_addons():
    data, status = supervisor_request('/store/addons')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/store/addons/<addon>', methods=['GET'])
@handle_supervisor_errors
def get_store_addon_info(addon: str):
    data, status = supervisor_request(f'/store/addons/{addon}')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/store/addons/<addon>/install', methods=['POST'])
@handle_supervisor_errors
def install_addon(addon: str):
    data, status = supervisor_request(f'/store/addons/{addon}/install', 'POST')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/store/addons/<addon>/update', methods=['POST'])
@handle_supervisor_errors
def update_addon(addon: str):
    update_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request(f'/store/addons/{addon}/update', 'POST', update_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/store/repositories', methods=['GET'])
@handle_supervisor_errors
def get_repositories():
    data, status = supervisor_request('/store/repositories')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/store/repositories', methods=['POST'])
@handle_supervisor_errors
def add_repository():
    repo_data: Optional[Dict[str, Any]] = request.get_json()
    if not repo_data or 'repository' not in repo_data:
        return jsonify({"error": "Repository URL required"}), 400
    
    data, status = supervisor_request('/store/repositories', 'POST', repo_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/backups', methods=['GET'])
@handle_supervisor_errors
def get_backups():
    data, status = supervisor_request('/backups')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/backups/info', methods=['GET'])
@handle_supervisor_errors
def get_backup_info():
    data, status = supervisor_request('/backups/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/backups/new/full', methods=['POST'])
@handle_supervisor_errors
def create_full_backup():
    backup_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request('/backups/new/full', 'POST', backup_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/backups/new/partial', methods=['POST'])
@handle_supervisor_errors
def create_partial_backup():
    backup_data: Optional[Dict[str, Any]] = request.get_json()
    if not backup_data:
        return jsonify({"error": "Backup configuration required"}), 400
    
    data, status = supervisor_request('/backups/new/partial', 'POST', backup_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/backups/<backup>/info', methods=['GET'])
@handle_supervisor_errors
def get_backup_details(backup: str):
    data, status = supervisor_request(f'/backups/{backup}/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/backups/<backup>', methods=['DELETE'])
@handle_supervisor_errors
def delete_backup(backup: str):
    data, status = supervisor_request(f'/backups/{backup}', 'DELETE')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/backups/<backup>/restore/full', methods=['POST'])
@handle_supervisor_errors
def restore_full_backup(backup: str):
    restore_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request(f'/backups/{backup}/restore/full', 'POST', restore_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/backups/<backup>/restore/partial', methods=['POST'])
@handle_supervisor_errors
def restore_partial_backup(backup: str):
    restore_data: Optional[Dict[str, Any]] = request.get_json()
    if not restore_data:
        return jsonify({"error": "Restore configuration required"}), 400
    
    data, status = supervisor_request(f'/backups/{backup}/restore/partial', 'POST', restore_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/info', methods=['GET'])
@handle_supervisor_errors
def get_system_info():
    data, status = supervisor_request('/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/supervisor/info', methods=['GET'])
@handle_supervisor_errors
def get_supervisor_info():
    data, status = supervisor_request('/supervisor/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/core/info', methods=['GET'])
@handle_supervisor_errors
def get_core_info():
    data, status = supervisor_request('/core/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/os/info', methods=['GET'])
@handle_supervisor_errors
def get_os_info():
    data, status = supervisor_request('/os/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/host/info', methods=['GET'])
@handle_supervisor_errors
def get_host_info():
    data, status = supervisor_request('/host/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/hardware/info', methods=['GET'])
@handle_supervisor_errors
def get_hardware_info():
    data, status = supervisor_request('/hardware/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/network/info', methods=['GET'])
@handle_supervisor_errors
def get_network_info():
    data, status = supervisor_request('/network/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/supervisor/restart', methods=['POST'])
@handle_supervisor_errors
def restart_supervisor():
    data, status = supervisor_request('/supervisor/restart', 'POST')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/core/restart', methods=['POST'])
@handle_supervisor_errors
def restart_core():
    restart_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request('/core/restart', 'POST', restart_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/host/reboot', methods=['POST'])
@handle_supervisor_errors
def reboot_host():
    reboot_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request('/host/reboot', 'POST', reboot_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/host/shutdown', methods=['POST'])
@handle_supervisor_errors
def shutdown_host():
    shutdown_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request('/host/shutdown', 'POST', shutdown_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/available_updates', methods=['GET'])
@handle_supervisor_errors
def get_available_updates():
    data, status = supervisor_request('/available_updates')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/supervisor/update', methods=['POST'])
@handle_supervisor_errors
def update_supervisor():
    update_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request('/supervisor/update', 'POST', update_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/core/update', methods=['POST'])
@handle_supervisor_errors
def update_core():
    update_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request('/core/update', 'POST', update_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/os/update', methods=['POST'])
@handle_supervisor_errors
def update_os():
    update_data: Dict[str, Any] = request.get_json() or {}
    data, status = supervisor_request('/os/update', 'POST', update_data)
    return jsonify(data), status

@app.route(f'{API_PREFIX}/supervisor/stats', methods=['GET'])
@handle_supervisor_errors
def get_supervisor_stats():
    data, status = supervisor_request('/supervisor/stats')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/core/stats', methods=['GET'])
@handle_supervisor_errors
def get_core_stats():
    data, status = supervisor_request('/core/stats')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/jobs/info', methods=['GET'])
@handle_supervisor_errors
def get_jobs_info():
    data, status = supervisor_request('/jobs/info')
    return jsonify(data), status

@app.route(f'{API_PREFIX}/supervisor/logs', methods=['GET'])
@handle_supervisor_errors
def get_supervisor_logs():
    range_header: Optional[str] = request.headers.get('Range')
    headers: Dict[str, str] = {}
    if range_header:
        headers['Range'] = range_header
    
    response = supervisor_request('/supervisor/logs', stream=False, headers=headers)
    if isinstance(response, tuple):
        data, status = response
        return jsonify(data), status
    else:
        return Response(
            stream_with_context(response.iter_content(chunk_size=1024)),
            content_type=response.headers.get('content-type', 'text/plain')
        )

@app.route(f'{API_PREFIX}/core/logs', methods=['GET'])
@handle_supervisor_errors
def get_core_logs():
    range_header: Optional[str] = request.headers.get('Range')
    headers: Dict[str, str] = {}
    if range_header:
        headers['Range'] = range_header
    
    response = supervisor_request('/core/logs', stream=False, headers=headers)
    if isinstance(response, tuple):
        data, status = response
        return jsonify(data), status
    else:
        return Response(
            stream_with_context(response.iter_content(chunk_size=1024)),
            content_type=response.headers.get('content-type', 'text/plain')
        )

@app.route(f'{API_PREFIX}/health', methods=['GET'])
def health_check():
    try:
        supervisor_request('/supervisor/ping')
        return jsonify({
            "status": "healthy",
            "supervisor_token_available": bool(SUPERVISOR_TOKEN),
            "supervisor_accessible": True
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "supervisor_token_available": bool(SUPERVISOR_TOKEN),
            "supervisor_accessible": False
        }), 503

@app.route(f'{API_PREFIX}/endpoints', methods=['GET'])
def list_endpoints():
    routes: List[Dict[str, Any]] = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.rule,
                'methods': [m for m in (rule.methods or []) if m not in {'OPTIONS', 'HEAD'}]
            })
    return jsonify({"available_endpoints": sorted(routes, key=lambda x: x['endpoint'])})

@app.errorhandler(404)
def not_found(error: Any):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error: Any):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    if not SUPERVISOR_TOKEN:
        print("WARNING: SUPERVISOR_TOKEN not available!")
    
    print("🚀 Starting Supervisor API Proxy on port 8080...")
    print(f"📡 API endpoints available at: {API_PREFIX}/")
    print("🔄 Attempting to bind to 0.0.0.0:8080...")
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        print(f"❌ Failed to start Flask application: {e}")
        raise