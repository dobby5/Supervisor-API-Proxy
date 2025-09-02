#!/usr/bin/with-contenv bashio

bashio::log.info "=== STARTING SIMPLE TEST VERSION ==="
bashio::log.info "Current directory: $(pwd)"
bashio::log.info "Changing to /app directory..."

cd /app
bashio::log.info "New directory: $(pwd)"
bashio::log.info "Files in /app: $(ls -la)"

bashio::log.info "Starting Python application..."
python3 app-simple.py

bashio::log.info "Python application has exited with code: $?"