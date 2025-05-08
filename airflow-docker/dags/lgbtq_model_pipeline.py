from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
from tasks import (
    fetch_articles,
    human_review,
    get_embeddings,
    retrain,
    get_metrics,
    deploy_model,
    keep_model,
    notify_admin,
    decide_branch
)

with DAG(
    "lgbtq_model_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["lgbtq_ai"]
) as dag:

    t1 = PythonOperator(
        task_id="fetch_articles",
        python_callable=fetch_articles
    )

    t2 = PythonOperator(
        task_id="human_review",
        python_callable=human_review
    )

    t3 = PythonOperator(  # new get_embeddings step
        task_id="get_embeddings",
        python_callable=get_embeddings
    )

    t4 = PythonOperator(
        task_id="retrain",
        python_callable=retrain
    )

    t5 = PythonOperator(
        task_id="get_metrics",
        python_callable=get_metrics
    )

    branch = BranchPythonOperator(
        task_id="decide_branch",
        python_callable=decide_branch
    )

    t6a = PythonOperator(
        task_id="deploy_model",
        python_callable=deploy_model
    )

    t6b = PythonOperator(
        task_id="keep_model",
        python_callable=keep_model
    )

    t7 = PythonOperator(
        task_id="notify_admin",
        python_callable=notify_admin,
        trigger_rule="none_failed_min_one_success"
    )

    # Define DAG flow
    t1 >> t2 >> t3 >> t4 >> t5 >> branch
    branch >> t6a >> t7
    branch >> t6b >> t7