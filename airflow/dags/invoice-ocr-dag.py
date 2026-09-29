"""Exécute le pipeline d'extraction OCR des factures une fois par jour."""

import pendulum
from airflow.sdk import dag, task


@dag(
    dag_id="dag",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["ocr", "invoice"],
)
def ocr_dag():

    @task
    def run_invoice_extraction():
        from src.extraction import main

        main()

    @task
    def run_invoice_comparison():
        from src.comparison import main

        main()

    run_invoice_extraction() >> run_invoice_comparison()


ocr_dag()
