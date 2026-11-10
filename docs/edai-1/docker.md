# Docker & Docker Compose

Đóng gói các thành phần data platform và tối ưu image.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-3"></a>
## Có sử dụng Docker & Docker Compose

**Rubric:** edai-1 · dòng 3 · 2 điểm · nhóm *Engineering Fundamentals* › *Docker & Docker Compose*

**Cần nộp (cả nhóm):** Document cách optimizer Docker image, và kích thước sau khi optimize so với cái gốc thay đổi như nào

**Cách làm:** [Đã có] docker-compose chạy MinIO, Kafka, generator, replayer. [Cần làm] thêm Spark, Flink, Airflow, Postgres, DataHub vào compose; chụp `docker compose ps` all healthy trong docs/Docker.md.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-4"></a>
## Optimize Dockerfile

**Rubric:** edai-1 · dòng 4 · 3 điểm · nhóm *Engineering Fundamentals* › *Docker & Docker Compose*

> Optimize Dockerfile (ví dụ multistage build)

**Cách làm:** [Đã có] Dockerfile multistage (builder + runtime). [Cần làm] build thêm bản 1-stage để so; bảng `docker images` trước/sau; thêm .dockerignore, ghim version requirements.txt.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
