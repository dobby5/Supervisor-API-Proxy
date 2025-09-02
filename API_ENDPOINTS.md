# Home Assistant Supervisor API Proxy - Vollständige Endpoint-Dokumentation

## Base URL
```
http://your-ha-ip:8099/api/v1/
```

## Authentifizierung
Alle Requests benötigen den `Authorization: Bearer <supervisor_token>` Header.

---

## 🏥 Health & Discovery

### Health Check
- `GET /api/v1/health` - Gesundheitsstatus der API und Supervisor-Verbindung

### API Discovery  
- `GET /api/v1/discovery` - Liste aller verfügbaren Endpoints

---

## 🔌 Add-ons Management

### Add-on Liste & Verwaltung
- `GET /api/v1/addons` - Liste aller Add-ons
- `POST /api/v1/addons/reload` - Add-ons neu laden

### Add-on Details & Medien
- `GET /api/v1/addons/<slug>` - Add-on Informationen abrufen  
- `POST /api/v1/addons/<slug>` - Add-on Konfiguration ändern
- `GET /api/v1/addons/<slug>/changelog` - Add-on Changelog
- `GET /api/v1/addons/<slug>/documentation` - Add-on Dokumentation
- `GET /api/v1/addons/<slug>/icon` - Add-on Icon
- `GET /api/v1/addons/<slug>/logo` - Add-on Logo

### Add-on Lifecycle
- `POST /api/v1/addons/<slug>/install` - Add-on installieren
- `POST /api/v1/addons/<slug>/uninstall` - Add-on deinstallieren  
- `POST /api/v1/addons/<slug>/start` - Add-on starten
- `POST /api/v1/addons/<slug>/stop` - Add-on stoppen
- `POST /api/v1/addons/<slug>/restart` - Add-on neustarten
- `POST /api/v1/addons/<slug>/update` - Add-on aktualisieren
- `POST /api/v1/addons/<slug>/rebuild` - Add-on neu bauen

### Add-on Konfiguration & Sicherheit
- `POST /api/v1/addons/<slug>/options` - Add-on Optionen setzen
- `POST /api/v1/addons/<slug>/options/validate` - Add-on Optionen validieren  
- `POST /api/v1/addons/<slug>/security` - Add-on Sicherheitseinstellungen
- `POST /api/v1/addons/<slug>/stdin` - Eingabe an Add-on senden

### Add-on Monitoring
- `GET /api/v1/addons/<slug>/logs` - Add-on Logs (mit Streaming Support)
- `GET /api/v1/addons/<slug>/stats` - Add-on Statistiken

---

## 💾 Backup Management  

### Backup Liste & Info
- `GET /api/v1/backups` - Liste aller Backups
- `GET /api/v1/backups/info` - Backup System Information
- `GET /api/v1/backups/<slug>` - Backup Details
- `DELETE /api/v1/backups/<slug>` - Backup löschen

### Backup Erstellung
- `POST /api/v1/backups/new/full` - Vollständiges Backup erstellen
- `POST /api/v1/backups/new/partial` - Partielles Backup erstellen

### Backup Wiederherstellung & Download  
- `GET /api/v1/backups/<slug>/download` - Backup herunterladen
- `POST /api/v1/backups/<slug>/restore/full` - Vollständige Wiederherstellung
- `POST /api/v1/backups/<slug>/restore/partial` - Partielle Wiederherstellung

### Backup Konfiguration
- `POST /api/v1/backups/options` - Backup Optionen setzen
- `POST /api/v1/backups/reload` - Backup System neu laden

---

## 🏠 Home Assistant Core

### Core Information & Status
- `GET /api/v1/core/info` - Home Assistant Core Informationen
- `GET /api/v1/core/stats` - Core Statistiken  
- `GET /api/v1/core/logs` - Core Logs

### Core Management
- `GET /api/v1/core/api` - Core API Zugriff
- `POST /api/v1/core/api` - Core API Operationen
- `POST /api/v1/core/check` - Core Gesundheits-Check
- `POST /api/v1/core/options` - Core Optionen setzen
- `POST /api/v1/core/update` - Core aktualisieren
- `POST /api/v1/core/restart` - Core neustarten

---

## 🖥️ Host & Operating System

### Host System
- `GET /api/v1/host/info` - Host System Informationen
- `GET /api/v1/host/logs` - Host System Logs
- `GET /api/v1/host/services` - Host Services Liste
- `POST /api/v1/host/options` - Host Optionen setzen
- `POST /api/v1/host/reboot` - Host neustarten
- `POST /api/v1/host/shutdown` - Host herunterfahren

### Operating System
- `GET /api/v1/os/info` - OS Informationen
- `POST /api/v1/os/update` - OS aktualisieren
- `POST /api/v1/os/config/sync` - OS Konfiguration synchronisieren
- `POST /api/v1/os/boot-slot` - OS Boot-Slot setzen

### OS Storage Management
- `GET /api/v1/os/config/swap` - Swap Konfiguration abrufen
- `POST /api/v1/os/config/swap` - Swap Konfiguration setzen
- `GET /api/v1/os/datadisk/list` - Datenträger auflisten
- `POST /api/v1/os/datadisk/move` - Datenträger verschieben  
- `POST /api/v1/os/datadisk/wipe` - Datenträger löschen

### OS Hardware Boards
- `GET /api/v1/os/boards/<board>` - Hardware Board Informationen
- `GET /api/v1/os/boards/yellow` - Yellow Board Status
- `POST /api/v1/os/boards/yellow` - Yellow Board Konfiguration
- `GET /api/v1/os/boards/green` - Green Board Status  
- `POST /api/v1/os/boards/green` - Green Board Konfiguration

---

## 🌐 Network Management

### Network Information
- `GET /api/v1/network/info` - Netzwerk Informationen
- `POST /api/v1/network/reload` - Netzwerk neu laden

### Network Interface Management  
- `GET /api/v1/network/interface/<interface>/info` - Interface Details
- `POST /api/v1/network/interface/<interface>/update` - Interface aktualisieren
- `GET /api/v1/network/interface/<interface>/accesspoints` - WLAN Access Points
- `POST /api/v1/network/interface/<interface>/vlan/<vlan_id>` - VLAN Konfiguration

---

## 🛒 Add-on Store

### Store Navigation
- `GET /api/v1/store` - Store Informationen
- `GET /api/v1/store/addons` - Store Add-ons auflisten
- `GET /api/v1/store/addons/<slug>` - Store Add-on Details

### Store Add-on Management
- `POST /api/v1/store/addons/<slug>/install` - Store Add-on installieren
- `POST /api/v1/store/addons/<slug>/update` - Store Add-on aktualisieren
- `GET /api/v1/store/addons/<slug>/changelog` - Store Add-on Changelog
- `GET /api/v1/store/addons/<slug>/documentation` - Store Add-on Dokumentation
- `GET /api/v1/store/addons/<slug>/icon` - Store Add-on Icon

### Repository Management
- `GET /api/v1/store/repositories` - Repositories auflisten
- `POST /api/v1/store/repositories` - Repository hinzufügen
- `DELETE /api/v1/store/repositories/<slug>` - Repository entfernen

---

## ⚙️ System Services & Jobs

### Job Management
- `GET /api/v1/jobs` - Jobs auflisten
- `GET /api/v1/jobs/info` - Job System Information
- `GET /api/v1/jobs/<uuid>` - Spezifischen Job abrufen
- `POST /api/v1/jobs/options` - Job Optionen setzen
- `POST /api/v1/jobs/reset` - Jobs zurücksetzen

### Services Management
- `GET /api/v1/services` - Services auflisten  
- `GET /api/v1/services/<service>` - Service Details
- `GET /api/v1/services/mqtt` - MQTT Service Status
- `POST /api/v1/services/mqtt` - MQTT Service konfigurieren
- `DELETE /api/v1/services/mqtt` - MQTT Service entfernen
- `GET /api/v1/services/mysql` - MySQL Service Status
- `POST /api/v1/services/mysql` - MySQL Service konfigurieren
- `DELETE /api/v1/services/mysql` - MySQL Service entfernen

---

## 🔊 Audio System

### Audio Information & Control
- `GET /api/v1/audio/info` - Audio System Informationen
- `GET /api/v1/audio/logs` - Audio System Logs
- `POST /api/v1/audio/reload` - Audio System neu laden
- `POST /api/v1/audio/restart` - Audio System neustarten
- `POST /api/v1/audio/update` - Audio System aktualisieren

### Audio Input/Output Management  
- `POST /api/v1/audio/default/input` - Standard Audio-Eingang setzen
- `POST /api/v1/audio/default/output` - Standard Audio-Ausgang setzen
- `POST /api/v1/audio/mute/input` - Audio-Eingang stumm schalten
- `POST /api/v1/audio/mute/output` - Audio-Ausgang stumm schalten
- `POST /api/v1/audio/volume/input` - Eingangslautstärke setzen
- `POST /api/v1/audio/volume/output` - Ausgangslautstärke setzen
- `POST /api/v1/audio/profile` - Audio-Profil setzen

---

## 🌍 DNS & Discovery

### DNS Management
- `GET /api/v1/dns/info` - DNS Informationen
- `GET /api/v1/dns/logs` - DNS Logs
- `GET /api/v1/dns/stats` - DNS Statistiken
- `POST /api/v1/dns/options` - DNS Optionen setzen
- `POST /api/v1/dns/restart` - DNS neustarten  
- `POST /api/v1/dns/update` - DNS aktualisieren

### Discovery Management
- `GET /api/v1/discovery` - Discoveries auflisten
- `POST /api/v1/discovery` - Discovery hinzufügen
- `GET /api/v1/discovery/<uuid>` - Discovery Details
- `DELETE /api/v1/discovery/<uuid>` - Discovery entfernen

---

## 🔐 Authentication & Security

### Authentication
- `GET /api/v1/auth` - Auth Status
- `POST /api/v1/auth` - Authentifizierung
- `POST /api/v1/auth/reset` - Auth zurücksetzen
- `GET /api/v1/auth/list` - Auth Einträge auflisten
- `DELETE /api/v1/auth/cache` - Auth Cache löschen

### Security
- `GET /api/v1/security/info` - Sicherheitsinformationen

---

## 🖥️ Hardware & System Monitoring  

### Hardware Information
- `GET /api/v1/hardware/info` - Hardware Informationen
- `GET /api/v1/hardware/audio` - Audio Hardware Details

### System Resolution & Health
- `GET /api/v1/resolution/info` - Resolution System Status  
- `GET /api/v1/resolution/suggestions` - Systemvorschläge
- `GET /api/v1/resolution/issue/<uuid>/suggestions` - Issue-spezifische Vorschläge
- `POST /api/v1/resolution/suggestion/<uuid>` - Vorschlag anwenden
- `DELETE /api/v1/resolution/suggestion/<uuid>` - Vorschlag ablehnen
- `DELETE /api/v1/resolution/issue/<uuid>` - Issue löschen
- `POST /api/v1/resolution/healthcheck` - Gesundheits-Check ausführen
- `POST /api/v1/resolution/check/<slug>/options` - Check Optionen setzen
- `POST /api/v1/resolution/check/<slug>/run` - Spezifischen Check ausführen

### Observer & Monitoring
- `GET /api/v1/observer/info` - Observer Informationen
- `GET /api/v1/observer/stats` - Observer Statistiken  
- `POST /api/v1/observer/update` - Observer aktualisieren

### Multicast System
- `GET /api/v1/multicast/info` - Multicast Informationen
- `GET /api/v1/multicast/logs` - Multicast Logs
- `GET /api/v1/multicast/stats` - Multicast Statistiken
- `POST /api/v1/multicast/restart` - Multicast neustarten
- `POST /api/v1/multicast/update` - Multicast aktualisieren

---

## 🚪 Ingress & Web Interface

### Ingress Management
- `GET /api/v1/ingress/panels` - Ingress Panels auflisten
- `POST /api/v1/ingress/session` - Ingress Session erstellen  
- `POST /api/v1/ingress/validate_session` - Session validieren

---

## 🐳 Docker & Infrastructure  

### Docker Management
- `GET /api/v1/docker/info` - Docker Informationen
- `POST /api/v1/docker/options` - Docker Optionen setzen
- `GET /api/v1/docker/registries` - Docker Registries auflisten
- `POST /api/v1/docker/registries` - Docker Registry hinzufügen
- `DELETE /api/v1/docker/registries/<registry>` - Docker Registry entfernen

### Mounts Management
- `GET /api/v1/mounts` - Mounts auflisten
- `POST /api/v1/mounts` - Mount erstellen
- `POST /api/v1/mounts/options` - Mount Optionen setzen  
- `PUT /api/v1/mounts/<name>` - Mount aktualisieren
- `DELETE /api/v1/mounts/<name>` - Mount entfernen
- `POST /api/v1/mounts/<name>/reload` - Mount neu laden

### CLI Interface
- `GET /api/v1/cli/info` - CLI Informationen
- `GET /api/v1/cli/stats` - CLI Statistiken
- `POST /api/v1/cli/update` - CLI aktualisieren

---

## 🔧 Supervisor Management

### Supervisor Status & Information
- `GET /api/v1/supervisor/info` - Supervisor Informationen
- `GET /api/v1/supervisor/logs` - Supervisor Logs
- `GET /api/v1/supervisor/stats` - Supervisor Statistiken

### Supervisor Control
- `POST /api/v1/supervisor/options` - Supervisor Optionen setzen
- `POST /api/v1/supervisor/update` - Supervisor aktualisieren
- `POST /api/v1/supervisor/reload` - Supervisor neu laden
- `POST /api/v1/supervisor/restart` - Supervisor neustarten
- `POST /api/v1/supervisor/repair` - Supervisor reparieren

---

## 📝 Request/Response Format

### Request Headers
```
Authorization: Bearer <supervisor_token>
Content-Type: application/json
```

### Response Format
```json
{
  "result": "ok",
  "data": {...}
}
```

### Error Format
```json
{
  "result": "error", 
  "message": "Error description"
}
```

---

## 🌟 Features

- ✅ **Vollständige Supervisor API Abdeckung** - Über 140+ Endpoints
- ✅ **Streaming Support** - Für Logs und Live-Daten  
- ✅ **CORS Konfiguration** - Für Web/Mobile Apps
- ✅ **Type-Safe Implementation** - Vollständige Python Type Hints
- ✅ **Error Handling** - Umfassende Fehlerbehandlung
- ✅ **Health Monitoring** - Eingebaute Gesundheitschecks
- ✅ **API Discovery** - Automatische Endpoint-Erkennung

**Insgesamt: 140+ Endpoints vollständig implementiert**