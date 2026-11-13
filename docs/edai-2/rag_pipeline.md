# RAG data pipeline

Tài liệu chính sách -> chunk -> embedding -> Feast, kèm governance.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-9"></a>
## Build data pipeline với ít nhất các step sau: kéo dữ liệu từ text => chia chunk => lưu…

**Rubric:** edai-2 · dòng 9 · 2 điểm · nhóm *RAG* › *RAG Data Pipeline*

> Build data pipeline (ví dụ với Airflow) với ít nhất các step sau: kéo dữ liệu từ text => chia chunk => lưu embedding vector cho các chunk vào feature store thông qua Feast

**Cần nộp (cả nhóm):** Document show ảnh pipeline đã chạy thành công trên Airflow, và lineage thể hiện trên DataHub + link tới code pipeline

**Cách làm:** [Đã có] rag_pipeline.py: chunk + bge-m3 -> Feast policy_chunks (tài liệu chính sách huỷ / hoàn tiền). [Cần sửa] bge-m3 ~2,2GB vượt limit 1Gi. Chụp Airflow run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-10"></a>
## Đảm bảo data governance cho pipeline

**Rubric:** edai-2 · dòng 10 · 2 điểm · nhóm *RAG* › *RAG Data Pipeline*

> Đảm bảo data governance cho pipeline (tương tự mini-coursework)

**Cách làm:** [Thiết kế] inlets/outlets -> DataHub lineage docs/policies -> policy_chunks; validate số chunk > 0, chunk_id unique, embedding đúng 1024 chiều; ghi version tài liệu + model embedding. [Cần làm] chụp lineage + tab Validation.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
