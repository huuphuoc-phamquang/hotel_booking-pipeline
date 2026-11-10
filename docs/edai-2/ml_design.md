# Repository & low-level ML design

README/documentation, design pattern, 5 class chính.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-55"></a>
## README.md và documentation follow rule ở ô A2

**Rubric:** edai-2 · dòng 55 · 2 điểm · nhóm *Repository Design*

**Cách làm:** [Cần làm] README theo ô A2: Repo Structure, TOC, docstring đầu file; dùng sơ đồ docs/architecture/booking-pricing.drawio (ảnh booking-pricing.png, trang components.html) thay booking-platform.html; link docs/booking-pricing-design.md.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-56"></a>
### Clean Code + clean repo + demonstrate the use of Design Pattern

**Rubric:** final · dòng 56 · 2 điểm · nhóm *Repository Design*

**Cần nộp (cả nhóm):** Capture màn hình thể hiện Design Pattern đã được sử dụng trong code

**Cách làm:** [Thiết kế] Repository (FeatureRepository bọc Feast), Strategy (DemandModel v1/v2 cho A/B), Chain of Responsibility (GuardrailChain), Factory (ModelClientFactory theo alias MLflow).

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-57"></a>
### Propose 5 key classes to present our main focus:

**Rubric:** final · dòng 57 · 1 điểm · nhóm *Documentation* › *Low-level ML Design*

> Propose 5 key classes to present our main focus: Example: class TrainingDataService: def read_training_table(self) -> DataFrame: ... def validate_schema(self, df: DataFrame) -> None: ... def dedup_by_created_ts(self, df: DataFrame) -> DataFrame: ... class SplitService: def get_split_boundaries(self, df: DataFrame) -> dict: ... def split_by_time(self, df: DataFrame) -> tuple[DataFrame, DataFrame, DataFrame]: ...

**Cần nộp (cả nhóm):** Document 5 key classes

**Cách làm:** [Thiết kế] TrainingDataService, SplitService, DemandModel, PriceOptimizer, GuardrailChain.

```python
class TrainingDataService:
    def read_labels(self, start: date, end: date) -> DataFrame: ...       # labels_cancel, chỉ booking đã qua check-in
    def join_features(self, labels: DataFrame) -> DataFrame: ...           # Feast get_historical_features
    def snapshot(self, df: DataFrame) -> int: ...                          # MERGE vào Iceberg, trả snapshot_id

class SplitService:
    def split_by_time(self, df: DataFrame, cutoff: date) -> tuple[DataFrame, DataFrame]: ...

class DemandModel:                                                         # Strategy: v1 / v2
    def expected_demand(self, cell: PriceCell, grid: list[float]) -> list[list[float]]: ...  # D_k(P) [nhóm k][điểm lưới]

class PriceOptimizer:                                                      # giải chung mọi nhóm k
    def best_prices(self, cell: PriceCell, demand: list[list[float]], p_cancel: list[list[float]],
                    capacity: float, cost: float) -> list[Quote]: ...

class GuardrailChain:
    def apply(self, quote: Quote, yesterday: Quote | None) -> Quote: ...  # sàn/trần → ±15% → kỳ nghỉ dài
```

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
