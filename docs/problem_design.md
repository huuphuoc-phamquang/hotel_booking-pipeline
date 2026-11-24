# Thiết kế bài toán

Tài liệu này giải thích bài toán mà toàn bộ hệ thống phục vụ: dự báo xác suất huỷ của từng booking (`cancel-risk`) để
đề xuất số phòng bán vượt (overbooking). Các tài liệu trong `edai-1/` và `edai-2/` mô tả cách triển khai; tài liệu này
mô tả lý do và logic của bài toán.

Số liệu trong tài liệu lấy từ `generator/profile_data` và `notebooks/cancel_risk.ipynb`, đều chạy cục bộ. Phần đã đo lại trên
cluster được ghi trong `edai-1/` và `edai-2/`.

## 1. Bối cảnh nghiệp vụ

Khách sạn bán phòng theo đêm. Một phòng trống trong đêm nào thì mất doanh thu của đêm đó, không bán bù được về sau.

Một phần booking bị huỷ trước ngày nhận phòng. Trong dữ liệu của đồ án, tỉ lệ huỷ trung bình là 32,9% trước drift và
47,4% sau drift. Khách sạn vì vậy đứng trước hai lựa chọn đều có chi phí:

- **Chỉ bán đúng số phòng.** Khi có booking huỷ, phòng bị bỏ trống. Chi phí này gọi là *spoilage*.
- **Bán vượt số phòng.** Nếu số booking huỷ ít hơn số phòng bán vượt, khách đến mà không có phòng. Khách sạn phải
  chuyển khách sang nơi khác và đền bù. Chi phí này gọi là *walk*.

Bán vượt (overbooking) là cách làm phổ biến của ngành để cân bằng hai chi phí trên. Câu hỏi của revenue manager là:
với một khách sạn và một đêm cụ thể, nên bán vượt bao nhiêu phòng?

## 2. Phát biểu bài toán

Bài toán gồm hai tầng, tầng sau dùng kết quả của tầng trước.

| Tầng | Đầu vào | Đầu ra | Thành phần |
|---|---|---|---|
| Dự báo | thuộc tính của một booking, lịch sử của khách và của khách sạn | xác suất huỷ $p_i$ của booking đó | model `cancel-risk` (XGBoost) phục vụ bằng KServe; tool `predict_cancellation` của `booking-mcp` lấy feature từ Feast online rồi gọi KServe |
| Quyết định | các $p_i$ của mọi booking đang giữ phòng cho một `hotel × stay_date`, cùng hai chi phí | số phòng bán vượt $K$ | `mcp_server/overbooking.py`, tool `propose_overbooking` |

Hai điểm cần lưu ý về phạm vi:

- Hệ thống chỉ **đề xuất** $K$. Việc ghi $K$ vào `gold.overbooking_limits` do tool `apply_overbooking` thực hiện và
  phải được revenue manager duyệt (mục 8).
- Xác suất huỷ chỉ được dùng ở dạng **cộng dồn** theo khách sạn và đêm. Hệ thống không dùng xác suất này để đổi giá
  hay đổi điều kiện đặt phòng của từng khách.

## 3. Từ xác suất huỷ tới số phòng bán vượt

### 3.1 Mô hình

Xét một khách sạn và một đêm có $M$ booking đang giữ phòng. Booking thứ $i$ huỷ với xác suất $p_i$. Giả định các
booking huỷ độc lập với nhau. Khi đó số booking huỷ $N$ là tổng của $M$ biến Bernoulli có xác suất khác nhau, tức
tuân theo phân phối Poisson-binomial:

$$N \sim \operatorname{Poisson-binomial}(p_1, \dots, p_M)$$

Hàm `cancel_distribution` tính chính xác $\mathbb{P}(N = n)$ bằng quy hoạch động, không dùng xấp xỉ chuẩn.

Nếu khách sạn bán vượt $K$ phòng thì có hai trường hợp:

- $N < K$: số booking huỷ không đủ bù, khách sạn phải walk $K - N$ khách, mỗi khách tốn $c_{\text{walk}}$.
- $N > K$: còn $N - K$ phòng trống, mỗi phòng tốn $c_{\text{spoil}}$.

### 3.2 Quy tắc chọn K

Hệ thống chọn $K$ lớn nhất thoả:

$$\mathbb{P}(N < K) \le \frac{c_{\text{spoil}}}{c_{\text{spoil}} + c_{\text{walk}}}$$

Quy tắc này có thể hiểu bằng cách xét việc bán thêm phòng vượt thứ $k$:

- Phòng này sinh lợi khi có ít nhất $k$ booking huỷ. Lợi ích là tránh được một phòng trống, trị giá $c_{\text{spoil}}$,
  với xác suất $\mathbb{P}(N \ge k)$.
- Phòng này gây thiệt hại khi có ít hơn $k$ booking huỷ. Thiệt hại là một khách bị walk, trị giá $c_{\text{walk}}$,
  với xác suất $\mathbb{P}(N < k)$.

Bán thêm phòng thứ $k$ có lợi khi $c_{\text{walk}} \cdot \mathbb{P}(N < k) \le c_{\text{spoil}} \cdot \mathbb{P}(N \ge k)$.
Biến đổi bất đẳng thức này cho đúng điều kiện ở trên. Đây là lời giải quen thuộc của bài toán newsvendor trong vận trù học.

Hệ thống đặt mặc định $c_{\text{spoil}} = 1$ và $c_{\text{walk}} = 3$ (biến môi trường `OVERBOOK_C_SPOIL`,
`OVERBOOK_C_WALK`), nên ngưỡng là $1/4 = 0{,}25$. Nói cách khác, hệ thống chấp nhận tối đa 25% khả năng phải walk
ít nhất một khách.

### 3.3 Ví dụ

Một đêm có 5 booking với xác suất huỷ lần lượt 0,1; 0,2; 0,3; 0,4; 0,5. Số booking huỷ kỳ vọng là 1,5. Phân phối
của $N$ tính bằng `cancel_distribution`:

| $n$ | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| $\mathbb{P}(N = n)$ | 0,151 | 0,371 | 0,327 | 0,127 | 0,021 | 0,001 |
| $\mathbb{P}(N < n)$ | 0 | 0,151 | 0,523 | 0,850 | 0,977 | 0,999 |

Với ngưỡng 0,25: $\mathbb{P}(N < 1) = 0{,}151$ đạt, còn $\mathbb{P}(N < 2) = 0{,}523$ vượt ngưỡng. Vậy $K = 1$.
Dù kỳ vọng có 1,5 booking huỷ, hệ thống chỉ đề xuất bán vượt 1 phòng vì walk đắt gấp ba spoilage.

Tỉ lệ chi phí quyết định mức thận trọng. Với 100 booking cùng có $p = 0{,}33$ (kỳ vọng 33 booking huỷ), hàm `limit` cho:

| $c_{\text{spoil}}: c_{\text{walk}}$ | Ngưỡng | $K$ |
|---|---|---|
| 1: 1 | 0,50 | 33 |
| 1: 3 (mặc định) | 0,25 | 30 |
| 1: 10 | 0,09 | 27 |

### 3.4 Kết quả trả về của `propose_overbooking`

Tool lấy điểm mới nhất của từng booking còn giữ phòng trong `gold.booking_risk`, bỏ booking đã huỷ, rồi trả về:

- `bookings`: số booking đang giữ phòng;
- `expected_cancellations`: tổng các $p_i$;
- `k`: số phòng bán vượt đề xuất;
- `rooms`: số phòng mở bán của đêm đó, lấy từ `gold.hotel_rooms`;
- `can_sell = max(0, rooms + k − bookings)`: số booking còn nhận thêm được.

$K$ được tính trên các booking đang có tại thời điểm hỏi. Khi có booking mới, kết quả cần được tính lại.

## 4. Calibration quan trọng hơn AUC

Quy tắc chọn $K$ dùng trực tiếp giá trị của $p_i$, không chỉ thứ hạng giữa các booking. Vì vậy, yêu cầu chính với
model là **calibration**: trong các booking được dự báo 30%, tỉ lệ huỷ thực tế phải xấp xỉ 30%.

AUC chỉ đo khả năng xếp booking dễ huỷ lên trên booking khó huỷ. Một model có AUC cao nhưng dự báo lệch đều 10 điểm
phần trăm vẫn cho $K$ sai.

Ví dụ minh hoạ bằng hàm `limit`: 100 booking có xác suất huỷ thật là 0,46, khi đó $K$ đúng là 43. Nếu model dự báo
0,33 cho mọi booking thì $K = 30$. Khách sạn bán thiếu 13 phòng so với mức tối ưu. Đây chính là tình huống của model
v1 sau drift (mục 6).

Có hai hệ quả trong thiết kế:

- **Trần AUC thấp là có chủ đích.** Nhãn huỷ phụ thuộc một biến ẩn (`propensity`, mục 5.2) mà model không quan sát
  được. Ngay cả khi biết công thức nhãn thật, AUC chỉ đạt 0,734; với các input model có thì trần là khoảng 0,68.
- **Cổng promote không dùng ngưỡng AUC cao.** Model chỉ được gán alias `production` khi AUC ≥ 0,60 (sàn chặn model
  hỏng), lệch calibration ≤ 0,03 và Brier không cao hơn bản production trên cùng tập validation. Cổng so Brier chứ
  không so AUC với bản production: sau drift, AUC của v1 gần như giữ nguyên, chỉ calibration lệch nặng (mục 6).

## 5. Dữ liệu và nhãn

### 5.1 Chuỗi nhân quả của generator

Dữ liệu do generator tái lập được sinh ra theo chuỗi: lượt xem giá (quote) → booking → huỷ → event. Booking là quote
có `booked = 1`. Generator biết xác suất huỷ thật của từng booking và ghi vào bucket riêng `truth/p_cancel/`. Pipeline
không đọc bucket này; nó chỉ dùng để chấm điểm model (mục 7).

### 5.2 Công thức nhãn

Xác suất huỷ thật của một booking là hàm logistic:

$$p = \sigma\left(-2{,}0 + 0{,}8 \cdot \frac{\ln(1 + \text{lead})}{3} + 1{,}2 \cdot \text{flexible} + 0{,}6 \cdot \text{propensity} - 0{,}5 \cdot \text{loyalty}\right)$$

| Thành phần | Ý nghĩa | Model có thấy không |
|---|---|---|
| `lead` | số ngày từ lúc đặt tới ngày nhận phòng; đặt càng sớm càng dễ huỷ | có (`lead_days`) |
| `flexible` | giá linh hoạt, được huỷ miễn phí | có (`free_cancel`) |
| `loyalty` | hạng thành viên 0–3; hạng cao ít huỷ hơn | có (`loyalty_tier`) |
| `propensity` | xu hướng huỷ riêng của từng khách, phân phối chuẩn | **không**, chỉ lộ gián tiếp qua lịch sử huỷ của khách |

Biến `propensity` không được ghi ra landing. Model chỉ ước lượng được nó qua các feature lịch sử như `cancel_rate_90d`.
Thiết kế này mô phỏng thực tế: luôn có yếu tố không quan sát được.

### 5.3 Input của model

Model nhận 10 input (`MODEL_INPUTS`), chia ba nhóm:

- **Thuộc tính booking:** `lead_days`, `nights`, `free_cancel`.
- **Lịch sử khách** (cửa sổ 90 ngày): `bookings_90d`, `cancel_rate_90d`, `avg_lead_days_90d`, `has_customer_history`, `loyalty_tier`.
- **Nhu cầu của khách sạn:** `bookings_7d`, `cancel_rate_30d`.

Các feature lịch sử được tính theo thời điểm (point-in-time): `event_timestamp` là cuối ngày logic `ds`, và lần huỷ
chỉ được tính khi `cancelled_at` không muộn hơn mốc đó. Nhờ vậy, feature của một booking không chứa thông tin tương lai.

Lúc train và lúc chấm dùng cùng một snapshot. DAG `score_bookings` chấm booking tạo ngày $d$ sau khi snapshot của ngày
$d$ đã lên online store, nên snapshot đó đã gồm chính booking này. Lúc train, point-in-time join cũng lấy feature tại
`booking_date + 1` (cùng snapshot). Booking bị huỷ ngay trong ngày tạo bị loại ở cả hai phía, nên snapshot không lộ
nhãn. Khách có booking rơi khỏi cửa sổ 90 ngày được ghi dòng mới ngay ngày đó, không giữ số đếm cũ tới khi hết TTL.

### 5.4 Nhãn chín

Nhãn của một booking chỉ xác định sau ngày nhận phòng: trước đó booking vẫn có thể bị huỷ. Tập train vì vậy chỉ lấy
booking đã qua ngày nhận phòng (`checkin_date < until`). `LABEL_SQL` còn dừng `booking_date` ở `until − 90` ngày. Nếu không, cuối cửa sổ chỉ còn
booking có lead time ngắn, vì booking lead time dài chưa tới ngày nhận phòng, và tập validation bị lệch.

Hệ quả: tại mọi thời điểm, khoảng ba tháng dữ liệu gần nhất chưa dùng để train được. Điều này chi phối cách xử lý
drift ở mục 6.

## 6. Drift và vòng đời model

Generator đổi hành vi từ **2025-06-01**, theo hai cách cùng lúc:

- **Concept drift:** hệ số của `lead` trong công thức nhãn tăng từ 0,8 lên 1,4. Cùng một booking, xác suất huỷ cao hơn trước.
- **Covariate drift:** lead time dài ra 1,5 lần (trung bình từ 18,6 lên 28,3 ngày). Phân phối của input thay đổi.

Tỉ lệ huỷ tăng từ 32,9% lên 47,4%. Model v1 train trên dữ liệu trước drift nên dự báo thấp hơn thực tế, và $K$ thấp theo.

Vòng đời của model được thiết kế quanh sự kiện này:

1. **Train v1** trên dữ liệu `[2025-01-01, 2025-06-01)` bằng training pipeline Kubeflow, lưu model và metadata lên
   MLflow, qua cổng promote rồi đóng vào image KServe (model-inside-image).
2. **Chờ nhãn chín rồi mới retrain.** Nếu retrain ngay sau mốc drift, tập train vẫn gần như toàn dữ liệu trước drift
   và v2 có xu hướng giống v1. Cần khoảng 120 ngày sau mốc: 30 ngày booking sau drift cộng 90 ngày cho nhãn chín.
3. **Train v2** bằng cùng pipeline trên dữ liệu sau mốc drift, qua cổng promote, build image KServe mới. DAG
   `score_bookings` chấm booking mới bằng v2; `rescore_active` (chạy tay) chấm lại các booking còn giữ phòng.
4. **So v1 với v2** bằng ground truth (mục 7): lệch calibration, Brier so với p thật và sai số K.

Mốc drift được biết trước nên retrain v2 là bước chạy tay. Phát hiện drift tự động (kiểm định KS theo thời gian thực
ở `drift-api`, PSI hằng ngày ở DAG `drift_monitor`) và canary 50/50 giữa hai phiên bản không thuộc rubric edai-1,
edai-2; code của chúng vẫn nằm trong repo nhưng không triển khai.

## 7. Đánh giá bằng ground truth

Vì generator biết xác suất huỷ thật, model được chấm trực tiếp so với sự thật, không phải chờ nhãn. Ba chỉ số chính:

- **Lệch calibration:** chênh giữa xác suất dự báo trung bình và xác suất thật trung bình.
- **Brier so với p thật:** trung bình bình phương sai số giữa $p_i$ dự báo và $p_i$ thật.
- **Sai số K:** chênh tuyệt đối giữa $K$ tính từ model và $K$ tính từ xác suất thật, lấy trung bình trên các `hotel × stay_date`.

Kết quả của `notebooks/cancel_risk.ipynb`, chạy cục bộ trên bộ dims thu nhỏ:

| | Lệch calibration | Brier vs p thật | Sai số K trung bình |
|---|---|---|---|
| v1, validation trước drift | 0,0009 | 0,016 | 0,30 |
| v1, sau drift 2025-06-01 | 0,127 | 0,040 | 1,62 |
| v2 (retrain trên dữ liệu sau drift) | 0,0008 | 0,019 | 0,36 |

Kết quả cho thấy drift làm sai số K của v1 tăng hơn năm lần, và retrain đưa sai số về gần mức ban đầu. Trên `gold.booking_risk`
của cluster mới đo được v1 với 13 ngày trước drift (`edai-2/novel_ideas.md`); phần trước/sau drift và retrain chưa lặp lại.

## 8. Vai trò của con người

Quyết định bán vượt có rủi ro kinh doanh: walk khách gây thiệt hại về tiền và uy tín. Hệ thống vì vậy tách hai bước:

- `propose_overbooking` chỉ đọc dữ liệu và trả đề xuất.
- `apply_overbooking` ghi $K$ vào `gold.overbooking_limits`. Tool này nằm trong `requireApproval` của agent, nên giao
  diện kagent dừng lại chờ revenue manager duyệt trước khi ghi.

Revenue manager hỏi bằng ngôn ngữ tự nhiên, ví dụ "Đêm 30/4 nên bán vượt bao nhiêu phòng?". Coordinator agent chuyển
câu hỏi cho policy-agent và data-agent; các agent gọi tool qua agentgateway và tra chính sách nội bộ bằng RAG.

## 9. Giả định và giới hạn

- **Huỷ độc lập.** Mô hình Poisson-binomial giả định các booking huỷ độc lập. Huỷ hàng loạt (bão, sự kiện bị hoãn)
  làm phương sai lớn hơn mô hình ước tính. Generator chưa mô phỏng tình huống này.
- **Chi phí cố định.** $c_{\text{spoil}}$ và $c_{\text{walk}}$ là hai hằng số chung, chưa thay đổi theo khách sạn,
  loại phòng hay mùa.
- **Không tính no-show và booking tương lai.** $K$ chỉ dựa trên xác suất huỷ của các booking đang có.
- **Dữ liệu giả lập.** Mọi kết quả phụ thuộc công thức nhãn của generator. Ưu điểm là có ground truth để chấm; hạn chế
  là chưa kiểm chứng trên dữ liệu thật.
- **Không định giá.** Phần tối ưu giá đã được cắt khỏi phạm vi; hệ thống chỉ có một model `cancel-risk`.
- **Không tự động hoá vòng đời model.** Không phát hiện drift tự động, không canary giữa hai phiên bản model (mục 6);
  A/B chỉ áp cho agent và phiên bản LLM trên nền tảng LLM.
- **Một PostgreSQL dùng chung.** Trên môi trường demo GKE, một pod PostgreSQL (2 CPU, 8Gi RAM, PVC 200Gi,
  `edai1/k8s/storage.yaml`) đồng thời phục vụ Gold (~140 triệu dòng), offline và online store của Feast, pgvector,
  sink của Flink, catalog Iceberg, metadata của Airflow và MLflow. Truy vấn OLAP nặng hoặc backfill có thể làm chậm
  đường đọc online của booking-mcp. Khi triển khai thật nên tách ít nhất online store và metadata của các công cụ
  sang instance riêng, chuyển Gold sang kho phân tích (vd. BigQuery) hoặc dùng read replica.
- **Feature `bookings_1h` chưa vào model.** Nhánh stream (Flink → `gold.feat_hotel_realtime` → Airflow 5 phút →
  `feast_online`) đã chạy nhưng model `cancel-risk` chưa dùng feature này vì dữ liệu train chưa có lịch sử của nó
  (`ml/training_pipeline.py`). Đường đi qua Airflow cũng làm độ trễ tối đa khoảng 5 phút; khi đưa feature vào model
  nên cho Flink ghi thẳng online store (Feast push source).

## 10. Thuật ngữ

| Thuật ngữ | Giải thích |
|---|---|
| Overbooking | bán số booking nhiều hơn số phòng, dựa trên dự đoán sẽ có booking huỷ |
| $K$ (overbooking limit) | số phòng được bán vượt cho một khách sạn trong một đêm |
| Spoilage | phòng bị bỏ trống do booking huỷ mà không bán bù |
| Walk | khách đến nhưng hết phòng, phải chuyển sang khách sạn khác |
| Lead time | số ngày từ lúc đặt tới ngày nhận phòng |
| Calibration | mức khớp giữa xác suất dự báo và tần suất xảy ra thực tế |
| Brier score | trung bình bình phương sai số của xác suất dự báo; càng thấp càng tốt |
| Concept drift | quan hệ giữa input và nhãn thay đổi |
| Covariate drift | phân phối của input thay đổi |
| PSI, KS | hai phép đo mức khác biệt giữa hai phân phối, dùng để phát hiện drift |
| Nhãn chín | nhãn đã xác định chắc chắn, tức booking đã qua ngày nhận phòng |
| HITL (human-in-the-loop) | bước bắt buộc có người duyệt trước khi hệ thống hành động |
