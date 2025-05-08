# Use lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy everything into the container
COPY . .

# Install system dependencies for newspaper3k and others
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 7860

# Run the app
CMD ["python", "app.py"]