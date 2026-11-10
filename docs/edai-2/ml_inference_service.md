# ML inference service

KServe model-inside-image.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-15"></a>
## Sử dụng KServe để serve model vừa train ở bên trên, dùng model-inside-image pattern

**Rubric:** edai-2 · dòng 15 · 2 điểm · nhóm *ML Inference Service để cái Agent bên dưới có thể gọi tới* › *ML Inference Service*

**Cần nộp (cả nhóm):** Document show có pod KServe + link tới kserve YAML file + show ảnh đã gọi thử KServe thành công

**Cách làm:** [Đã có] kserve-cancel-risk.yaml model-inside-image. [Cần làm] tương tự cho demand-model và cancel-segment; chụp pod + gọi V1 predict.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
