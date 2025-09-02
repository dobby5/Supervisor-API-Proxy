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
COPY run.sh /
RUN chmod a+x /run.sh

# Expose port
EXPOSE 8080

# Use standard CMD for Home Assistant add-ons
CMD [ "/run.sh" ]
