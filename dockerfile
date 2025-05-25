FROM apache/nifi:latest

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --break-system-packages --no-cache-dir pandas numpy && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER nifi