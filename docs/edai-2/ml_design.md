# Repository & low-level ML design

README, tài liệu kỹ thuật và sơ đồ kiến trúc tổng thể của hệ thống.

<a id="edai-2-55"></a>
## README.md và tài liệu kiến trúc

[`README.md`](../../README.md) ở gốc repo trình bày bài toán nghiệp vụ (dự báo cancellation để tối ưu overbooking có người duyệt), cấu trúc repository, luồng dữ liệu theo ngày và liên kết tới [`docs/README.md`](../README.md). Toàn bộ file mã nguồn đều có docstring mô tả ở đầu file.

Sơ đồ kiến trúc tổng thể [`booking-overbooking.drawio`](../architecture/booking-overbooking.drawio) được thiết kế theo chuẩn mỗi thành phần chính là một deployable unit, phân biệt rõ luồng dữ liệu và luồng người dùng/MLOps bằng màu sắc và đánh số thứ tự `1→n`.

![Sơ đồ kiến trúc tổng thể booking-overbooking](../architecture/booking-overbooking.png)
