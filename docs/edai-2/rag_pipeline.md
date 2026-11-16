# RAG data pipeline

Tài liệu chính sách được chia chunk, embed rồi lưu vào Feast, có lineage và kiểm tra dữ liệu.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-9"></a>
## Build data pipeline với ít nhất các step sau: kéo dữ liệu từ text => chia chunk => lưu…

**Rubric:** edai-2 · dòng 9 · 2 điểm · nhóm *RAG* › *RAG Data Pipeline*

> Build data pipeline (ví dụ với Airflow) với ít nhất các step sau: kéo dữ liệu từ text => chia chunk => lưu embedding vector cho các chunk vào feature store thông qua Feast

**Cần nộp (cả nhóm):** Document show ảnh pipeline đã chạy thành công trên Airflow, và lineage thể hiện trên DataHub + link tới code pipeline

**Cách làm:** [Đã có] `rag_pipeline.py` chia chunk, embed bằng bge-m3 rồi ghi vào Feast `policy_chunks`; tài liệu chính sách nằm ở `policies/*.md`. Task embed chạy trên pod riêng 4–6Gi (`executor_config`), chart booking-mcp nâng limit lên 4Gi. [Cần làm] chụp lần chạy trên Airflow.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-2-10"></a>
## Đảm bảo data governance cho pipeline

**Rubric:** edai-2 · dòng 10 · 2 điểm · nhóm *RAG* › *RAG Data Pipeline*

> Đảm bảo data governance cho pipeline (tương tự mini-coursework)

**Cách làm:** [Đã có] Inlets, outlets tạo lineage trên DataHub từ `docs/policies` tới `policy_chunks`. Pipeline kiểm số chunk > 0, `chunk_id` không trùng và embedding đúng 1024 chiều; mỗi chunk ghi `doc_sha256` (version tài liệu) và `embed_model`. [Cần làm] chụp lineage và tab Validation.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
