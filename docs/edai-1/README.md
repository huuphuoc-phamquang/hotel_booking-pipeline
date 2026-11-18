# Data platform (edai-1)

| Tài liệu | Nội dung |
|---|---|
| [docker.md](docker.md) | Đóng gói data platform thành image và tối ưu kích thước. |
| [data_generator.md](data_generator.md) | Generator tái lập được: lỗi offline, lỗi streaming, data drift và bảng nhãn. |
| [processing_jobs.md](processing_jobs.md) | Spark và Flink job từ baseline tới bản tối ưu, đo bằng Spark UI và Flink UI. |
| [data_storage.md](data_storage.md) | Lakehouse trên Iceberg, data warehouse là tầng Gold trên PostgreSQL. |
| [data_pipeline.md](data_pipeline.md) | Ba pipeline DP1–DP3 trên Airflow, mỗi pipeline gồm ingest và validate. |
| [data_governance.md](data_governance.md) | Lineage và kết quả kiểm tra dữ liệu DP1–DP3 trên DataHub. |
| [schema_design.md](schema_design.md) | Bảng theo zone, dimension SCD2, bảng feature, quan hệ dim–fact và quy ước đặt tên. |
| [novel_ideas.md](novel_ideas.md) | Mỗi ý tưởng gồm vấn đề, cách làm và minh chứng đã chạy. |

## Dòng rubric edai-1

| Dòng | Điểm | Mục | Tài liệu | Trạng thái |
|---|---|---|---|---|
| 3 | 2 | Có sử dụng Docker & Docker Compose | [docker.md](docker.md#edai-1-3) | Đã có |
| 4 | 3 | Optimize Dockerfile | [docker.md](docker.md#edai-1-4) | Đã có |
| 5 | 2 | Simulate skew | [data_generator.md](data_generator.md#edai-1-5) | Đã có |
| 6 | 2 | Simulate schema evolution | [data_generator.md](data_generator.md#edai-1-6) | Đã có |
| 7 | 2 | Simulate another offline data problem | [data_generator.md](data_generator.md#edai-1-7) | Đã có · Thêm cho novelty |
| 8 | 2 | Store data after generating so that we can ingest to Bronze zone later | [data_generator.md](data_generator.md#edai-1-8) | Đã có |
| 9 | 2 | Simulate late arrivals | [data_generator.md](data_generator.md#edai-1-9) | Đã có |
| 10 | 2 | Simulate another streaming data problem | [data_generator.md](data_generator.md#edai-1-10) | Đã có |
| 11 | 2 | Baseline | [processing_jobs.md](processing_jobs.md#edai-1-11) | Đã có · chờ cluster |
| 12 | 3 | Handle skew with explanation | [processing_jobs.md](processing_jobs.md#edai-1-12) | Đã có · chờ cluster |
| 13 | 3 | Handle schema evolution with explanation | [processing_jobs.md](processing_jobs.md#edai-1-13) | Đã có |
| 14 | 3 | Handle other offline data problem with explanation | [processing_jobs.md](processing_jobs.md#edai-1-14) | Đã có |
| 15 | 2 | Spark job được tích hợp vào các data pipeline | [processing_jobs.md](processing_jobs.md#edai-1-15) | Đã có |
| 16 | 2 | Baseline | [processing_jobs.md](processing_jobs.md#edai-1-16) | Đã có |
| 17 | 3 | Handle late arrival with explanation | [processing_jobs.md](processing_jobs.md#edai-1-17) | Đã có |
| 18 | 3 | Handle other streaming problem with explanation | [processing_jobs.md](processing_jobs.md#edai-1-18) | Đã có |
| 19 | 2 | Window processing | [processing_jobs.md](processing_jobs.md#edai-1-19) | Đã có |
| 20 | 3 | Lakehouse | [data_storage.md](data_storage.md#edai-1-20) | Đã có · Thiết kế · Cần làm |
| 21 | 3 | Datawarehouse | [data_storage.md](data_storage.md#edai-1-21) | Đã có · Cần làm |
| 22 | 2 | Ingest stage | [data_pipeline.md](data_pipeline.md#edai-1-22) | Đã có |
| 23 | 2 | Validate stage | [data_pipeline.md](data_pipeline.md#edai-1-23) | Đã có |
| 24 | 2 | Ingest stage | [data_pipeline.md](data_pipeline.md#edai-1-24) | Đã có |
| 25 | 2 | Validate stage | [data_pipeline.md](data_pipeline.md#edai-1-25) | Đã có |
| 26 | 2 | Ingest stage | [data_pipeline.md](data_pipeline.md#edai-1-26) | Đã có |
| 27 | 2 | Validate stage | [data_pipeline.md](data_pipeline.md#edai-1-27) | Đã có |
| 28 | 2 | Lineage between the pipeline and tables | [data_governance.md](data_governance.md#edai-1-28) | Đã có |
| 29 | 2 | Data validation | [data_governance.md](data_governance.md#edai-1-29) | Đã có |
| 30 | 2 | Lineage between the pipeline and tables | [data_governance.md](data_governance.md#edai-1-30) | Đã có |
| 31 | 2 | Data validation | [data_governance.md](data_governance.md#edai-1-31) | Đã có |
| 32 | 2 | Lineage between the pipeline and tables | [data_governance.md](data_governance.md#edai-1-32) | Đã có |
| 33 | 2 | Data validation | [data_governance.md](data_governance.md#edai-1-33) | Đã có |
| 34 | 2 | Visualize tables on all zones | [schema_design.md](schema_design.md#edai-1-34) | Đã có |
| 35 | 2 | Dim table with SCD 2 | [schema_design.md](schema_design.md#edai-1-35) | Đã có · chờ cluster |
| 36 | 2 | Feature tables with 2 columns event_timestamp and created | [schema_design.md](schema_design.md#edai-1-36) | Đã có |
| 37 | 2 | Relationship between dim & fact tables | [schema_design.md](schema_design.md#edai-1-37) | Đã có |
| 38 | 2 | Naming convention | [schema_design.md](schema_design.md#edai-1-38) | Đã có |
| 39 | 10 | Idea 1 | [novel_ideas.md](novel_ideas.md#edai-1-39) | — |
| 40 | 10 | Idea 2 | [novel_ideas.md](novel_ideas.md#edai-1-40) | — |
