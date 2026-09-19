ARG AIRFLOW_VERSION=3.1.7
ARG PYTHON_VERSION=3.12
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

ARG AIRFLOW_VERSION
ARG PYTHON_VERSION

# Pas de __pycache__ dans les dossiers montés depuis l'hôte
ENV PYTHONDONTWRITEBYTECODE=1

# Dossier de la base SQLite, créé ici pour que le volume nommé appartienne à l'utilisateur airflow
RUN mkdir -p /opt/airflow/db

COPY --chown=airflow:0 airflow/start.sh /opt/airflow/start.sh
COPY --chown=airflow:0 pyproject.toml requirements.txt /tmp/invoice-ocr/
COPY --chown=airflow:0 src /tmp/invoice-ocr/src

RUN pip install --no-cache-dir /tmp/invoice-ocr \
        --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt" \
    && rm -rf /tmp/invoice-ocr
