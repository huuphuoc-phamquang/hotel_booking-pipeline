# Warm-up (Agent Substrate)

Giữ sẵn worker cho agent để giảm chi phí và độ trễ khởi động.

<a id="edai-2-27"></a>
## Chế độ Warm-up cho agent (Agent Fleet Architecture)

**[update sau]:** Đã thiết kế cấu hình trong `k8s/agent-substrate.yaml` sử dụng `WorkerPool` để giữ sẵn 2 worker ở trạng thái warm và chụp snapshot actor khi rảnh, kết hợp HPA scale qua subresource của `WorkerPool` khi tải tăng. Hướng triển khai là nâng cấp `kagent` lên phiên bản hỗ trợ Agent Substrate để chạy thử nghiệm nhiều agent chia sẻ trên số lượng worker tối thiểu, sau đó bổ sung số liệu và ảnh chụp thực tế trên cluster.
