"""DAG integrity cho cả edai1/dags và edai2/dags: import không lỗi, đúng task + thứ tự, chuỗi Airflow Dataset nối đúng.

Chạy trong image apache/airflow:2.10.5-python3.12 (Airflow không chạy trên Windows), xem ci/test_dags.sh.
  - import   : DagBag không có import_errors (Variable có default, Connection chỉ đọc lúc chạy task)
  - cấu trúc : DP1 check -> ingest -> validate theo bảng; DP2/DP3 đợi DAG trước; drift_monitor short-circuit trước retrain
  - Dataset  : outlet của dp3.validate_features = schedule của feast_materialize_incremental; outlet của materialize
               = schedule của score_bookings (đổi URI một bên thì chuỗi đứt mà không lỗi -> test bắt)
"""
import os

import pytest
from airflow.models import DagBag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def dags():
    out = {}
    for folder in ("edai1/dags", "edai2/dags"):
        bag = DagBag(dag_folder=os.path.join(ROOT, folder), include_examples=False)
        assert not bag.import_errors, bag.import_errors
        out.update(bag.dags)
    return out


def upstream(dag, task_id):
    return set(dag.get_task(task_id).upstream_task_ids)


def test_all_dags_present(dags):
    assert set(dags) == {"dp1_ingest_bronze", "dp1_load_dims", "dp2_bronze_to_gold", "dp3_offline_features",
                         "rag_data_pipeline", "feast_materialize_incremental", "feast_materialize_realtime",
                         "score_bookings", "drift_monitor"}


def test_dp_structure(dags):
    dp1 = dags["dp1_ingest_bronze"]
    for t in ("quotes", "bookings", "payments", "cancellations"):
        assert upstream(dp1, f"ingest_{t}") == {f"check_{t}"} and upstream(dp1, f"validate_{t}") == {f"ingest_{t}"}
    dp2 = dags["dp2_bronze_to_gold"]
    assert [t.task_id for t in dp2.topological_sort()] == ["wait_dp1", "silver_bookings", "stage_gold", "upsert_gold",
                                                           "validate_gold"]
    dp3 = dags["dp3_offline_features"]
    assert upstream(dp3, "validate_features") == {"build_features"} and upstream(dp3, "build_features") == {"wait_dp2"}
    assert all(d.max_active_runs == 1 for d in (dp2, dp3))


def test_dataset_chain(dags):
    outlets = lambda dag, task: {d.uri for d in dags[dag].get_task(task).outlets if hasattr(d, "uri")}
    schedule = lambda dag: {uri for uri, _ in dags[dag].timetable.dataset_condition.iter_datasets()}
    assert outlets("dp3_offline_features", "validate_features") == schedule("feast_materialize_incremental")
    assert outlets("feast_materialize_incremental", "materialize") == schedule("score_bookings")


def test_drift_monitor_gates_retrain(dags):
    d = dags["drift_monitor"]
    assert upstream(d, "retrain") == {"plan_retrain"} and upstream(d, "plan_retrain") == {"measure"}
