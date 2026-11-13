# Repository & low-level ML design

README/documentation, design pattern, 5 class chính.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-55"></a>
## README.md và documentation follow rule ở ô A2

**Rubric:** edai-2 · dòng 55 · 2 điểm · nhóm *Repository Design*

**Cách làm:** [Cần làm] README theo ô A2: Repo Structure, TOC, docstring đầu file; dùng sơ đồ docs/architecture/booking-pricing.drawio (ảnh booking-pricing.png); link docs/README.md (bảng tra rubric).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-56"></a>
### Clean Code + clean repo + demonstrate the use of Design Pattern

**Rubric:** final · dòng 56 · 2 điểm · nhóm *Repository Design*

**Cần nộp (cả nhóm):** Capture màn hình thể hiện Design Pattern đã được sử dụng trong code

**Cách làm:** [Thiết kế] Repository (đọc Feast online qua một hàm _online duy nhất), Adapter (KServe V1 sau CancelRiskClient), Strategy (DriftDetector KS / PSI hoán đổi cho drift-api và drift_monitor), Factory (chọn model theo alias MLflow production).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-57"></a>
### Propose 5 key classes to present our main focus:

**Rubric:** final · dòng 57 · 1 điểm · nhóm *Documentation* › *Low-level ML Design*

> Propose 5 key classes to present our main focus: Example: class TrainingDataService: def read_training_table(self) -> DataFrame: ... def validate_schema(self, df: DataFrame) -> None: ... def dedup_by_created_ts(self, df: DataFrame) -> DataFrame: ... class SplitService: def get_split_boundaries(self, df: DataFrame) -> dict: ... def split_by_time(self, df: DataFrame) -> tuple[DataFrame, DataFrame, DataFrame]: ...

**Cần nộp (cả nhóm):** Document 5 key classes

**Cách làm:** [Thiết kế] docs/edai-2/ml_design.md: TrainingDataService, SplitService, CancelRiskTrainer, CancelRiskClient, OverbookingPlanner.

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

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
