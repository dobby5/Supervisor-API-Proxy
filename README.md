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

- 🔌 **Full Supervisor API Proxy** - Access all Supervisor endpoints
- 📱 **Mobile App Support** - Optimized for Android app integration  
- 🔒 **Secure Access** - Token-based authentication with CORS support
- 🚀 **RESTful API** - Clean REST endpoints with /api/v1/ prefix
- 📊 **Real-time Logs** - Streaming log support with range headers
- 🔄 **Job Management** - Monitor and control Supervisor jobs
- 💾 **Backup Management** - Create, restore and manage backups
- 🏠 **Add-on Control** - Install, configure and manage add-ons
- 📈 **System Monitoring** - Access system stats and information
- ⚡ **Health Checks** - Built-in health monitoring endpoints

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

### Available Endpoints

| Category | Endpoint | Methods | Description |
|----------|----------|---------|-------------|
| **Health** | `/health` | GET | Health check |
| **Discovery** | `/discovery` | GET | List available endpoints |
| **Add-ons** | `/addons` | GET | List all add-ons |
| **Add-ons** | `/addons/{slug}` | GET, POST | Get/update add-on |
| **Add-ons** | `/addons/{slug}/install` | POST | Install add-on |
| **Add-ons** | `/addons/{slug}/uninstall` | POST | Uninstall add-on |
| **Add-ons** | `/addons/{slug}/start` | POST | Start add-on |
| **Add-ons** | `/addons/{slug}/stop` | POST | Stop add-on |
| **Add-ons** | `/addons/{slug}/logs` | GET | Get add-on logs |
| **Backups** | `/backups` | GET, POST | List/create backups |
| **Backups** | `/backups/{slug}` | GET, DELETE | Get/delete backup |
| **Backups** | `/backups/{slug}/restore/full` | POST | Full restore |
| **Backups** | `/backups/{slug}/restore/partial` | POST | Partial restore |
| **System** | `/supervisor/info` | GET | Supervisor information |
| **System** | `/core/info` | GET | Core information |
| **System** | `/host/info` | GET | Host information |
| **System** | `/os/info` | GET | OS information |

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

## Android Integration

This add-on is designed for Android app integration. See the [Android Client Documentation](docs/android-client.md) for Kotlin implementation examples.

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

## Changelog

### v1.0.0
- Initial release
- Full Supervisor API proxy functionality
- Android client support
- CORS configuration
- Health monitoring
- Streaming logs support