ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN \
    apk add --no-cache --virtual .build-dependencies \
        gcc \
        musl-dev \
        python3-dev \
    && apk add --no-cache \
        python3 \
        py3-pip \
        bash \
        curl \
        jq \
    && pip3 install --no-cache-dir --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && apk del .build-dependencies \
    && rm -rf /var/cache/apk/* /tmp/*

# Copy application files
COPY app.py /app/
COPY run.sh /
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
    maintainer="Home Assistant Add-on Developer" \
    org.opencontainers.image.title="Supervisor API Proxy" \
    org.opencontainers.image.description="A REST API proxy for Home Assistant Supervisor" \
    org.opencontainers.image.vendor="Home Assistant Community Add-ons" \
    org.opencontainers.image.authors="Add-on Developer" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.source="https://github.com/homeassistant/addons"

CMD ["/run.sh"]