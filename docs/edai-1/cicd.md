# CI/CD cho DP1–DP3

Jenkins: test DAG + GX suite, build image Spark job, sync DAG lên Airflow. Cấu hình Jenkins dùng chung: [edai-2/cicd.md](../edai-2/cicd.md).

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="final-30"></a>
## DP 1

**Rubric:** final · dòng 30 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

> DP 1 (xem ở sheet mini-coursework)

**Cần nộp (cả nhóm):** Capture màn hình từng CI/CD pipeline đã run thành công

**Cách làm:** [Đã có] ci/Jenkinsfile.data: test generator + GX + Spark + SQL + DAG integrity -> build image generator/Spark/Flink -> e2e stream -> deploy DAG (dp1_ingest_bronze cùng các DAG khác). [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-31"></a>
## DP 2

**Rubric:** final · dòng 31 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

> DP 2 (xem ở sheet mini-coursework)

**Cách làm:** [Đã có] ci/Jenkinsfile.data cho dp2_bronze_to_gold: test Spark (pyspark) + SQL DP2 trên Postgres thật -> build image Spark -> deploy DAG + sql/. [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-32"></a>
## DP 3

**Rubric:** final · dòng 32 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

> DP 3 (xem ở sheet mini-coursework)

**Cách làm:** [Đã có] ci/Jenkinsfile.data cho dp3_offline_features: test SQL DP3 + check validate trên Postgres thật -> deploy DAG + sql/dp3_features.sql. [Cần làm] chụp run.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
