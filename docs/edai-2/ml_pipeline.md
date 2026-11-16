# ML pipeline

Notebook, Kubeflow pipeline, training phân tán, MLflow và versioning dữ liệu train.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-13"></a>
## Build 1 training pipeline với ít nhất 4 steps: load data từ offline feature store, data…

**Rubric:** edai-2 · dòng 13 · 2 điểm · nhóm *ML Pipelines* › *Training Pipelines*

> Build 1 training pipeline (sử dụng Kubeflow Pipelines) với ít nhất 4 steps: load data từ offline feature store, data split, model training, model evaluation

**Cần nộp (cả nhóm):** Document show ảnh pipeline đã chạy thành công trên KF Pipelines + link tới code pipeline

**Cách làm:** [Đã có] Pipeline KFP 4 step cho cancel-risk. Dữ liệu lấy theo cửa sổ [`since`, `until`): v1 dùng [2025-01-01, 2025-06-01), v2 bắt đầu từ mốc phát hiện drift; lấy mẫu `sample_pct` theo `booking_id`. Nhãn đến từ view `gold.labels_cancel`, chỉ gồm booking đã chín nhãn. Input có `loyalty_tier` và `has_customer_history`. DSN warehouse lấy từ Secret `ml-warehouse`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-14"></a>
## Lưu model, data và các metadata liên quan khác ở mỗi training run lên MLFlow, tự động gắn…

**Rubric:** edai-2 · dòng 14 · 2 điểm · nhóm *ML Pipelines* › *Training Pipelines*

> Lưu model, data và các metadata liên quan khác ở mỗi training run lên MLFlow (cho versioning), tự động gắn tag cho model là `latest` hoặc `production` để tự động hoá deploy.

**Cần nộp (cả nhóm):** Document show ảnh model đã được version và lưu trữ lại + Data tương ứng cũng được version

**Cách làm:** [Đã có] Ghi model, dữ liệu và tham số lên MLflow, gắn tag `release=latest`. Alias `production` chỉ được gán khi qua cổng promote: AUC ≥ 0,60 (sàn chặn model hỏng, thấp hơn trần đo bằng `generator/profile_data`), lệch calibration ≤ 0,03 và không kém bản production khi chấm trên cùng tập validation. Không dùng `scale_pos_weight` vì tham số này làm lệch xác suất.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

## Bổ sung final-coursework

<a id="final-23"></a>
### Jupyter notebook để kéo dữ liệu từ offline store để tạo ra model.

**Rubric:** final · dòng 23 · 2 điểm · nhóm *ML* › *Jupyter notebook to demonstrate basic understanding of ML/DL*

> Jupyter notebook để kéo dữ liệu từ offline store (thông qua Feast) để tạo ra model (dùng ML/DL). Jupyter notebook cần đảm bảo ít nhất các step sau: + Load data từ offline store thông qua Feast (nhớ merge với bảng label đã generate ở bước Improve the Data Generator nhé cả nhà!) + Chia data thành trainining set và validation set + Train model trên training dataset (không cần độ chính xác cao, tuy nhiên cần phù hợp task, ví dụ bài regression lại dùng model classification!) + Đánh giá trên validation dataset + Save model (ví dụ lưu ra dạng .joblib)

**Cần nộp (cả nhóm):** Document các step chính đã làm trong Jupyter notebook

**Cách làm:** [Đã có] `notebooks/cancel_risk.ipynb` chạy cục bộ và có output. Notebook lấy dữ liệu từ generator, chia train và validation theo thời gian, train XGBoost, so AUC với trần của nhãn, vẽ reliability theo decile so với p thật, tính Brier so với p thật và sai số số phòng bán vượt K (`overbooking.limit`). Sau drift 2025-06-01, độ lệch calibration của v1 là 0,127; retrain trên cửa sổ sau drift kéo xuống 0,0008, sai số K giảm từ 1,62 xuống 0,36. Notebook dùng nhãn generator ngay, còn pipeline thật phải chờ nhãn chín (`drift_stats.retrain_window`).

**Kết quả:** notebook `notebooks/cancel_risk.ipynb` đã chạy cục bộ và có output (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="final-24"></a>
### Chuyển đổi code từ Jupyter notebook thành training pipeline với số lượng step giống ở…

**Rubric:** final · dòng 24 · 2 điểm · nhóm *ML Pipelines* › *Training Pipeline*

> Chuyển đổi code từ Jupyter notebook thành training pipeline với số lượng step giống ở phần notebook bên trên (sử dụng Kubeflow pipeline, cái này có thể deploy riêng mà không cần deploy cả Kubeflow).

**Cần nộp (cả nhóm):** Capture training pipeline đã run thành công + Capture màn hình thể hiện có sử dụng distributed training

**Cách làm:** [Đã có] `ml/training_pipeline.py` gồm 4 step: `load_from_feast`, `split_by_time`, `train`, `evaluate_and_register`. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-25"></a>
### Trong training pipeline, ở step train, thay bằng distributed training

**Rubric:** final · dòng 25 · 2 điểm · nhóm *ML Pipelines* › *Training Pipeline*

> Trong training pipeline, ở step train, thay bằng distributed training, ví dụ nếu mọi người dùng model XGBoost thì có thể coi tutorial này.

**Cách làm:** [Đã có] `ml/train_xgb_dist.py` dùng `xgboost.collective`, mỗi worker giữ một phần dữ liệu. Component `train_distributed` tạo Kubeflow Trainer TrainJob runtime `xgboost-distributed` với 2 node (`distributed=True` mặc định, `dsl.If`/`dsl.OneOf` chọn giữa bản này và bản một node). `tests/test_train_xgb_dist.py` chạy 2 worker với RabitTracker cục bộ; AUC lệch dưới 0,01 so với bản một node. [Cần làm] chụp 2 pod worker.

**Kết quả:** các test `edai2/tests/test_train_xgb_dist.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.

<a id="final-26"></a>
### Khi training pipeline hoàn tất, thông tin của MODEL cần được lưu trữ lại ở Model Registry

**Rubric:** final · dòng 26 · 2 điểm · nhóm *Versioning* › *Model Versioning*

> Khi training pipeline hoàn tất, thông tin của MODEL (weight, hyperparam) cần được lưu trữ lại ở Model Registry (qua MLFlow)

**Cần nộp (cả nhóm):** Model đã được version và lưu trữ lại + Data tương ứng cũng được version theo cơ chế incremental

**Cách làm:** [Đã có] MLflow registry gắn tag `release=latest`. Alias `production` chỉ được gán khi qua cổng promote: AUC ≥ 0,60 (sàn chặn model hỏng, thấp hơn trần đo bằng `generator/profile_data`), lệch calibration ≤ 0,03 và không kém bản production khi chấm trên cùng tập validation. Không dùng `scale_pos_weight` vì tham số này làm lệch xác suất.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-27"></a>
### Mỗi lần kéo dữ liệu từ Feast về để training, cần version lại DATA theo cơ chế incremental

**Rubric:** final · dòng 27 · 2 điểm · nhóm *Versioning* › *Data Versioning*

> Mỗi lần kéo dữ liệu từ Feast về để training, cần version lại DATA theo cơ chế incremental (ví dụ lần train thứ 2 data chỉ có 1 chút thay đổi thì chỉ lưu trữ lại phần thay đổi này thôi, tránh việc lưu full data của cả lần 1 và lần 2)

**Cách làm:** [Đã có] `ml/data_version.py` upsert tập train vào bảng Iceberg `ml.train_cancel_risk` theo `booking_id` (pyiceberg); `load_from_feast` trả `snapshot_id` và MLflow ghi `train_snapshot_id`. `tests/test_data_version.py` xác nhận: chỉ phần thay đổi được ghi, dữ liệu giống hệt không tạo snapshot mới, time travel trả đúng tập cũ. [Cần làm] chụp snapshot trên cluster.

**Kết quả:** các test `edai2/tests/test_data_version.py` chạy cục bộ và đạt (2026-11-16). Chưa có ảnh chụp trên cluster.
