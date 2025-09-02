# Lokale Installation - Supervisor API Proxy

## Voraussetzungen
- Home Assistant mit Supervisor
- SSH-Zugang zu Home Assistant

## Installation als lokales Add-on

### Option 1: Direkte Ordner-Installation

1. **Add-on Ordner erstellen:**
   ```bash
   mkdir -p /addons/supervisor_api_proxy
   ```

2. **Dateien kopieren:**
   Kopieren Sie alle Dateien aus diesem Verzeichnis nach `/addons/supervisor_api_proxy/`

3. **Add-on in Home Assistant installieren:**
   - Gehen Sie zu **Supervisor → Add-on Store**
   - Klicken Sie auf **⋮** (drei Punkte) oben rechts
   - Wählen Sie **Check for updates**
   - Das Add-on "Supervisor API Proxy" erscheint unter "Local add-ons"
   - Klicken Sie auf das Add-on und dann auf **INSTALL**

### Option 2: Via SSH Upload

1. **Dateien per SSH hochladen:**
   ```bash
   scp -r ./* root@your-ha-ip:/addons/supervisor_api_proxy/
   ```

2. **Home Assistant Add-on Store aktualisieren**
   - **Supervisor → Add-on Store → ⋮ → Check for updates**

## Konfiguration

Nach der Installation:

1. **Add-on konfigurieren:**
   ```yaml
   log_level: info
   cors_origins:
     - "*"
   port: 8099
   ssl: false
   ```

2. **Add-on starten:**
   - Klicken Sie auf **START**
   - Aktivieren Sie **"Start on boot"** falls gewünscht
   - Aktivieren Sie **"Show in sidebar"** für schnellen Zugang

## Zugriff

- **API Base URL:** `http://your-ha-ip:8099/api/v1/`
- **Health Check:** `http://your-ha-ip:8099/api/v1/health`
- **API Discovery:** `http://your-ha-ip:8099/api/v1/discovery`

## Lokaler Build (Optional)

Falls Sie das Docker Image manuell bauen möchten:

```bash
cd /addons/supervisor_api_proxy
docker build -t local/supervisor-api-proxy .
```

## Troubleshooting

**Add-on erscheint nicht:**
- Überprüfen Sie, dass alle Dateien in `/addons/supervisor_api_proxy/` sind
- Führen Sie "Check for updates" im Add-on Store aus
- Überprüfen Sie die Supervisor-Logs

**Installation schlägt fehl:**
- Überprüfen Sie die Docker-Logs: `docker logs <container_id>`
- Stellen Sie sicher, dass Port 8099 nicht bereits verwendet wird

**API nicht erreichbar:**
- Überprüfen Sie die Add-on-Logs
- Stellen Sie sicher, dass `SUPERVISOR_TOKEN` verfügbar ist (wird automatisch gesetzt)
- Überprüfen Sie die Netzwerk-Einstellungen