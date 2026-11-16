#!/bin/sh
# DAG integrity test trong image Airflow chính thức (cùng bản sẽ deploy). Chạy từ gốc repo:
#   docker run --rm -v "$PWD:/opt/booking" -w /opt/booking apache/airflow:2.10.5-python3.12 bash ci/test_dags.sh
set -e
pip install -q apache-airflow-providers-apache-spark acryl-datahub-airflow-plugin pytest \
  -c https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.12.txt
export AIRFLOW__CORE__LOAD_EXAMPLES=False AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////tmp/airflow.db
airflow db migrate > /dev/null
# DAG import governance/, gold_checks, drift_stats như khi deploy (thư mục DAG + các thư mục chung trong PYTHONPATH)
PYTHONPATH=edai1:edai1/dags:edai2/dags python -m pytest tests/test_dag_integrity.py -q -p no:cacheprovider
