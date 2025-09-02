# Home Assistant Supervisor API Proxy

A lightweight RESTful API proxy for Home Assistant Supervisor functions, providing easy access to add-ons, backups, system information, and more.

## Features

- **Add-on Management**: Install, start, stop, restart, and configure add-ons
- **Store Access**: Browse and install add-ons from the Home Assistant Add-on Store
- **Backup Operations**: Create, restore, and manage full and partial backups
- **System Information**: Get detailed info about supervisor, core, OS, and hardware
- **System Control**: Restart services, reboot, and shutdown the host
- **Update Management**: Check for and apply updates to supervisor, core, and OS
- **Statistics**: Monitor resource usage and performance metrics
- **Logging**: Access supervisor and core logs with streaming support
- **Health Monitoring**: Built-in health checks and endpoint discovery

## API Endpoints

All endpoints are prefixed with `/api/v1`:

### Add-ons
- `GET /addons` - List all installed add-ons
- `POST /addons/reload` - Reload add-on information
- `GET /addons/{addon}/info` - Get add-on details
- `GET /addons/{addon}/logs` - Get add-on logs
- `GET /addons/{addon}/stats` - Get add-on statistics
- `POST /addons/{addon}/start` - Start an add-on
- `POST /addons/{addon}/stop` - Stop an add-on
- `POST /addons/{addon}/restart` - Restart an add-on
- `POST /addons/{addon}/uninstall` - Uninstall an add-on
- `POST /addons/{addon}/options` - Configure add-on options

### Store
- `GET /store` - Get store information
- `GET /store/addons` - List all store add-ons
- `GET /store/addons/{addon}` - Get store add-on details
- `POST /store/addons/{addon}/install` - Install add-on from store
- `POST /store/addons/{addon}/update` - Update an add-on
- `GET /store/repositories` - List repositories
- `POST /store/repositories` - Add repository

### Backups
- `GET /backups` - List all backups
- `GET /backups/info` - Get backup manager info
- `POST /backups/new/full` - Create full backup
- `POST /backups/new/partial` - Create partial backup
- `GET /backups/{backup}/info` - Get backup details
- `DELETE /backups/{backup}` - Delete backup
- `POST /backups/{backup}/restore/full` - Restore full backup
- `POST /backups/{backup}/restore/partial` - Restore partial backup

### System Information
- `GET /info` - General system information
- `GET /supervisor/info` - Supervisor information
- `GET /core/info` - Home Assistant Core information
- `GET /os/info` - OS information
- `GET /host/info` - Host information
- `GET /hardware/info` - Hardware information
- `GET /network/info` - Network information

### System Control
- `POST /supervisor/restart` - Restart supervisor
- `POST /core/restart` - Restart Home Assistant Core
- `POST /host/reboot` - Reboot host
- `POST /host/shutdown` - Shutdown host

### Updates
- `GET /available_updates` - List available updates
- `POST /supervisor/update` - Update supervisor
- `POST /core/update` - Update Home Assistant Core
- `POST /os/update` - Update Home Assistant OS

### Statistics
- `GET /supervisor/stats` - Supervisor statistics
- `GET /core/stats` - Core statistics

### Logs
- `GET /supervisor/logs` - Get supervisor logs
- `GET /core/logs` - Get core logs

### Utility
- `GET /health` - Health check endpoint
- `GET /endpoints` - List all available endpoints

## Installation

### As Home Assistant Add-on

1. Add this repository to your Home Assistant Add-on Store
2. Install the "Supervisor API Proxy" add-on
3. Configure the add-on options if needed
4. Start the add-on

### Manual Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/supervisor-api-proxy.git
cd supervisor-api-proxy
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export SUPERVISOR_TOKEN="your_supervisor_token"
```

4. Run the application:
```bash
python app.py
```

## Configuration

### Environment Variables

- `SUPERVISOR_TOKEN`: Required. The Home Assistant Supervisor API token
- `LOG_LEVEL`: Optional. Logging level (default: info)
- `CORS_ORIGINS`: Optional. CORS allowed origins

### Add-on Configuration

```yaml
log_level: info
cors_origins: []
```

## Usage Examples

### Get all add-ons
```bash
curl -X GET http://localhost:8080/api/v1/addons
```

### Start an add-on
```bash
curl -X POST http://localhost:8080/api/v1/addons/core_ssh/start
```

### Create a full backup
```bash
curl -X POST http://localhost:8080/api/v1/backups/new/full \
  -H "Content-Type: application/json" \
  -d '{"name": "My Backup"}'
```

### Get system information
```bash
curl -X GET http://localhost:8080/api/v1/info
```

## Development

### Requirements

- Python 3.8+
- Flask 2.3+
- Home Assistant Supervisor access

### Type Checking

The code includes full type annotations. Run type checking with:

```bash
mypy app.py
```

### Testing

Test the health endpoint:

```bash
curl -X GET http://localhost:8080/api/v1/health
```

## Docker

### Build

```bash
docker build -t supervisor-api-proxy .
```

### Run

```bash
docker run -d \
  -p 8080:8080 \
  -e SUPERVISOR_TOKEN="your_token" \
  supervisor-api-proxy
```

## Security

- Always use HTTPS in production
- Secure your `SUPERVISOR_TOKEN` 
- Limit network access to trusted clients only
- Consider using authentication middleware for additional security

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- Create an issue for bug reports or feature requests
- Check existing issues before creating new ones
- Provide detailed information about your environment

## Changelog

### v1.2.0
- Added full type annotations
- Removed all comments for cleaner code
- Improved error handling
- Added comprehensive API documentation

### v1.1.0
- Added backup management endpoints
- Improved logging and health checks
- Added CORS support

### v1.0.0
- Initial release
- Basic supervisor API proxy functionality