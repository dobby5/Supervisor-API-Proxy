# Troubleshooting Home Assistant Add-on Repository

## Problem: Add-on nicht sichtbar in Home Assistant

### Repository Prüfung

1. **Repository URL korrekt?**
   - URL: `https://github.com/dobby5/Supervisor-API-Proxy`
   - ✅ Repository ist öffentlich zugänglich
   - ✅ `repository.yaml` ist im Root-Verzeichnis vorhanden

2. **Datei-Struktur korrekt?**
   ```
   ✅ repository.yaml (im Root)
   ✅ supervisor_api_proxy/
   ├── ✅ config.yaml
   ├── ✅ Dockerfile
   ├── ✅ app.py
   ├── ✅ requirements.txt
   ├── ✅ run.sh
   ├── ✅ build.yaml
   ├── ✅ README.md
   ├── ✅ CHANGELOG.md
   ├── ✅ icon.png
   └── ✅ logo.png
   ```

### Fehlerbehebung Schritte

1. **Repository Cache leeren in Home Assistant:**
   - Gehe zu Settings → Add-ons → Add-on Store
   - Klicke auf die drei Punkte → "Check for updates"
   - Warte 30 Sekunden und lade die Seite neu

2. **Repository erneut hinzufügen:**
   - Entferne das Repository: Settings → Add-ons → Add-on Store → drei Punkte → Repositories
   - Füge es erneut hinzu: `https://github.com/dobby5/Supervisor-API-Proxy`

3. **Home Assistant Logs überprüfen:**
   - Gehe zu Settings → System → Logs
   - Suche nach Fehlern bezüglich "repository" oder "add-on"

4. **Supervisor Logs:**
   - SSH in Home Assistant
   - Führe aus: `ha supervisor logs`

### Bekannte Probleme

- **Docker Image**: Das Image `ghcr.io/dobby5/supervisor-api-proxy/{arch}` existiert noch nicht
- **Build Process**: Das Add-on muss erst gebaut werden

### Alternative: Lokales Add-on installieren

Falls das Repository nicht funktioniert, kann das Add-on lokal installiert werden:

1. Erstelle Ordner: `/config/addons/local/supervisor_api_proxy/`
2. Kopiere alle Dateien aus `supervisor_api_proxy/` dorthin
3. Das Add-on erscheint unter "Local Add-ons"

### Debug Commands

```bash
# Home Assistant Supervisor Logs
ha supervisor logs

# Repository Update erzwingen
ha addons reload

# Add-on Store neu laden
ha addons update
```