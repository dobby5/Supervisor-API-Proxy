# API Reference

Complete reference documentation for the Home Assistant Supervisor API Proxy endpoints.

## Base URL

```
http://your-ha-ip:8099/api/v1
```

## Authentication

All API endpoints require authentication using a Bearer token in the Authorization header:

```http
Authorization: Bearer YOUR_SUPERVISOR_TOKEN
```

## Response Format

All responses follow a consistent JSON format:

**Success Response:**
```json
{
  "data": { ... },
  "result": "ok"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "details": "Additional error details (optional)"
}
```

## Health & Discovery

### Health Check

Check the proxy and supervisor connection status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy|unhealthy",
  "timestamp": 1640995200.0,
  "supervisor_connection": true,
  "version": "1.0.0"
}
```

**Status Codes:**
- `200` - Healthy
- `503` - Unhealthy

### API Discovery

Get available API endpoints.

**Endpoint:** `GET /discovery`

**Response:**
```json
{
  "message": "Home Assistant Supervisor API Proxy",
  "version": "1.0.0",
  "endpoints": {
    "health": "/api/v1/health",
    "discovery": "/api/v1/discovery",
    "addons": { ... },
    "backups": { ... },
    "system": { ... }
  }
}
```

## Add-on Management

### List Add-ons

Get all available add-ons.

**Endpoint:** `GET /addons`

**Response:**
```json
{
  "data": [
    {
      "slug": "addon-slug",
      "name": "Add-on Name",
      "description": "Add-on description",
      "version": "1.0.0",
      "version_latest": "1.1.0",
      "installed": true,
      "available": true,
      "state": "started|stopped|error",
      "boot": "auto|manual",
      "build": false,
      "options": { ... },
      "schema": { ... },
      "network": { ... },
      "host_network": false,
      "privileged": [],
      "auto_update": false,
      "ingress": false,
      "ingress_url": null
    }
  ]
}
```

### Get Add-on Info

Get detailed information about a specific add-on.

**Endpoint:** `GET /addons/{slug}`

**Parameters:**
- `slug` (path) - Add-on slug identifier

**Response:**
```json
{
  "data": {
    "slug": "addon-slug",
    "name": "Add-on Name",
    "state": "started",
    "version": "1.0.0",
    "options": { ... },
    "schema": { ... }
  }
}
```

### Install Add-on

Install an add-on from the store.

**Endpoint:** `POST /addons/{slug}/install`

**Parameters:**
- `slug` (path) - Add-on slug identifier

**Response:**
```json
{
  "result": "ok"
}
```

### Uninstall Add-on

Remove an installed add-on.

**Endpoint:** `POST /addons/{slug}/uninstall`

**Parameters:**
- `slug` (path) - Add-on slug identifier

**Response:**
```json
{
  "result": "ok"
}
```

### Start Add-on

Start a stopped add-on.

**Endpoint:** `POST /addons/{slug}/start`

**Parameters:**
- `slug` (path) - Add-on slug identifier

**Response:**
```json
{
  "result": "ok"
}
```

### Stop Add-on

Stop a running add-on.

**Endpoint:** `POST /addons/{slug}/stop`

**Parameters:**
- `slug` (path) - Add-on slug identifier

**Response:**
```json
{
  "result": "ok"
}
```

### Restart Add-on

Restart an add-on.

**Endpoint:** `POST /addons/{slug}/restart`

**Parameters:**
- `slug` (path) - Add-on slug identifier

**Response:**
```json
{
  "result": "ok"
}
```

### Update Add-on

Update an add-on to the latest version.

**Endpoint:** `POST /addons/{slug}/update`

**Parameters:**
- `slug` (path) - Add-on slug identifier

**Response:**
```json
{
  "result": "ok"
}
```

### Get Add-on Logs

Retrieve add-on logs with optional streaming.

**Endpoint:** `GET /addons/{slug}/logs`

**Parameters:**
- `slug` (path) - Add-on slug identifier
- `follow` (query, optional) - Stream logs in real-time (`true`/`false`)

**Response:**
- Content-Type: `text/plain`
- Body: Raw log text

**Example:**
```bash
curl "http://your-ha-ip:8099/api/v1/addons/my-addon/logs?follow=true"
```

### Get Add-on Statistics

Get resource usage statistics for an add-on.

**Endpoint:** `GET /addons/{slug}/stats`

**Parameters:**
- `slug` (path) - Add-on slug identifier

**Response:**
```json
{
  "data": {
    "cpu_percent": 2.5,
    "memory_usage": 134217728,
    "memory_limit": 1073741824,
    "memory_percent": 12.5,
    "network_rx": 1048576,
    "network_tx": 524288,
    "blk_read": 2097152,
    "blk_write": 1048576
  }
}
```

## Backup Management

### List Backups

Get all available backups.

**Endpoint:** `GET /backups`

**Response:**
```json
{
  "data": [
    {
      "slug": "backup-slug",
      "name": "My Backup",
      "date": "2023-01-01T10:00:00Z",
      "type": "full|partial",
      "protected": false,
      "compressed": true,
      "location": null,
      "addons": [
        {
          "slug": "addon-slug",
          "name": "Add-on Name", 
          "version": "1.0.0"
        }
      ],
      "folders": ["config", "ssl"],
      "homeassistant": "2023.1.1",
      "size": 1048576000
    }
  ]
}
```

### Get Backup Info

Get detailed information about a specific backup.

**Endpoint:** `GET /backups/{slug}`

**Parameters:**
- `slug` (path) - Backup slug identifier

**Response:**
```json
{
  "data": {
    "slug": "backup-slug",
    "name": "My Backup",
    "date": "2023-01-01T10:00:00Z",
    "type": "full",
    "size": 1048576000,
    "addons": [...],
    "folders": [...]
  }
}
```

### Create Backup

Create a new backup.

**Endpoint:** `POST /backups`

**Request Body:**
```json
{
  "name": "My Backup",
  "addons": ["addon1", "addon2"],
  "folders": ["config", "ssl"],
  "password": "optional-password"
}
```

**Parameters:**
- `name` (optional) - Backup name
- `addons` (optional) - List of add-on slugs to include (null for all)
- `folders` (optional) - List of folders to include (null for all)
- `password` (optional) - Password protection

**Response:**
```json
{
  "result": "ok"
}
```

### Delete Backup

Remove a backup.

**Endpoint:** `DELETE /backups/{slug}`

**Parameters:**
- `slug` (path) - Backup slug identifier

**Response:**
```json
{
  "result": "ok"
}
```

### Restore Full Backup

Restore a complete backup.

**Endpoint:** `POST /backups/{slug}/restore/full`

**Parameters:**
- `slug` (path) - Backup slug identifier

**Request Body:**
```json
{
  "password": "backup-password"
}
```

**Response:**
```json
{
  "result": "ok"
}
```

### Restore Partial Backup

Restore selected components from a backup.

**Endpoint:** `POST /backups/{slug}/restore/partial`

**Parameters:**
- `slug` (path) - Backup slug identifier

**Request Body:**
```json
{
  "addons": ["addon1", "addon2"],
  "folders": ["config"],
  "homeassistant": true,
  "password": "backup-password"
}
```

**Response:**
```json
{
  "result": "ok"
}
```

## System Information

### Supervisor Information

Get Home Assistant Supervisor details.

**Endpoint:** `GET /supervisor/info`

**Response:**
```json
{
  "data": {
    "version": "2023.01.1",
    "version_latest": "2023.01.1",
    "update_available": false,
    "channel": "stable",
    "arch": "amd64",
    "supported": true,
    "healthy": true,
    "timezone": "UTC",
    "logging": "info",
    "ip_address": "192.168.1.100",
    "wait_boot": 600,
    "debug": false,
    "addons": [...],
    "addons_repositories": [...]
  }
}
```

### Update Supervisor

Update Home Assistant Supervisor.

**Endpoint:** `POST /supervisor/update`

**Response:**
```json
{
  "result": "ok"
}
```

### Core Information

Get Home Assistant Core details.

**Endpoint:** `GET /core/info`

**Response:**
```json
{
  "data": {
    "version": "2023.1.1",
    "version_latest": "2023.1.1", 
    "update_available": false,
    "machine": "generic-x86-64",
    "ip_address": "192.168.1.100",
    "port": 8123,
    "ssl": false,
    "watchdog": true,
    "boot_time": 60.5,
    "state": "RUNNING"
  }
}
```

### Update Core

Update Home Assistant Core.

**Endpoint:** `POST /core/update`

**Response:**
```json
{
  "result": "ok"
}
```

### Restart Core

Restart Home Assistant Core.

**Endpoint:** `POST /core/restart`

**Response:**
```json
{
  "result": "ok"
}
```

### Host Information

Get host system information.

**Endpoint:** `GET /host/info`

**Response:**
```json
{
  "data": {
    "hostname": "homeassistant",
    "operating_system": "Home Assistant OS",
    "kernel": "5.15.0",
    "disk_total": 32212254720,
    "disk_used": 4294967296,
    "disk_free": 27917287424
  }
}
```

### OS Information

Get operating system details.

**Endpoint:** `GET /os/info`

**Response:**
```json
{
  "data": {
    "version": "9.5",
    "version_latest": "9.5",
    "update_available": false,
    "board": "generic-x86-64",
    "boot": "A"
  }
}
```

### Network Information

Get network configuration.

**Endpoint:** `GET /network/info`

**Response:**
```json
{
  "data": {
    "hostname": "homeassistant",
    "interfaces": [...]
  }
}
```

## Store Management

### List Repositories

Get configured add-on repositories.

**Endpoint:** `GET /store/repositories`

**Response:**
```json
{
  "data": [
    {
      "slug": "repository-slug",
      "name": "Repository Name",
      "url": "https://github.com/user/repo",
      "maintainer": "Maintainer Name"
    }
  ]
}
```

### Add Repository

Add a new add-on repository.

**Endpoint:** `POST /store/repositories`

**Request Body:**
```json
{
  "repository": "https://github.com/user/addon-repository"
}
```

**Response:**
```json
{
  "result": "ok"
}
```

### Remove Repository

Remove an add-on repository.

**Endpoint:** `DELETE /store/repositories/{slug}`

**Parameters:**
- `slug` (path) - Repository slug

**Response:**
```json
{
  "result": "ok"
}
```

### List Store Add-ons

Get all add-ons available in the store.

**Endpoint:** `GET /store/addons`

**Response:**
```json
{
  "data": [
    {
      "slug": "addon-slug",
      "name": "Add-on Name",
      "description": "Description",
      "repository": "repository-slug",
      "version": "1.0.0",
      "installed": false
    }
  ]
}
```

### Get Store Add-on Info

Get information about a store add-on.

**Endpoint:** `GET /store/addons/{slug}`

**Parameters:**
- `slug` (path) - Add-on slug

**Response:**
```json
{
  "data": {
    "slug": "addon-slug",
    "name": "Add-on Name", 
    "description": "Description",
    "long_description": "Detailed description...",
    "version": "1.0.0",
    "repository": "repository-slug",
    "arch": ["amd64", "aarch64"],
    "image": "addon-image"
  }
}
```

## Job Management

### List Jobs

Get all running and completed jobs.

**Endpoint:** `GET /jobs`

**Response:**
```json
{
  "data": [
    {
      "uuid": "job-uuid",
      "name": "Install addon",
      "reference": "addon-slug",
      "done": false,
      "child_jobs": [],
      "progress": 50,
      "stage": "downloading",
      "errors": []
    }
  ]
}
```

### Get Job Info

Get information about a specific job.

**Endpoint:** `GET /jobs/{uuid}`

**Parameters:**
- `uuid` (path) - Job UUID

**Response:**
```json
{
  "data": {
    "uuid": "job-uuid",
    "name": "Install addon",
    "done": true,
    "progress": 100,
    "errors": []
  }
}
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 500 | Internal Server Error |
| 502 | Bad Gateway (Supervisor unavailable) |
| 503 | Service Unavailable |
| 504 | Gateway Timeout |

### Common Error Responses

**Authentication Error:**
```json
{
  "error": "Unauthorized",
  "details": "Invalid or missing authorization token"
}
```

**Validation Error:**
```json
{
  "error": "Bad request",
  "details": "Invalid request data"
}
```

**Supervisor Connection Error:**
```json
{
  "error": "Unable to connect to Supervisor",
  "details": "Supervisor service is not available"
}
```

**Resource Not Found:**
```json
{
  "error": "Not found",
  "details": "The requested resource does not exist"
}
```

## Rate Limiting

The API includes basic rate limiting to prevent abuse:

- **Default limit:** 100 requests per minute per IP
- **Headers:** Rate limit information is included in response headers:
  - `X-RateLimit-Limit` - Request limit
  - `X-RateLimit-Remaining` - Remaining requests
  - `X-RateLimit-Reset` - Reset timestamp

**Rate Limit Exceeded:**
```json
{
  "error": "Rate limit exceeded",
  "details": "Too many requests. Please try again later."
}
```

## CORS Support

The API includes CORS headers to support web applications:

- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Methods`
- `Access-Control-Allow-Headers`

Configure allowed origins in the add-on configuration:

```yaml
cors_origins:
  - "https://my-app.example.com"
  - "http://localhost:3000"
```

## Streaming Endpoints

Some endpoints support streaming responses:

### Log Streaming

```bash
curl -N "http://your-ha-ip:8099/api/v1/addons/my-addon/logs?follow=true"
```

### Server-Sent Events

For real-time updates, use the `Accept: text/event-stream` header:

```bash
curl -H "Accept: text/event-stream" \
     "http://your-ha-ip:8099/api/v1/addons/my-addon/logs?follow=true"
```

## OpenAPI/Swagger

An OpenAPI specification is available for integration with API tools:

**Endpoint:** `GET /api/v1/openapi.json`

You can use tools like Swagger UI or Postman to explore the API interactively.

## SDK Examples

### Python

```python
import requests

class SupervisorAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
    
    def get_addons(self):
        response = self.session.get(f'{self.base_url}/addons')
        return response.json()
    
    def start_addon(self, slug):
        response = self.session.post(f'{self.base_url}/addons/{slug}/start')
        return response.json()

# Usage
api = SupervisorAPI('http://192.168.1.100:8099/api/v1', 'your-token')
addons = api.get_addons()
```

### JavaScript/Node.js

```javascript
class SupervisorAPI {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async request(method, endpoint, data = null) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method,
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: data ? JSON.stringify(data) : null
        });
        return response.json();
    }
    
    getAddons() {
        return this.request('GET', '/addons');
    }
    
    startAddon(slug) {
        return this.request('POST', `/addons/${slug}/start`);
    }
}

// Usage
const api = new SupervisorAPI('http://192.168.1.100:8099/api/v1', 'your-token');
const addons = await api.getAddons();
```

### cURL Examples

```bash
# Get health status
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://your-ha-ip:8099/api/v1/health

# List add-ons
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://your-ha-ip:8099/api/v1/addons

# Start an add-on
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://your-ha-ip:8099/api/v1/addons/my-addon/start

# Create backup
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Backup"}' \
     http://your-ha-ip:8099/api/v1/backups

# Stream logs
curl -N \
     -H "Authorization: Bearer YOUR_TOKEN" \
     "http://your-ha-ip:8099/api/v1/addons/my-addon/logs?follow=true"
```