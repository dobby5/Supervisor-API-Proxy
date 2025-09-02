FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies (minimal set for our Flask app)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget jq dos2unix \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Fix line endings and make run script executable
RUN dos2unix run.sh \
 && chmod +x run.sh

# Expose port
EXPOSE 8080

# Use ENTRYPOINT with bash like the working example
ENTRYPOINT ["/bin/bash", "/app/run.sh"]