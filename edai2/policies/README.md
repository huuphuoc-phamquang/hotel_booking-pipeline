# Tài liệu chính sách cho RAG

Chính sách nội bộ (hư cấu) của hệ thống đặt phòng trong đồ án. DAG `rag_data_pipeline` đọc các file `.md` ở
MinIO `s3://docs/policies/`: chép thư mục này lên bằng `mc cp --recursive policies/ minio/docs/policies/`.
Bộ dữ liệu fine-tune (`llm_platform/finetune/build_dataset.py`) cũng lấy dữ kiện từ đây, nên sửa chính sách thì
chạy lại cả RAG lẫn fine-tune.
