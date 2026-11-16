# Chính sách bán vượt (overbooking) và chuyển khách

## Vì sao bán vượt
Một phần booking sẽ huỷ hoặc không đến. Để không bỏ trống phòng, khách sạn nhận thêm K booking so với số phòng. K được
chọn sao cho cân bằng hai chi phí:
- **Phòng trống (c_spoil):** mất doanh thu 1 đêm, quy ước 1 đơn vị giá phòng.
- **Chuyển khách (c_walk):** chuyển khách sang khách sạn khác khi số khách đến vượt số phòng, quy ước 3 đơn vị giá phòng
  (bồi thường + vận chuyển + uy tín).

K là số lớn nhất sao cho xác suất "số booking huỷ ít hơn K" không vượt c_spoil / (c_spoil + c_walk) = 1/4. Xác suất huỷ
của từng booking lấy từ model cancel-risk, cộng dồn theo khách sạn × đêm (không dùng để đổi giá hay điều kiện của
từng khách).

## Phê duyệt
- Hệ thống chỉ **đề xuất** K. Revenue manager phải duyệt trước khi K được ghi và áp dụng.
- Không bán vượt cho đêm có sự kiện lớn mà tỉ lệ huỷ lịch sử dưới 10%.

## Khi phải chuyển khách
- Ưu tiên giữ lại khách hạng thành viên cao, khách đặt giá không hoàn tiền, khách ở nhiều đêm.
- Khách bị chuyển: phòng tương đương hoặc tốt hơn ở khách sạn gần, miễn phí đêm đầu, xe đưa đón, hoàn 100% tiền đã trả
  cho đêm bị chuyển.
