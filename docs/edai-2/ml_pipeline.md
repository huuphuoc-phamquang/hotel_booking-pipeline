# ML pipeline

Notebook, Kubeflow pipeline, training phân tán, MLflow và versioning dữ liệu train.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-13"></a>
## Build 1 training pipeline với ít nhất 4 steps: load data từ offline feature store, data…

**Rubric:** edai-2 · dòng 13 · 2 điểm · nhóm *ML Pipelines* › *Training Pipelines*

> Build 1 training pipeline (sử dụng Kubeflow Pipelines) với ít nhất 4 steps: load data từ offline feature store, data split, model training, model evaluation

**Cần nộp (cả nhóm):** Document show ảnh pipeline đã chạy thành công trên KF Pipelines + link tới code pipeline

**Cách làm:** [Đã có] Pipeline KFP 4 step cho cancel-risk. Dữ liệu lấy theo cửa sổ [`since`, `until`): v1 dùng [2025-01-01, 2025-06-01), v2 dùng dữ liệu sau mốc drift 2025-06-01 (retrain bằng tay khi nhãn đã chín); lấy mẫu `sample_pct` theo `booking_id`. Nhãn đến từ view `gold.labels_cancel`, chỉ gồm booking đã chín nhãn. Input có `loyalty_tier` và `has_customer_history`. DSN warehouse lấy từ Secret `ml-warehouse`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-14"></a>
## Lưu model, data và các metadata liên quan khác ở mỗi training run lên MLFlow, tự động gắn…

**Rubric:** edai-2 · dòng 14 · 2 điểm · nhóm *ML Pipelines* › *Training Pipelines*

> Lưu model, data và các metadata liên quan khác ở mỗi training run lên MLFlow (cho versioning), tự động gắn tag cho model là `latest` hoặc `production` để tự động hoá deploy.

**Cần nộp (cả nhóm):** Document show ảnh model đã được version và lưu trữ lại + Data tương ứng cũng được version

**Cách làm:** [Đã có] Ghi model, dữ liệu và tham số lên MLflow, gắn tag `release=latest`. Alias `production` chỉ được gán khi qua cổng promote: AUC ≥ 0,60 (sàn chặn model hỏng, thấp hơn trần đo bằng `generator/profile_data`), lệch calibration ≤ 0,03 và không kém bản production khi chấm trên cùng tập validation. Không dùng `scale_pos_weight` vì tham số này làm lệch xác suất.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
