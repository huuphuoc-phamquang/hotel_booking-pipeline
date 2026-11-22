# Warm-up (Agent Substrate)

Giữ sẵn worker cho agent để giảm chi phí và độ trễ khởi động.

<a id="edai-2-27"></a>
## Chế độ Warm-up cho agent (Agent Fleet Architecture)

Hệ thống đã triển khai chế độ Warm-up theo mô hình **Agent Fleet** của Agent Substrate tại [agent-substrate-v1.yaml](../../edai2/k8s/agent-substrate-v1.yaml):

- **Pool worker warm dùng chung (`WorkerPool/agents-warm`):** duy trì sẵn `2/2 Ready` worker pod gVisor (`agents-warm-96bf878d7-fj7cd` tại `10.42.0.175` và `agents-warm-96bf878d7-qmffk` tại `10.42.0.177`, image `ateworker-gvisor:v1.0.1`, `SandboxConfig/gvisor-default`), kết hợp object storage RustFS (`s3://ate-snapshots`) để lưu golden snapshot và actor checkpoint.
- **Nhiều agent chia sẻ số lượng worker tối thiểu:** cả 4 agent (`data-agent`, `policy-agent`, `policy-agent-v2`, `coordinator-agent`) cùng tham chiếu `Harness/kagent-default` và đạt `Ready=True` (`ActorTemplate golden snapshot is ready`), chạy ghép kênh trên đúng 2 worker pod thay vì cấp 1 Deployment/Pod riêng cho từng agent hoặc từng session.
- **Đo đạc thực tế khi gọi A2A (`lf.a2a.v1.A2AService/SendMessage`):** `atelet` khôi phục (restore) actor gVisor từ snapshot chỉ mất **`103.9ms–122.5ms`** (`data-agent`: `103.9ms`, `policy-agent`: `122.5ms`, `policy-agent-v2`: `121.0ms`, `coordinator-agent`: `111.9ms`) và checkpoint sau lượt chạy mất **`76.9ms–88.3ms`**, đạt `grpc-status: 0` khi gọi `vllm-booking` với tổng thời gian phản hồi end-to-end `1.61s–3.12s`.

![Agent Substrate Warm-up WorkerPool phục vụ 4 agent trên 2 worker gVisor](../images/edai-2/substrate-warmup.jpg)
