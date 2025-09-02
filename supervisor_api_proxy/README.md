# Supervisor API Proxy Add-on

A lightweight RESTful API proxy for Home Assistant Supervisor functions, providing easy access to add-ons, backups, system information, and more.

## About

This add-on provides a REST API proxy for Home Assistant Supervisor functions, making it easier to interact with your Home Assistant system programmatically.

## Installation

1. Add this repository to your Home Assistant Add-on Store: `https://github.com/dobby5/Supervisor-API-Proxy`
2. Install the "Supervisor API Proxy" add-on
3. Configure the add-on options if needed
4. Start the add-on

## Configuration

```yaml
log_level: info
cors_origins: []
```

### Option: `log_level`

The log level for the application.

### Option: `cors_origins`

List of allowed CORS origins.

## Usage

Once started, the API is available at `http://homeassistant:8080/api/v1/`

For detailed API documentation, see the main repository README.

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/dobby5/Supervisor-API-Proxy/issues).