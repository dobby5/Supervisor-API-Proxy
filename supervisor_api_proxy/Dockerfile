# Use simple Alpine Linux instead of HA base image to avoid s6-overlay issues
FROM alpine:3.18

# Install Python and dependencies
RUN apk add --no-cache python3 py3-pip bash

# Set working directory  
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy apps
COPY app.py .
COPY app-simple.py .

# Copy simple startup script (no bashio)
COPY run-direct.sh /
RUN chmod +x /run-direct.sh

# Expose port
EXPOSE 8080

# Direct startup without s6-overlay
CMD ["/run-direct.sh"]