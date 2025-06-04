# Airflow-Docker Backend

This folder contains the backend data pipeline infrastructure.

It includes:
- Airflow DAGs for automating data ingestion, retraining, and deployment.
- Docker setup for running Airflow locally or in production.
- Scripts for monitoring model performance and triggering retraining.

This is the core backend orchestration layer of the LGBTQ.AI+ platform.

All scripts can be found in /dags/tasks. The 'lgbtq_model_pipeline.py' script
in /dags/ shows the flow of the DAG and ties each task together. 