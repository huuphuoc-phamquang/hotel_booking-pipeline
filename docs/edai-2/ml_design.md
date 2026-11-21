# Repository & low-level ML design

README và tài liệu, các design pattern đã dùng và 5 class chính của hệ thống ML.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-55"></a>
## README.md và documentation follow rule ở ô A2

**Rubric:** edai-2 · dòng 55 · 2 điểm · nhóm *Repository Design*

**Cách làm:** [Đã có] [`README.md`](../../README.md) ở gốc repo trình bày bài toán (dự báo cancellation để overbooking, có người duyệt), sơ đồ [`docs/architecture/booking-overbooking.png`](../architecture/booking-overbooking.png) (nguồn `.drawio`), mục lục, cấu trúc repo, luồng dữ liệu theo ngày và link tới [`docs/README.md`](../README.md); mọi file mã đều có docstring đầu file.

**Kết quả:** Đã hoàn thiện [`README.md`](../../README.md), [`docs/README.md`](../README.md) và sơ đồ kiến trúc tổng thể [`booking-overbooking.drawio`](../architecture/booking-overbooking.drawio) theo đúng quy tắc ô A2 (mỗi thành phần chính là 1 deployable unit, phân biệt luồng dữ liệu và luồng người dùng/MLOps bằng màu sắc và đánh số thứ tự `1→n`).

![Sơ đồ kiến trúc tổng thể booking-overbooking](../architecture/booking-overbooking.png)
