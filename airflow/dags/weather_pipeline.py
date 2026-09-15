from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


def hello_weather():
    print("Hello depuis le pipeline météo !")


with DAG(
    dag_id="weather_pipeline",
    start_date=datetime(2026, 9, 15),
    schedule=None,
    catchup=False,
) as dag:

    # test_task = PythonOperator(
    #     task_id="test_weather_pipeline",
    #     python_callable=hello_weather,
    # )

    ingest_weather = BashOperator(
        task_id="ingest_weather",
        bash_command="python /opt/airflow/ingestion/fetch_weather.py",
    )