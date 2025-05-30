FROM apache/airflow:2.6.0

COPY requirements.txt /
USER airflow
# Copy your DAGs into the DAGs directory
#COPY dags /opt/airflow/dags
RUN pip install --no-cache-dir --progress-bar off -r /requirements.txt


