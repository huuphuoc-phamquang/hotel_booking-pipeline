# Docker & Docker Compose

Các thành phần của data platform được đóng gói thành image và tối ưu kích thước.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-1-3"></a>
## Có sử dụng Docker & Docker Compose

**Rubric:** edai-1 · dòng 3 · 2 điểm · nhóm *Engineering Fundamentals* › *Docker & Docker Compose*

**Cần nộp (cả nhóm):** Document cách optimizer Docker image, và kích thước sau khi optimize so với cái gốc thay đổi như nào

**Cách làm:** [Đã có] `docker-compose` khởi chạy MinIO, Kafka, generator và replayer. [Cần làm] bổ sung Spark, Flink, Airflow, Postgres, DataHub vào compose; chụp `docker compose ps` với mọi service ở trạng thái healthy, đưa vào `docs/edai-1/docker.md`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="edai-1-4"></a>
## Optimize Dockerfile

**Rubric:** edai-1 · dòng 4 · 3 điểm · nhóm *Engineering Fundamentals* › *Docker & Docker Compose*

> Optimize Dockerfile (ví dụ multistage build)

**Cách làm:** [Đã có] `docker/Dockerfile` dùng multistage (builder và runtime trên `python:3.12-slim`), kèm `docker/Dockerfile.single` một stage để so sánh, `.dockerignore` và `requirements.txt` ghim version. Đo cục bộ bằng `docker images`: bản một stage nặng 2,09GB, bản multistage 834MB. [Cần làm] ghi bảng so sánh vào `docs/edai-1/docker.md`.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
