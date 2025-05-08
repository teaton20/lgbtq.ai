# Use official Airflow base image
FROM apache/airflow:2.7.3

# Switch to the airflow user (already set by the base image)
USER airflow

# Install required Python packages
RUN pip install --no-cache-dir \
    sentence-transformers \
    pymongo \
    python-dotenv \
    feedparser \
    newspaper3k