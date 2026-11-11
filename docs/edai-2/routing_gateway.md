# Routing & gateway (NGINX Ingress)

Ẩn service sau ingress, basic auth, rate limit, domain + HTTPS.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-37"></a>
## Service để coi metric · edai-2 · External Routing & Gateway (NGINX Ingress Controll

**Rubric:** edai-2 · dòng 37 · 2 điểm · nhóm *External Routing & Gateway (NGINX Ingress Controller)* › *Các service cần được hide đằng sau gateway*

> Service để coi metric (ví dụ Grafana)

**Cần nộp (cả nhóm):** Document phải link được tới các setting trên NGINX, để thể hiện mọi người đã setup như thế nào

**Cách làm:** [Đã có] ingress grafana.booking.local. [Cần làm] chụp truy cập qua ingress.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-38"></a>
## Service để coi log · edai-2 · External Routing & Gateway (NGINX Ingress Controll

**Rubric:** edai-2 · dòng 38 · 2 điểm · nhóm *External Routing & Gateway (NGINX Ingress Controller)* › *Các service cần được hide đằng sau gateway*

> Service để coi log (ví dụ Kibana)

**Cách làm:** [Đã có] ingress kibana.booking.local. [Cần làm] chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-39"></a>
## Service để coi trace · edai-2 · External Routing & Gateway (NGINX Ingress Controll

**Rubric:** edai-2 · dòng 39 · 2 điểm · nhóm *External Routing & Gateway (NGINX Ingress Controller)* › *Các service cần được hide đằng sau gateway*

> Service để coi trace (ví dụ Jaeger)

**Cách làm:** [Đã có] ingress jaeger.booking.local. [Cần làm] chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-40"></a>
## UI để test agent

**Rubric:** edai-2 · dòng 40 · 2 điểm · nhóm *External Routing & Gateway (NGINX Ingress Controller)* › *Các service cần được hide đằng sau gateway*

> UI để test agent (xem tại đây)

**Cách làm:** [Đã có] ingress agents.booking.local (kagent UI). [Cần làm] chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-41"></a>
## UI cho agent registry

**Rubric:** edai-2 · dòng 41 · 2 điểm · nhóm *External Routing & Gateway (NGINX Ingress Controller)* › *Các service cần được hide đằng sau gateway*

**Cách làm:** [Đã có] ingress registry.agents.booking.local. [Cần làm] deploy registry rồi chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-42"></a>
## Setup authentication cho UI test agent ở trên

**Rubric:** edai-2 · dòng 42 · 2 điểm · nhóm *External Routing & Gateway (NGINX Ingress Controller)* › *Basic authentication & rate limit ở gateway (username/password)*

**Cách làm:** [Đã có] basic auth (htpasswd) + limit-rps 10 cho kagent UI. [Cần làm] chụp 401 khi sai mật khẩu.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-43"></a>
## Làm cái này cho Web API kéo dữ liệu · edai-2 · External Routing & Gateway (NGINX Ingress Controll

**Rubric:** edai-2 · dòng 43 · 1 điểm · nhóm *External Routing & Gateway (NGINX Ingress Controller)* › *Setup domain & enable HTTPS*

> Làm cái này cho Web API kéo dữ liệu. Mọi người có thể tham khảo 2 đồ án sau: cái này và cái này

**Cách làm:** [Đã có] cert-manager letsencrypt cho api.booking.example.com. [Cần làm] cần domain thật trỏ về ingress; chụp cert hợp lệ.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-38"></a>
### Service để coi metric · final · Routing & Gateway (NGINX Ingress Controller)

**Rubric:** final · dòng 38 · 2 điểm · nhóm *Routing & Gateway (NGINX Ingress Controller)* › *Các service cần được hide đằng sau gateway*

> Service để coi metric (ví dụ Grafana)

**Cần nộp (cả nhóm):** Capture màn hình thể hiện từng setup đã thành công

**Cách làm:** [Đã có] k8s/ingress.yaml grafana.booking.local. [Cần làm] chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-39"></a>
### Service để coi log · final · Routing & Gateway (NGINX Ingress Controller)

**Rubric:** final · dòng 39 · 2 điểm · nhóm *Routing & Gateway (NGINX Ingress Controller)* › *Các service cần được hide đằng sau gateway*

> Service để coi log (ví dụ Kibana)

**Cách làm:** [Đã có] k8s/ingress.yaml kibana.booking.local (EFK ở docs/edai-2/observability.md). [Cần làm] chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-40"></a>
### Service để coi trace · final · Routing & Gateway (NGINX Ingress Controller)

**Rubric:** final · dòng 40 · 2 điểm · nhóm *Routing & Gateway (NGINX Ingress Controller)* › *Các service cần được hide đằng sau gateway*

> Service để coi trace (ví dụ Jaeger)

**Cách làm:** [Đã có] k8s/ingress.yaml jaeger.booking.local. [Cần làm] chụp.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-41"></a>
### Web API kéo dữ liệu

**Rubric:** final · dòng 41 · 2 điểm · nhóm *Routing & Gateway (NGINX Ingress Controller)* › *Các service cần được hide đằng sau gateway*

**Cách làm:** [Thiết kế] thêm host api.booking.example.com -> pricing-api trong ingress.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-42"></a>
### Setup authentication & rate limit cho Web API kéo dữ liệu

**Rubric:** final · dòng 42 · 2 điểm · nhóm *Routing & Gateway (NGINX Ingress Controller)* › *Basic authentication & rate limit ở gateway (username/password)*

**Cách làm:** [Thiết kế] pricing-api: annotation auth-type basic + secret htpasswd, limit-rps; chụp 401 khi thiếu mật khẩu và 503 khi vượt limit.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-43"></a>
### Làm cái này cho Web API kéo dữ liệu · final · Routing & Gateway (NGINX Ingress Controller)

**Rubric:** final · dòng 43 · 1 điểm · nhóm *Routing & Gateway (NGINX Ingress Controller)* › *Setup domain & enable HTTPS*

> Làm cái này cho Web API kéo dữ liệu. Mọi người có thể tham khảo 2 đồ án sau: cái này và cái này

**Cách làm:** [Đã có] cert-manager Let's Encrypt cho api.booking.example.com trong ingress. [Cần làm] trỏ domain, chụp cert.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
