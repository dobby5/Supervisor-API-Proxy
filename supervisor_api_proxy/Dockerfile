ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install Python and dependencies
RUN apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY run.sh .

# Create s6-overlay service directory and copy run script
RUN mkdir -p /etc/services.d/supervisor-proxy
COPY run.sh /etc/services.d/supervisor-proxy/run
RUN chmod a+x /etc/services.d/supervisor-proxy/run

# Expose port
EXPOSE 8080
