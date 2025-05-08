# Start from the official Airflow image
FROM apache/airflow:2.7.3

# Switch to root temporarily (required for system-level installs — not needed here)
USER airflow

# Install necessary packages as Airflow user
RUN pip install --no-cache-dir \
    sentence-transformers \
    pymongo \
    python-dotenv

# You can add any other packages here
# RUN pip install pandas seaborn matplotlib