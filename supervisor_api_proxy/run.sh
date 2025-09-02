#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Supervisor API Proxy..."

cd /app
python3 app.py