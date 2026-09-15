from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def hello_weather():
    print("Hello depuis le pipeline météo !")


with DAG(
    dag_id="weather_pipeline",
    start_date=datetime(2026, 9, 15),
    schedule=None,
    catchup=False,
) as dag:

    test_task = PythonOperator(
        task_id="test_weather_pipeline",
        python_callable=hello_weather,
    )