# Start from the official Airflow image
FROM apache/airflow:2.7.3

# Switch to root to install packages
USER airflow

# Install sentence-transformers (includes torch, transformers, etc.)
RUN pip install --no-cache-dir sentence-transformers

# You can add any other packages here, like:
# RUN pip install pandas seaborn matplotlib

# Switch back to Airflow user
USER airflow