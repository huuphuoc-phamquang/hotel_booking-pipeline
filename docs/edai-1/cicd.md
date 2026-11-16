# CI/CD cho DP1–DP3

Jenkins kiểm DAG và bộ Great Expectations, build image cho Spark job rồi đồng bộ DAG lên Airflow. Cấu hình
Jenkins dùng chung nằm ở [edai-2/cicd.md](../edai-2/cicd.md).

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="final-30"></a>
## DP 1

**Rubric:** final · dòng 30 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

> DP 1 (xem ở sheet mini-coursework)

**Cần nộp (cả nhóm):** Capture màn hình từng CI/CD pipeline đã run thành công

**Cách làm:** [Đã có] `ci/Jenkinsfile.data` test generator, Great Expectations, Spark, SQL và DAG integrity; build image generator, Spark, Flink; chạy e2e stream; cuối cùng deploy DAG (`dp1_ingest_bronze` cùng các DAG khác). [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-31"></a>
## DP 2

**Rubric:** final · dòng 31 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

> DP 2 (xem ở sheet mini-coursework)

**Cách làm:** [Đã có] Với `dp2_bronze_to_gold`, `ci/Jenkinsfile.data` test Spark (pyspark) và SQL DP2 trên Postgres thật, build image Spark, rồi deploy DAG cùng thư mục `sql/`. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-32"></a>
## DP 3

**Rubric:** final · dòng 32 · 2 điểm · nhóm *CI/CD* › *CI/CD cho pipelines*

> DP 3 (xem ở sheet mini-coursework)

**Cách làm:** [Đã có] Với `dp3_offline_features`, `ci/Jenkinsfile.data` test SQL DP3 và các kiểm tra validate trên Postgres thật, rồi deploy DAG cùng `sql/dp3_features.sql`. [Cần làm] chụp lần chạy.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
