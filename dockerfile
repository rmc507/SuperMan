# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . /app/

# Make the scripts executable
RUN chmod +x /app/superman && \
    chmod +x /app/superman.py

# Create necessary directories and links
RUN mkdir -p /root/bin && \
    mkdir -p /root/Coding/smartman && \
    ln -s /app/superman.py /root/Coding/smartman/superman.py && \
    ln -s /app/superman /root/bin/superman

# Add superman alias to .bashrc
RUN echo "alias superman='history | tail -50 > /tmp/superman_current_history && /root/bin/superman'" >> /root/.bashrc

# Create entrypoint script
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'if [ $# -eq 0 ]; then' >> /app/entrypoint.sh && \
    echo '    bash' >> /app/entrypoint.sh && \
    echo 'else' >> /app/entrypoint.sh && \
    echo '    /root/bin/superman "$@"' >> /app/entrypoint.sh && \
    echo 'fi' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
