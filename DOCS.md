# Home Assistant Supervisor API Proxy

This add-on provides a secure proxy to the Home Assistant Supervisor API, allowing external applications to interact with your Home Assistant system through a controlled interface.

## Installation

1. Add this repository to your Home Assistant supervisor
2. Install the "Supervisor API Proxy" add-on
3. Start the add-on

## Configuration

The add-on runs on port 8099 by default and provides access to Supervisor API endpoints through a unified REST interface.

## Usage

Once running, you can access the API at:
```
http://your-ha-ip:8099/api/v1/
```

All requests require the `Authorization: Bearer <supervisor_token>` header.

## Security

- The add-on only exposes selected Supervisor API endpoints
- All requests are authenticated and authorized
- No sensitive system operations are exposed without proper authentication

## Support

For support and issues, please check the Home Assistant Community forums.