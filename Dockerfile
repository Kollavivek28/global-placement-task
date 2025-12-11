##############################
# Stage 1: Builder
##############################
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


##############################
# Stage 2: Runtime
##############################
FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

##############################
# Install system dependencies
##############################
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

##############################
# Copy dependencies from builder
##############################
COPY --from=builder /usr/local /usr/local

##############################
# Copy application code
##############################
COPY . .

##############################
# Install cron job file
##############################
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron
RUN crontab /etc/cron.d/2fa-cron

##############################
# Create necessary directories
##############################
RUN mkdir -p /cron && mkdir -p /data
RUN chmod -R 755 /cron && chmod -R 755 /data

EXPOSE 8080

##############################
# Start cron + API server
##############################
CMD cron && uvicorn main:app --host 0.0.0.0 --port 8080
