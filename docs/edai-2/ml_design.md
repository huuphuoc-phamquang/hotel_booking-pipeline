# Repository & low-level ML design

README và tài liệu, các design pattern đã dùng và 5 class chính của hệ thống ML.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-55"></a>
## README.md và documentation follow rule ở ô A2

**Rubric:** edai-2 · dòng 55 · 2 điểm · nhóm *Repository Design*

**Cách làm:** [Đã có] `README.md` ở gốc repo trình bày bài toán (dự báo cancellation để overbooking, có người duyệt), sơ đồ `docs/architecture/booking-overbooking.png` (nguồn `.drawio`), mục lục, cấu trúc repo, luồng dữ liệu theo ngày và link tới `docs/README.md`; mọi file mã đều có docstring đầu file.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

## Bổ sung final-coursework

<a id="final-56"></a>
### Clean Code + clean repo + demonstrate the use of Design Pattern

**Rubric:** final · dòng 56 · 2 điểm · nhóm *Repository Design*

**Cần nộp (cả nhóm):** Capture màn hình thể hiện Design Pattern đã được sử dụng trong code

**Cách làm:** [Đã có] Bốn design pattern: Repository (`risk_api._online` và `model_rows` gom việc đọc Feast về một chỗ), Adapter (`risk_api._predict` đổi response KServe V1 `[[p0, p1]]` thành xác suất), Facade (tool MCP gói risk-api, Postgres và Feast cho agent), Strategy (`dsl.If` chọn train một node hay TrainJob phân tán, cùng output Model). [Cần làm] chụp code của từng pattern.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

<a id="final-57"></a>
### Propose 5 key classes to present our main focus:

**Rubric:** final · dòng 57 · 1 điểm · nhóm *Documentation* › *Low-level ML Design*

> Propose 5 key classes to present our main focus: Example: class TrainingDataService: def read_training_table(self) -> DataFrame: ... def validate_schema(self, df: DataFrame) -> None: ... def dedup_by_created_ts(self, df: DataFrame) -> DataFrame: ... class SplitService: def get_split_boundaries(self, df: DataFrame) -> dict: ... def split_by_time(self, df: DataFrame) -> tuple[DataFrame, DataFrame, DataFrame]: ...

**Cần nộp (cả nhóm):** Document 5 key classes

**Cách làm:** [Đã có] `docs/edai-2/ml_design.md` đề xuất 5 class ứng với code hiện có: `TrainingDataService` (`load_from_feast` và `data_version`), `SplitService` (`split_by_time`), `CancelRiskTrainer` (`train`, `train_distributed` và `evaluate_and_register`), `CancelRiskClient` (`model_rows` và `_predict` của risk-api), `OverbookingPlanner` (`overbooking.limit`).

```python
class TrainingDataService:
    def read_labels(self, since: date, until: date) -> DataFrame: ...      # fact_bookings ⟕ cancellations, checkin < until
    def join_features(self, labels: DataFrame) -> DataFrame: ...           # Feast get_historical_features, điền thiếu như serve
    def snapshot(self, df: DataFrame) -> int: ...                          # MERGE vào Iceberg, trả snapshot_id

class SplitService:
    def split_by_time(self, df: DataFrame, cutoff: date) -> tuple[DataFrame, DataFrame]: ...

class CancelRiskTrainer:
    def fit(self, train: DataFrame) -> Model: ...                          # XGBoost trên MODEL_INPUTS, không scale_pos_weight
    def gate(self, model: Model, valid: DataFrame, production: Model | None) -> bool: ...   # AUC sàn, calibration, so production

class CancelRiskClient:                                                    # risk-api: feature theo booking_id + KServe
    async def probability(self, booking_id: int) -> float: ...

class OverbookingPlanner:
    def limit(self, probs: list[float], c_spoil: float, c_walk: float) -> int: ...   # K lớn nhất với P(N < K) ≤ c_spoil/(c_spoil+c_walk)
```

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
