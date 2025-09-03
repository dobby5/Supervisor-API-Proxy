ARG BUILD_FROM=ghcr.io/hassio-addons/base:14.0.5
FROM ${BUILD_FROM}

# Python + requirements
RUN apk add --no-cache python3 py3-pip
COPY proxy.py /proxy.py
RUN pip3 install flask requests

CMD ["python3", "/proxy.py"]
