# syntax=docker/dockerfile:1.4

# Use lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies first (faster rebuilds if code changes)
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage layer caching
COPY requirements.txt .

# Install Python dependencies (pip cache enabled)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Install system dependencies and SSL certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Now copy the full app (this breaks cache only if your code changes)
COPY . .

# Expose the port used by Flask or Gradio or custom app
EXPOSE 8080

# Default command to run the app
CMD ["python", "app.py"]