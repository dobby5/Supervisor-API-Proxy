# Home Assistant Supervisor API Proxy Add-on

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/homeassistant/addons.svg
[commits]: https://github.com/homeassistant/addons/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[license-shield]: https://img.shields.io/github/license/homeassistant/addons.svg
[releases-shield]: https://img.shields.io/github/release/homeassistant/addons.svg
[releases]: https://github.com/homeassistant/addons/releases

## About

The Supervisor API Proxy add-on provides a REST API interface to access Home Assistant Supervisor functionality from external applications, particularly Android apps. This add-on acts as a secure proxy between external clients and the Home Assistant Supervisor API.

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

## Installation

1. Add this repository to your Home Assistant Add-on store
2. Install the "Supervisor API Proxy" add-on
3. Configure the add-on (see Configuration section)
4. Start the add-on
5. Access the API at `http://your-ha-ip:8099/api/v1/`

## Configuration

Example configuration:

```yaml
log_level: info
cors_origins:
  - "*"  # Allow all origins (use specific domains in production)
port: 8099
ssl: false
certfile: fullchain.pem
keyfile: privkey.pem
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `log_level` | `info` | Log level (trace, debug, info, notice, warning, error, fatal) |
| `cors_origins` | `["*"]` | List of allowed CORS origins |
| `port` | `8099` | Port for the API server |
| `ssl` | `false` | Enable SSL/TLS |
| `certfile` | `fullchain.pem` | SSL certificate file |
| `keyfile` | `privkey.pem` | SSL private key file |

## API Documentation

### Base URL
```
http://your-ha-ip:8099/api/v1/
```

### Authentication
All requests require the `Authorization: Bearer <supervisor_token>` header.

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

### Example API Calls

#### Get Add-on List
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://your-ha-ip:8099/api/v1/addons
```

#### Create Backup
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "my-backup"}' \
     http://your-ha-ip:8099/api/v1/backups
```

#### Get Streaming Logs
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://your-ha-ip:8099/api/v1/addons/my-addon/logs?follow=true
```

## Security Considerations

⚠️ **Important Security Notes:**

- Always use specific CORS origins in production (not `"*"`)
- Consider enabling SSL/TLS for external access
- Regularly rotate your Supervisor tokens
- Monitor access logs for suspicious activity
- Use firewall rules to restrict access to trusted networks

## Troubleshooting

### Common Issues

**Connection Refused**
- Check if the add-on is running
- Verify port configuration
- Ensure firewall allows traffic on the configured port

**Unauthorized Access**
- Verify Supervisor token is valid
- Check token has proper permissions
- Ensure Authorization header format is correct

**CORS Errors**
- Add your client's origin to `cors_origins` configuration
- Restart the add-on after configuration changes

### Debug Mode

Enable debug logging by setting `log_level: debug` in configuration.

## Development

### Local Testing
```bash
# Clone repository
git clone https://github.com/your-repo/supervisor-api-proxy
cd supervisor-api-proxy

# Build Docker image
docker build -t supervisor-proxy .

# Run locally
docker run -p 8099:8099 -e SUPERVISOR_TOKEN=your_token supervisor-proxy
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- 📚 [Documentation](https://github.com/your-repo/supervisor-api-proxy)
- 🐛 [Issue Tracker](https://github.com/your-repo/supervisor-api-proxy/issues)
- 💬 [Home Assistant Community](https://community.home-assistant.io/)

## License

MIT License - see [LICENSE](LICENSE) file for details.