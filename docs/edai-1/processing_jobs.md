# Processing jobs: Spark & Flink

Từ baseline tới bản tối ưu; đo bằng Spark UI và Flink UI.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-1-11"></a>
## Baseline · Spark job to handle offline data problems

**Rubric:** edai-1 · dòng 11 · 2 điểm · nhóm *Processing Jobs* › *Spark job to handle offline data problems*

> Baseline (without optimization)

**Cần nộp (cả nhóm):** Document giải thích từng step optimize từ baseline như thế nào, dùng Spark UI như thế nào (với screenshots để thấy rõ vấn đề), và đã tích hợp vào Airflow pipeline ra sao

**Cách làm:** [Đã có] silver_quotes baseline: AQE tắt + broadcast tắt (không tối ưu); build_spark không còn ép autoBroadcastJoinThreshold=-1 nên join hotels (~1-2 MB) tự broadcast. tests/test_silver_quotes.py chạy pyspark cục bộ: 4 chế độ cho đúng cùng kết quả. [Cần làm] chạy trên >= 100GB, chụp Spark UI (straggler task), ghi thời gian vào docs/edai-1/processing_jobs.md.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-12"></a>
## Handle skew with explanation

**Rubric:** edai-1 · dòng 12 · 3 điểm · nhóm *Processing Jobs* › *Spark job to handle offline data problems*

> Handle skew with explanation (Ví dụ: Do data bị skew như thế này, tôi thấy từ Spark UI có vấn đề như này, tôi sẽ có các phương pháp thử nghiệm như thế này, và sau khi thử nghiệm thì nó tăng ntn so với baseline)

**Cách làm:** [Đã có] silver_quotes 4 cấu hình trên stg_quotes ⋈ raw_inventory theo (hotel_id, room_type, stay_date): baseline / aqe (mặc định Spark) / aqe_tuned (skewJoin factor 2, ngưỡng 64MB) / salt (salting 200 ô nóng nhất, hot_keys + salted_join tổng quát theo khoá). [Cần làm] chạy trên >= 100GB, ghi thời gian, max/median task time, shuffle read; chỉ salting khi aqe_tuned còn straggler.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-13"></a>
## Handle schema evolution with explanation

**Rubric:** edai-1 · dòng 13 · 3 điểm · nhóm *Processing Jobs* › *Spark job to handle offline data problems*

**Cách làm:** [Đã có] mergeSchema + coalesce room_category; tests/test_silver_bookings.py (pyspark cục bộ, Bronze qua mốc 2025-07-01): không mất dòng nào, room_category không null, channel null đúng ở partition v1. [Cần làm] chụp kết quả trên dữ liệu thật.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-14"></a>
## Handle other offline data problem with explanation

**Rubric:** edai-1 · dòng 14 · 3 điểm · nhóm *Processing Jobs* › *Spark job to handle offline data problems*

**Cách làm:** [Đã có] dedup theo idempotency_key (row_number theo created_at); tests/test_silver_bookings.py: sau dedup mỗi idempotency_key 1 dòng và status khớp kết cục generator. [Cần làm] số dòng trước/sau trên dữ liệu thật.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-15"></a>
## Spark job được tích hợp vào các data pipeline

**Rubric:** edai-1 · dòng 15 · 2 điểm · nhóm *Processing Jobs* › *Spark job to handle offline data problems*

**Cách làm:** [Đã có] DAG dp2_bronze_to_gold gọi SparkSubmitOperator silver_bookings.py chế độ incr (chỉ đọc partition dt=ds, MERGE vào Iceberg; tests/test_silver_bookings.py so với dựng lại cả bảng) rồi stage_gold.py (Silver -> staging Gold qua JDBC); image Spark có Iceberg + s3a + JDBC (k8s/spark.Dockerfile). [Cần làm] chụp Airflow graph + log Spark.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-16"></a>
## Baseline · Flink job to handle streaming data problems

**Rubric:** edai-1 · dòng 16 · 2 điểm · nhóm *Processing Jobs* › *Flink job to handle streaming data problems (later in final coursework, we will merge this streaming pipeline into the feature store)*

> Baseline (without optimization)

**Cần nộp (cả nhóm):** Document giải thích từng step optimize từ baseline như thế nào, dùng Flink UI như thế nào (nhớ show hình ảnh để thấy rõ các vấn đề, và giải thích vấn đề)

**Cách làm:** [Đã có] cờ BASELINE=True (watermark 0s, không dedup). [Cần làm] chụp Flink UI: số event late bị bỏ, kết quả window sai.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-17"></a>
## Handle late arrival with explanation

**Rubric:** edai-1 · dòng 17 · 3 điểm · nhóm *Processing Jobs* › *Flink job to handle streaming data problems (later in final coursework, we will merge this streaming pipeline into the feature store)*

**Cách làm:** [Đã có] watermark 10 phút + allowed lateness 5 phút + side output ở nhánh đối soát tumbling 1 phút (cửa sổ trượt 1 giờ chỉ đẩy event ra side output khi trễ > 1h15'), ghi gold.stream_late_bookings; e2e trên Docker xác nhận đếm + side output = tổng từng phút. Trên PyFlink 1.20 gán timestamp sau source, không with_idleness (đo được: idleness làm watermark đứng). [Cần làm] bảng số event vào side output baseline vs tối ưu theo từng nguồn trễ; giải thích chọn 10 phút.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-18"></a>
## Handle other streaming problem with explanation

**Rubric:** edai-1 · dòng 18 · 3 điểm · nhóm *Processing Jobs* › *Flink job to handle streaming data problems (later in final coursework, we will merge this streaming pipeline into the feature store)*

**Cách làm:** [Đã có] DedupByEventId (state TTL 1 giờ). [Cần làm] đếm event trùng trước/sau, chụp state size trên Flink UI.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-1-19"></a>
## Window processing

**Rubric:** edai-1 · dòng 19 · 2 điểm · nhóm *Processing Jobs* › *Flink job to handle streaming data problems (later in final coursework, we will merge this streaming pipeline into the feature store)*

**Cần nộp (cả nhóm):** Document show đoạn code thể hiện khả năng xử lý Window trong Flink, và giải thích đoạn code đó làm gì

**Cách làm:** [Đã có] sliding window 1 giờ trượt 5 phút theo hotel_id (SlidingEventTimeWindows) ra bookings_1h, upsert gold.feat_hotel_realtime; tumbling 1 phút (TumblingEventTimeWindows) ra gold.stream_bookings_1m để đối soát. [Cần làm] trích code + giải thích trong docs/edai-1/processing_jobs.md.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
