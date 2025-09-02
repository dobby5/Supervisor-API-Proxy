# Use official Python Alpine image for better compatibility
FROM python:3.11-alpine

# Install system dependencies
RUN apk add --no-cache \
    bash \
    curl \
    jq

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /tmp/*

# Copy application files
COPY app.py /app/
COPY run-python-only.sh /run.sh
RUN chmod a+x /run.sh

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8099/api/v1/health || exit 1

# Expose port
EXPOSE 8099

# Labels
LABEL \
    io.hass.name="Supervisor API Proxy" \
    io.hass.description="A REST API proxy for Home Assistant Supervisor" \
    io.hass.arch="armhf|aarch64|i386|amd64|armv7" \
    io.hass.type="addon" \
    io.hass.version="1.0.0" \
    maintainer="Local Development" \
    org.opencontainers.image.title="Supervisor API Proxy" \
    org.opencontainers.image.description="A REST API proxy for Home Assistant Supervisor" \
    org.opencontainers.image.licenses="MIT"

CMD ["/run.sh"]