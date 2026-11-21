# ML pipeline

Notebook, Kubeflow pipeline, training phân tán, MLflow và versioning dữ liệu train.

<a id="edai-2-13"></a>
## Training pipeline 4 bước (Load Feast → Split → Train → Evaluate)

Code pipeline: [`edai2/ml/training_pipeline.py`](../../edai2/ml/training_pipeline.py), [`edai2/ci/kfp_run.py`](../../edai2/ci/kfp_run.py) và [`edai2/ml/run_steps.py`](../../edai2/ml/run_steps.py) cho mô hình `cancel-risk`.

Pipeline gồm 4 bước: `load_from_feast` → `split_by_time` → `train` → `evaluate_and_register`. Dữ liệu lấy theo cửa sổ thời gian (`[2025-01-01, 2025-06-01)` cho v1, sau mốc drift `2025-06-01` cho v2), lấy mẫu `sample_pct` theo `booking_id`, sử dụng nhãn từ view `gold.labels_cancel` (chỉ gồm booking đã chín nhãn) cùng các feature như `loyalty_tier`, `has_customer_history`.

Sau khi nâng quota CPU lên 32 vCPU và triển khai **Kubeflow Pipelines 2.4.1** vào namespace `kubeflow` trên GKE, pipeline `cancel-risk-training` (run `train-68da7f7-v2`, mẫu 5% booking, `distributed=False`) đã chạy thành công đủ 4 bước (`Succeeded`), lưu phiên bản tập train vào bảng Iceberg `ml.train_cancel_risk` và ghi nhận model/metric lên MLflow. Trước đó, pipeline cũng đã chạy kiểm chứng qua `ml/run_steps.py` (Job `train-cancel-risk`) và xử lý lỗi `LABEL_SQL` dùng `%` (đổi sang `mod(booking_id, 100)` cho psycopg 3).

![Kubeflow Pipelines UI: run train-68da7f7-v2 hoàn thành 4 step](../images/edai-2/kfp-pipeline-run.png)

![Job train-cancel-risk hoàn thành 4 step trên GKE và bảng Iceberg ml.train_cancel_risk trong Postgres](../images/edai-2/ml-run-steps.png)

<a id="edai-2-14"></a>
## Theo dõi thí nghiệm, model registry và versioning dữ liệu với MLflow

Trên cluster GKE (`hotel-booking-edai2`, dữ liệu Gold khôi phục giai đoạn `2025-01-01` → `2025-01-13`), MLflow 3.6.0 (`k8s/mlflow.yaml`, image `docker/mlflow.Dockerfile`) được cài đặt để lưu metadata trên Postgres (`mlflow`) và artifact trên MinIO (`--serve-artifacts`). Bước `evaluate_and_register` tự động ghi nhận:
- Tham số XGBoost và `train_snapshot_id` trỏ tới snapshot Iceberg của tập train (`ml.train_cancel_risk`), cho phép tái lập đúng tập dữ liệu đã train bằng time travel (`data_version.load_training_set`).
- Dataset `train` gắn vào run, `feature_importance.json` và `reference_lead_days.npy` phục vụ theo dõi drift.
- Đăng ký model `cancel-risk` version 1 kèm tag `release = latest`.

| Metric (tập validation) | Giá trị | Cổng promote |
|---|---|---|
| `val_auc` | 0,709 | ≥ 0,60: đạt |
| `val_calib_gap` | 0,068 | ≤ 0,03: **không đạt** |
| `val_brier` | 0,025 | ≤ Brier bản production (chưa có, mặc định 1): đạt |

Model chưa đạt cổng `val_calib_gap` nên không được gắn alias `production` (đúng thiết kế tự động chặn model kém chất lượng). Nguyên nhân lệch calibration là dữ liệu khôi phục 13 ngày đầu năm 2025 chưa đủ nhãn huỷ muộn.

![MLflow: run và dataset train](../images/edai-2/mlflow-runs.png)

![MLflow: metric của run](../images/edai-2/mlflow-run.png)

![MLflow: train_snapshot_id](../images/edai-2/mlflow-run-params.png)

![MLflow: model cancel-risk version 1, tag release=latest](../images/edai-2/mlflow-model.png)

