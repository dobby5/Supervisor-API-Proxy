ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install Python
RUN apk add --no-cache python3 py3-pip

# Set working directory  
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy apps (both versions for testing)
COPY app.py .
COPY app-simple.py .

# Copy and set run script
COPY run-simple.sh /
RUN chmod +x /run-simple.sh

# Expose port
EXPOSE 8080

# Start with simple version for testing
CMD ["/run-simple.sh"]