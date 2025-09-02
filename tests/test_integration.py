#!/usr/bin/env python3
"""
Integration tests for the Home Assistant Supervisor API Proxy
"""

import os
import json
import time
import pytest
import requests
import subprocess
from unittest.mock import Mock, patch
from threading import Thread


class MockSupervisorServer:
    """Mock Home Assistant Supervisor server for testing"""
    
    def __init__(self, port=8080):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.server = None
        self.thread = None
        
    def start(self):
        """Start the mock supervisor server"""
        from flask import Flask, request, jsonify
        
        mock_app = Flask(__name__)
        
        # Mock endpoints
        @mock_app.route('/supervisor/ping', methods=['GET'])
        def supervisor_ping():
            return jsonify({"result": "ok"})
        
        @mock_app.route('/addons', methods=['GET'])
        def addons_list():
            return jsonify({
                "data": [
                    {
                        "slug": "test-addon",
                        "name": "Test Addon",
                        "description": "A test add-on",
                        "version": "1.0.0",
                        "version_latest": "1.0.0",
                        "installed": True,
                        "available": True,
                        "state": "stopped",
                        "boot": "manual",
                        "build": False,
                        "options": {},
                        "schema": {},
                        "network": None,
                        "host_network": False,
                        "host_pid": False,
                        "host_ipc": False,
                        "host_dbus": False,
                        "privileged": [],
                        "apparmor": "default",
                        "devices": [],
                        "auto_update": False,
                        "ingress": False,
                        "ingress_url": None,
                        "ingress_panel": False,
                        "url": None,
                        "detached": False,
                        "repository": "local"
                    }
                ]
            })
        
        @mock_app.route('/addons/<slug>', methods=['GET'])
        def addon_info(slug):
            if slug == "test-addon":
                return jsonify({
                    "data": {
                        "slug": slug,
                        "name": "Test Addon",
                        "state": "stopped",
                        "version": "1.0.0"
                    }
                })
            return jsonify({"error": "Add-on not found"}), 404
        
        @mock_app.route('/addons/<slug>/start', methods=['POST'])
        def addon_start(slug):
            if slug == "test-addon":
                return jsonify({"result": "ok"})
            return jsonify({"error": "Add-on not found"}), 404
        
        @mock_app.route('/addons/<slug>/stop', methods=['POST'])  
        def addon_stop(slug):
            if slug == "test-addon":
                return jsonify({"result": "ok"})
            return jsonify({"error": "Add-on not found"}), 404
        
        @mock_app.route('/addons/<slug>/logs', methods=['GET'])
        def addon_logs(slug):
            if slug == "test-addon":
                logs = "2023-01-01 10:00:00 INFO Starting addon\n2023-01-01 10:00:01 INFO Addon started\n"
                return logs, 200, {'Content-Type': 'text/plain'}
            return jsonify({"error": "Add-on not found"}), 404
        
        @mock_app.route('/backups', methods=['GET'])
        def backups_list():
            return jsonify({
                "data": [
                    {
                        "slug": "test-backup",
                        "name": "Test Backup",
                        "date": "2023-01-01T10:00:00Z",
                        "type": "full",
                        "protected": False,
                        "compressed": True,
                        "location": None,
                        "addons": [],
                        "folders": ["config"],
                        "homeassistant": "2023.1.1",
                        "size": 1024000
                    }
                ]
            })
        
        @mock_app.route('/backups', methods=['POST'])
        def create_backup():
            return jsonify({"result": "ok"})
        
        @mock_app.route('/supervisor/info', methods=['GET'])
        def supervisor_info():
            return jsonify({
                "data": {
                    "version": "2023.01.1",
                    "version_latest": "2023.01.1", 
                    "update_available": False,
                    "channel": "stable",
                    "arch": "amd64",
                    "supported": True,
                    "healthy": True,
                    "timezone": "UTC",
                    "logging": "info",
                    "ip_address": "192.168.1.100",
                    "wait_boot": 600,
                    "debug": False,
                    "debug_block": False,
                    "addons": [],
                    "addons_repositories": []
                }
            })
        
        @mock_app.route('/core/info', methods=['GET'])
        def core_info():
            return jsonify({
                "data": {
                    "version": "2023.1.1",
                    "version_latest": "2023.1.1",
                    "update_available": False,
                    "machine": "generic-x86-64",
                    "ip_address": "192.168.1.100",
                    "port": 8123,
                    "ssl": False,
                    "watchdog": True,
                    "boot_time": 60.5,
                    "state": "RUNNING"
                }
            })
        
        @mock_app.route('/jobs', methods=['GET'])
        def jobs_list():
            return jsonify({
                "data": [
                    {
                        "uuid": "test-job-uuid",
                        "name": "Install test addon",
                        "reference": "test-addon",
                        "done": False,
                        "child_jobs": [],
                        "progress": 50,
                        "stage": "Installing",
                        "errors": []
                    }
                ]
            })
        
        # Authentication check
        @mock_app.before_request
        def check_auth():
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"error": "Unauthorized"}), 401
            
            token = auth_header.split(' ', 1)[1]
            if token != 'test-token':
                return jsonify({"error": "Invalid token"}), 401
        
        # Start server in thread
        def run_server():
            mock_app.run(host='localhost', port=self.port, debug=False, use_reloader=False)
        
        self.thread = Thread(target=run_server, daemon=True)
        self.thread.start()
        
        # Wait for server to start
        time.sleep(1)
    
    def stop(self):
        """Stop the mock supervisor server"""
        if self.thread and self.thread.is_alive():
            # In a real scenario, you'd properly shut down the Flask server
            pass


@pytest.fixture(scope="session")
def mock_supervisor():
    """Start and stop mock supervisor server for the test session"""
    server = MockSupervisorServer(port=18080)
    server.start()
    yield server
    server.stop()


@pytest.fixture(scope="session") 
def proxy_server():
    """Start the proxy server for integration tests"""
    # Set environment variables for testing
    env = os.environ.copy()
    env.update({
        'SUPERVISOR_TOKEN': 'test-token',
        'SUPERVISOR_URL': 'http://localhost:18080',
        'PORT': '18099',
        'LOG_LEVEL': 'ERROR',  # Minimize log output during tests
        'CORS_ORIGINS': '*'
    })
    
    # Start the proxy server
    process = subprocess.Popen(
        ['python3', 'app.py'],
        env=env,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield process
    
    # Clean up
    process.terminate()
    process.wait()


class TestProxyIntegration:
    """Integration tests for the complete proxy setup"""
    
    @pytest.fixture
    def proxy_url(self):
        return "http://localhost:18099"
    
    def test_health_endpoint_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test health endpoint with real HTTP requests"""
        response = requests.get(f"{proxy_url}/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['supervisor_connection'] is True
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_discovery_endpoint_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test API discovery endpoint"""
        response = requests.get(f"{proxy_url}/api/v1/discovery")
        
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'endpoints' in data
        assert 'addons' in data['endpoints']
    
    def test_addons_list_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test add-ons list endpoint integration"""
        response = requests.get(f"{proxy_url}/api/v1/addons")
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert len(data['data']) == 1
        assert data['data'][0]['slug'] == 'test-addon'
        assert data['data'][0]['name'] == 'Test Addon'
    
    def test_addon_info_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test specific add-on info endpoint"""
        response = requests.get(f"{proxy_url}/api/v1/addons/test-addon")
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['slug'] == 'test-addon'
        assert data['data']['name'] == 'Test Addon'
        assert data['data']['state'] == 'stopped'
    
    def test_addon_not_found_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test non-existent add-on returns 404"""
        response = requests.get(f"{proxy_url}/api/v1/addons/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert 'error' in data
    
    def test_addon_start_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test add-on start endpoint"""
        response = requests.post(f"{proxy_url}/api/v1/addons/test-addon/start")
        
        assert response.status_code == 200
        data = response.json()
        assert data['result'] == 'ok'
    
    def test_addon_stop_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test add-on stop endpoint"""
        response = requests.post(f"{proxy_url}/api/v1/addons/test-addon/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data['result'] == 'ok'
    
    def test_addon_logs_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test add-on logs endpoint"""
        response = requests.get(f"{proxy_url}/api/v1/addons/test-addon/logs")
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'text/plain; charset=utf-8'
        assert 'Starting addon' in response.text
        assert 'Addon started' in response.text
    
    def test_backups_list_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test backups list endpoint"""
        response = requests.get(f"{proxy_url}/api/v1/backups")
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert len(data['data']) == 1
        assert data['data'][0]['slug'] == 'test-backup'
        assert data['data'][0]['name'] == 'Test Backup'
    
    def test_create_backup_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test backup creation endpoint"""
        backup_data = {
            "name": "Integration Test Backup",
            "addons": None,
            "folders": None,
            "password": None
        }
        
        response = requests.post(
            f"{proxy_url}/api/v1/backups",
            json=backup_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['result'] == 'ok'
    
    def test_supervisor_info_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test supervisor info endpoint"""
        response = requests.get(f"{proxy_url}/api/v1/supervisor/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['version'] == '2023.01.1'
        assert data['data']['healthy'] is True
        assert data['data']['supported'] is True
    
    def test_core_info_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test core info endpoint"""
        response = requests.get(f"{proxy_url}/api/v1/core/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['version'] == '2023.1.1'
        assert data['data']['state'] == 'RUNNING'
        assert data['data']['port'] == 8123
    
    def test_jobs_list_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test jobs list endpoint"""
        response = requests.get(f"{proxy_url}/api/v1/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert len(data['data']) == 1
        assert data['data'][0]['uuid'] == 'test-job-uuid'
        assert data['data'][0]['name'] == 'Install test addon'
    
    def test_cors_headers_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test CORS headers are present"""
        response = requests.get(f"{proxy_url}/api/v1/discovery")
        
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*'
    
    def test_method_not_allowed_integration(self, mock_supervisor, proxy_server, proxy_url):
        """Test method not allowed"""
        response = requests.put(f"{proxy_url}/api/v1/health")
        assert response.status_code == 405


class TestErrorScenarios:
    """Test error scenarios in integration"""
    
    @pytest.fixture
    def proxy_url(self):
        return "http://localhost:18099"
    
    def test_supervisor_unavailable(self, proxy_server, proxy_url):
        """Test when supervisor is not available"""
        # Health check should still work but report unhealthy
        response = requests.get(f"{proxy_url}/api/v1/health")
        
        assert response.status_code == 503  # Service unavailable
        data = response.json()
        assert data['status'] == 'unhealthy'
        assert data['supervisor_connection'] is False
    
    def test_invalid_endpoint(self, mock_supervisor, proxy_server, proxy_url):
        """Test invalid endpoint returns 404"""
        response = requests.get(f"{proxy_url}/api/v1/invalid-endpoint")
        assert response.status_code == 404


class TestAuthenticationIntegration:
    """Test authentication scenarios"""
    
    def test_auth_via_supervisor(self, mock_supervisor):
        """Test that authentication is properly forwarded to supervisor"""
        # This would be tested with a real supervisor that checks tokens
        # For now, we verify the mock server receives the correct headers
        
        # Direct call to mock supervisor without token should fail
        response = requests.get("http://localhost:18080/addons")
        assert response.status_code == 401
        
        # Direct call with correct token should succeed  
        headers = {'Authorization': 'Bearer test-token'}
        response = requests.get("http://localhost:18080/addons", headers=headers)
        assert response.status_code == 200
        
        # Direct call with wrong token should fail
        headers = {'Authorization': 'Bearer wrong-token'}
        response = requests.get("http://localhost:18080/addons", headers=headers)
        assert response.status_code == 401


class TestPerformance:
    """Basic performance tests"""
    
    @pytest.fixture
    def proxy_url(self):
        return "http://localhost:18099"
    
    def test_response_times(self, mock_supervisor, proxy_server, proxy_url):
        """Test that response times are reasonable"""
        import time
        
        # Test multiple endpoints
        endpoints = [
            "/api/v1/health",
            "/api/v1/discovery", 
            "/api/v1/addons",
            "/api/v1/supervisor/info"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{proxy_url}{endpoint}")
            end_time = time.time()
            
            assert response.status_code == 200
            assert end_time - start_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, mock_supervisor, proxy_server, proxy_url):
        """Test handling concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request():
            response = requests.get(f"{proxy_url}/api/v1/discovery")
            return response.status_code
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10


if __name__ == '__main__':
    pytest.main([__file__, "-v"])