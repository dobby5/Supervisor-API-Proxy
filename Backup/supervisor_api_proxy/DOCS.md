# Supervisor API Proxy Add-on Documentation

## Installation

### Add Repository to Home Assistant

1. In Home Assistant, go to **Settings** > **Add-ons** > **Add-on Store**
2. Click the three dots in the top right corner
3. Select **Repositories**
4. Add this URL: `https://github.com/dobby5/Supervisor-API-Proxy`
5. Click **Add**

### Install the Add-on

1. Find "Supervisor API Proxy" in the add-on store
2. Click on it and press **Install**
3. After installation, configure the options if needed
4. Click **Start**

## Configuration

```yaml
log_level: info
cors_origins: []
```

## API Endpoints

The API is available at `http://homeassistant:8080/api/v1/`

### Available Endpoints

- **Add-ons**: `/addons/*` - Manage Home Assistant add-ons
- **Store**: `/store/*` - Browse and install from add-on store
- **Backups**: `/backups/*` - Create and restore backups
- **System Info**: `/info`, `/supervisor/info`, etc. - Get system information
- **System Control**: `/supervisor/restart`, `/host/reboot`, etc. - Control services
- **Updates**: `/available_updates`, `/supervisor/update`, etc. - Manage updates
- **Statistics**: `/supervisor/stats`, `/core/stats` - Monitor resources
- **Logs**: `/supervisor/logs`, `/core/logs` - Access system logs
- **Health**: `/health` - Health check endpoint
- **Endpoints**: `/endpoints` - List all available endpoints

## Usage Examples

### Check Add-on Health
```bash
curl -X GET http://homeassistant:8080/api/v1/health
```

### List All Add-ons
```bash
curl -X GET http://homeassistant:8080/api/v1/addons
```

### Get System Information
```bash
curl -X GET http://homeassistant:8080/api/v1/info
```

## Troubleshooting

### Add-on Won't Start
1. Check the add-on logs for error messages
2. Ensure Home Assistant Supervisor is running properly
3. Verify the add-on configuration is correct

### API Returns Errors
1. Check that the Supervisor API is accessible
2. Verify the add-on has the correct permissions (`hassio_api: true`, `hassio_role: admin`)
3. Check the add-on logs for detailed error information

## Support

For issues and support, please visit: https://github.com/dobby5/Supervisor-API-Proxy/issues