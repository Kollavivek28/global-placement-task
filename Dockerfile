##############################
# Stage 1: Builder
##############################
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies (optimized for caching)
RUN pip install --no-cache-dir -r requirements.txt


##############################
# Stage 2: Runtime
##############################
FROM python:3.11-slim

# Set timezone to UTC (critical!)
ENV TZ=UTC

# Set working directory
WORKDIR /app

##############################
# Install system dependencies
##############################
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

##############################
# Configure timezone
##############################
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
# Setup cron job (if needed)
##############################
# Create cron directory
RUN mkdir -p /cron
RUN mkdir -p /data

# Set permissions
RUN chmod -R 755 /data
RUN chmod -R 755 /cron

##############################
# Expose API port
##############################
EXPOSE 8080

##############################
# Start cron + API server
##############################
CMD cron && uvicorn main:app --host 0.0.0.0 --port 8080
