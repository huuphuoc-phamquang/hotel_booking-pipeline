# ML pipeline

Notebook, Kubeflow pipeline, training phân tán, MLflow, version dữ liệu.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-13"></a>
## Build 1 training pipeline với ít nhất 4 steps: load data từ offline feature store, data…

**Rubric:** edai-2 · dòng 13 · 2 điểm · nhóm *ML Pipelines* › *Training Pipelines*

> Build 1 training pipeline (sử dụng Kubeflow Pipelines) với ít nhất 4 steps: load data từ offline feature store, data split, model training, model evaluation

**Cần nộp (cả nhóm):** Document show ảnh pipeline đã chạy thành công trên KF Pipelines + link tới code pipeline

**Cách làm:** [Đã có] cancel-risk KFP 4 step; dữ liệu theo cửa sổ [since, until) (v1: tháng 1-6/2025, v2: dữ liệu gần đây sau drift); nhãn = left join cancellations, chỉ booking có checkin < until; input có loyalty_tier và has_customer_history. [Cần sửa] connection string lấy từ Secret.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-14"></a>
## Lưu model, data và các metadata liên quan khác ở mỗi training run lên MLFlow, tự động gắn…

**Rubric:** edai-2 · dòng 14 · 2 điểm · nhóm *ML Pipelines* › *Training Pipelines*

> Lưu model, data và các metadata liên quan khác ở mỗi training run lên MLFlow (cho versioning), tự động gắn tag cho model là `latest` hoặc `production` để tự động hoá deploy.

**Cần nộp (cả nhóm):** Document show ảnh model đã được version và lưu trữ lại + Data tương ứng cũng được version

**Cách làm:** [Đã có] log model/data/params, tag release=latest, alias production qua cổng promote: AUC ≥ 0,60 (sàn chặn model hỏng, dưới trần đo bằng generator/profile_data), lệch calibration ≤ 0,03, không kém bản production chấm trên cùng validation; bỏ scale_pos_weight (làm lệch xác suất).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-23"></a>
### Jupyter notebook để kéo dữ liệu từ offline store để tạo ra model.

**Rubric:** final · dòng 23 · 2 điểm · nhóm *ML* › *Jupyter notebook to demonstrate basic understanding of ML/DL*

> Jupyter notebook để kéo dữ liệu từ offline store (thông qua Feast) để tạo ra model (dùng ML/DL). Jupyter notebook cần đảm bảo ít nhất các step sau: + Load data từ offline store thông qua Feast (nhớ merge với bảng label đã generate ở bước Improve the Data Generator nhé cả nhà!) + Chia data thành trainining set và validation set + Train model trên training dataset (không cần độ chính xác cao, tuy nhiên cần phù hợp task, ví dụ bài regression lại dùng model classification!) + Đánh giá trên validation dataset + Save model (ví dụ lưu ra dạng .joblib)

**Cần nộp (cả nhóm):** Document các step chính đã làm trong Jupyter notebook

**Cách làm:** [Thiết kế] notebooks/cancel_risk.ipynb: Feast get_historical_features + left join cancellations -> split theo thời gian -> XGBoost -> AUC, calibration, Brier so với xác suất huỷ thật của generator.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-24"></a>
### Chuyển đổi code từ Jupyter notebook thành training pipeline với số lượng step giống ở…

**Rubric:** final · dòng 24 · 2 điểm · nhóm *ML Pipelines* › *Training Pipeline*

> Chuyển đổi code từ Jupyter notebook thành training pipeline với số lượng step giống ở phần notebook bên trên (sử dụng Kubeflow pipeline, cái này có thể deploy riêng mà không cần deploy cả Kubeflow).

**Cần nộp (cả nhóm):** Capture training pipeline đã run thành công + Capture màn hình thể hiện có sử dụng distributed training

**Cách làm:** [Đã có] ml/training_pipeline.py 4 step (load_from_feast, split_by_time, train, evaluate_and_register). [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-25"></a>
### Trong training pipeline, ở step train, thay bằng distributed training

**Rubric:** final · dòng 25 · 2 điểm · nhóm *ML Pipelines* › *Training Pipeline*

> Trong training pipeline, ở step train, thay bằng distributed training, ví dụ nếu mọi người dùng model XGBoost thì có thể coi tutorial này.

**Cách làm:** [Thiết kế] step train tạo Kubeflow Trainer TrainJob runtime XGBoost 2 worker (xgboost.collective) theo tutorial; evaluate đọc model từ artifact. [Cần làm] chụp 2 pod worker.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-26"></a>
### Khi training pipeline hoàn tất, thông tin của MODEL cần được lưu trữ lại ở Model Registry

**Rubric:** final · dòng 26 · 2 điểm · nhóm *Versioning* › *Model Versioning*

> Khi training pipeline hoàn tất, thông tin của MODEL (weight, hyperparam) cần được lưu trữ lại ở Model Registry (qua MLFlow)

**Cần nộp (cả nhóm):** Model đã được version và lưu trữ lại + Data tương ứng cũng được version theo cơ chế incremental

**Cách làm:** [Đã có] MLflow registry, tag release=latest, alias production qua cổng promote: AUC ≥ 0,60 (sàn chặn model hỏng, dưới trần đo bằng generator/profile_data), lệch calibration ≤ 0,03, không kém bản production chấm trên cùng validation; bỏ scale_pos_weight (làm lệch xác suất).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-27"></a>
### Mỗi lần kéo dữ liệu từ Feast về để training, cần version lại DATA theo cơ chế incremental

**Rubric:** final · dòng 27 · 2 điểm · nhóm *Versioning* › *Data Versioning*

> Mỗi lần kéo dữ liệu từ Feast về để training, cần version lại DATA theo cơ chế incremental (ví dụ lần train thứ 2 data chỉ có 1 chút thay đổi thì chỉ lưu trữ lại phần thay đổi này thôi, tránh việc lưu full data của cả lần 1 và lần 2)

**Cách làm:** [Thiết kế] tập train ghi Iceberg ml.train_cancel_risk bằng MERGE INTO ON booking_id (chỉ thêm file cho dòng mới/đổi); MLflow ghi snapshot_id, tái lập bằng VERSION AS OF. [Cần làm] chụp snapshot + số file thêm.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
