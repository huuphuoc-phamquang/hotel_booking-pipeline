# ML inference service

Model được phục vụ bằng KServe theo mô hình model-inside-image.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-15"></a>
## Sử dụng KServe để serve model vừa train ở bên trên, dùng model-inside-image pattern

**Rubric:** edai-2 · dòng 15 · 2 điểm · nhóm *ML Inference Service để cái Agent bên dưới có thể gọi tới* › *ML Inference Service*

**Cần nộp (cả nhóm):** Document show có pod KServe + link tới kserve YAML file + show ảnh đã gọi thử KServe thành công

**Cách làm:** [Đã có] `kserve-cancel-risk.yaml` theo mô hình model-inside-image. [Cần làm] chụp pod và một lần gọi V1 predict.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
