from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime
from airflow.sensors.python import PythonSensor
from sensors.review_threshold_sensor import check_review_threshold
from tasks import (
    fetch_articles_rss,
    fetch_articles_api,
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

    t1a = PythonOperator(
        task_id="fetch_articles_rss",
        python_callable=fetch_articles_rss
    )

    t1b = PythonOperator(
        task_id="fetch_articles_api",
        python_callable=fetch_articles_api
    )

    # sensor to wait and check for if at least n articles have been labeled
    # within review_queue. if so, triggers t2.
    wait_for_n_labeled = PythonSensor(
        task_id="wait_for_n_labeled",
        python_callable=check_review_threshold,
        poke_interval=300,   # check every 5 minutes (300 seconds)
        timeout=7200,        # give up after 2 hours (7200 seconds)
        mode="poke"
    )

    t2 = PythonOperator(
        task_id="human_review",
        python_callable=human_review
    )

    t3 = PythonOperator(
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

    # DAG flow
    [t1a, t1b] >> wait_for_n_labeled >> t2 >> t3 >> t4 >> t5 >> branch
    branch >> t6a >> t7
    branch >> t6b >> t7