#!/usr/bin/env python3
"""
Unit tests for the Home Assistant Supervisor API Proxy
"""

import os
import json
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Import the app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, make_supervisor_request, validate_token, get_auth_headers, ProxyError


class TestApp:
    """Test cases for the main Flask application"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def mock_supervisor_token(self):
        """Mock the supervisor token"""
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            yield
    
    def test_health_endpoint_success(self, client, mock_supervisor_token):
        """Test health endpoint with successful supervisor response"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "ok"}
            mock_request.return_value = (mock_response, 200)
            
            response = client.get('/api/v1/health')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert data['supervisor_connection'] is True
            assert 'timestamp' in data
            assert 'version' in data
    
    def test_health_endpoint_supervisor_failure(self, client, mock_supervisor_token):
        """Test health endpoint when supervisor is not accessible"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_request.side_effect = Exception("Connection failed")
            
            response = client.get('/api/v1/health')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['status'] == 'unhealthy'
            assert data['supervisor_connection'] is False
    
    def test_discovery_endpoint(self, client, mock_supervisor_token):
        """Test API discovery endpoint"""
        response = client.get('/api/v1/discovery')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'version' in data
        assert 'endpoints' in data
        assert 'addons' in data['endpoints']
        assert 'backups' in data['endpoints']
        assert 'system' in data['endpoints']
    
    def test_addons_list_endpoint(self, client, mock_supervisor_token):
        """Test add-ons list endpoint"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"slug": "addon1", "name": "Test Addon 1"},
                    {"slug": "addon2", "name": "Test Addon 2"}
                ]
            }
            mock_request.return_value = (mock_response, 200)
            
            response = client.get('/api/v1/addons')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['data']) == 2
            assert data['data'][0]['slug'] == 'addon1'
    
    def test_addon_info_endpoint(self, client, mock_supervisor_token):
        """Test specific add-on info endpoint"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {"slug": "test-addon", "name": "Test Addon", "state": "started"}
            }
            mock_request.return_value = (mock_response, 200)
            
            response = client.get('/api/v1/addons/test-addon')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['data']['slug'] == 'test-addon'
            assert data['data']['state'] == 'started'
    
    def test_addon_start_endpoint(self, client, mock_supervisor_token):
        """Test add-on start endpoint"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "ok"}
            mock_request.return_value = (mock_response, 200)
            
            response = client.post('/api/v1/addons/test-addon/start')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['result'] == 'ok'
            mock_request.assert_called_once()
    
    def test_backups_list_endpoint(self, client, mock_supervisor_token):
        """Test backups list endpoint"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"slug": "backup1", "name": "Test Backup 1", "date": "2023-01-01"},
                    {"slug": "backup2", "name": "Test Backup 2", "date": "2023-01-02"}
                ]
            }
            mock_request.return_value = (mock_response, 200)
            
            response = client.get('/api/v1/backups')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['data']) == 2
            assert data['data'][0]['slug'] == 'backup1'
    
    def test_create_backup_endpoint(self, client, mock_supervisor_token):
        """Test backup creation endpoint"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "ok"}
            mock_request.return_value = (mock_response, 200)
            
            backup_data = {"name": "Test Backup"}
            response = client.post('/api/v1/backups', 
                                 json=backup_data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['result'] == 'ok'
    
    def test_supervisor_info_endpoint(self, client, mock_supervisor_token):
        """Test supervisor info endpoint"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "version": "2023.01.1",
                    "healthy": True,
                    "supported": True
                }
            }
            mock_request.return_value = (mock_response, 200)
            
            response = client.get('/api/v1/supervisor/info')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['data']['version'] == '2023.01.1'
            assert data['data']['healthy'] is True
    
    def test_core_info_endpoint(self, client, mock_supervisor_token):
        """Test core info endpoint"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "version": "2023.1.1",
                    "state": "RUNNING",
                    "port": 8123
                }
            }
            mock_request.return_value = (mock_response, 200)
            
            response = client.get('/api/v1/core/info')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['data']['version'] == '2023.1.1'
            assert data['data']['state'] == 'RUNNING'
    
    def test_jobs_list_endpoint(self, client, mock_supervisor_token):
        """Test jobs list endpoint"""
        with patch('app.make_supervisor_request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"uuid": "job-1", "name": "Install addon", "done": False},
                    {"uuid": "job-2", "name": "Update core", "done": True}
                ]
            }
            mock_request.return_value = (mock_response, 200)
            
            response = client.get('/api/v1/jobs')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['data']) == 2
            assert data['data'][0]['uuid'] == 'job-1'
    
    def test_cors_headers(self, client, mock_supervisor_token):
        """Test CORS headers are present"""
        response = client.get('/api/v1/discovery')
        
        # Check CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_method_not_allowed(self, client, mock_supervisor_token):
        """Test method not allowed responses"""
        response = client.put('/api/v1/health')
        assert response.status_code == 405
    
    def test_not_found_endpoint(self, client, mock_supervisor_token):
        """Test non-existent endpoint returns 404"""
        response = client.get('/api/v1/nonexistent')
        assert response.status_code == 404


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_validate_token_success(self):
        """Test token validation with valid token"""
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            # Should not raise an exception
            validate_token()
    
    def test_validate_token_failure(self):
        """Test token validation without token"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ProxyError) as excinfo:
                validate_token()
            assert "token not configured" in str(excinfo.value.message)
    
    def test_get_auth_headers(self):
        """Test auth headers generation"""
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            headers = get_auth_headers()
            assert headers['Authorization'] == 'Bearer test-token'
            assert headers['Content-Type'] == 'application/json'
    
    @patch('app.requests.request')
    def test_make_supervisor_request_success(self, mock_request):
        """Test successful supervisor request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "ok"}
        mock_request.return_value = mock_response
        
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            response, status = make_supervisor_request('GET', '/test')
            
            assert status == 200
            assert response.status_code == 200
            mock_request.assert_called_once()
    
    @patch('app.requests.request')
    def test_make_supervisor_request_timeout(self, mock_request):
        """Test supervisor request timeout"""
        mock_request.side_effect = requests.exceptions.Timeout()
        
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            with pytest.raises(ProxyError) as excinfo:
                make_supervisor_request('GET', '/test')
            assert "Request failed" in str(excinfo.value.message)
    
    @patch('app.requests.request')
    def test_make_supervisor_request_connection_error(self, mock_request):
        """Test supervisor request connection error"""
        mock_request.side_effect = requests.exceptions.ConnectionError()
        
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            with pytest.raises(ProxyError) as excinfo:
                make_supervisor_request('GET', '/test')
            assert "Request failed" in str(excinfo.value.message)
    
    @patch('app.requests.request')
    def test_make_supervisor_request_with_data(self, mock_request):
        """Test supervisor request with JSON data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        test_data = {"key": "value"}
        
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            response, status = make_supervisor_request('POST', '/test', data=test_data)
            
            assert status == 200
            mock_request.assert_called_once()
            # Check that JSON data was passed
            call_args = mock_request.call_args
            assert call_args[1]['json'] == test_data
    
    @patch('app.requests.request')
    def test_make_supervisor_request_with_params(self, mock_request):
        """Test supervisor request with query parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        test_params = {"follow": "true"}
        
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            response, status = make_supervisor_request('GET', '/test', params=test_params)
            
            assert status == 200
            mock_request.assert_called_once()
            # Check that params were passed
            call_args = mock_request.call_args
            assert call_args[1]['params'] == test_params


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_missing_supervisor_token(self, client):
        """Test endpoints without supervisor token"""
        with patch.dict(os.environ, {}, clear=True):
            response = client.get('/api/v1/addons')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "token not configured" in data['error']
    
    def test_supervisor_api_error(self, client):
        """Test handling of supervisor API errors"""
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            with patch('app.make_supervisor_request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 404
                mock_response.json.return_value = {"error": "Not found"}
                mock_request.return_value = (mock_response, 404)
                
                response = client.get('/api/v1/addons/nonexistent')
                
                assert response.status_code == 404
                data = json.loads(response.data)
                assert data['error'] == 'Not found'
    
    def test_json_decode_error(self, client):
        """Test handling of invalid JSON responses"""
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            with patch('app.make_supervisor_request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.side_effect = ValueError("Invalid JSON")
                mock_response.text = "Invalid response"
                mock_request.return_value = (mock_response, 200)
                
                response = client.get('/api/v1/addons')
                
                assert response.status_code == 200
                assert response.data == b"Invalid response"
    
    def test_unexpected_exception(self, client):
        """Test handling of unexpected exceptions"""
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            with patch('app.make_supervisor_request') as mock_request:
                mock_request.side_effect = Exception("Unexpected error")
                
                response = client.get('/api/v1/addons')
                
                assert response.status_code == 500
                data = json.loads(response.data)
                assert "Internal server error" in data['error']


class TestStreamingEndpoints:
    """Test streaming endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_addon_logs_streaming(self, client):
        """Test add-on logs streaming endpoint"""
        with patch.dict(os.environ, {'SUPERVISOR_TOKEN': 'test-token'}):
            with patch('app.make_supervisor_request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.iter_content.return_value = [b'log line 1\n', b'log line 2\n']
                mock_response.headers = {'content-type': 'text/plain'}
                mock_request.return_value = (mock_response, 200)
                
                response = client.get('/api/v1/addons/test-addon/logs?follow=true')
                
                assert response.status_code == 200
                # Check that streaming was requested
                call_args = mock_request.call_args
                assert call_args[1]['stream'] is True


if __name__ == '__main__':
    pytest.main([__file__])