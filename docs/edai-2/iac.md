# Infrastructure as Code

Terraform dựng hạ tầng GKE; Ansible cấu hình VM.

Mỗi mục dưới đây ứng với một dòng của rubric. Phần **Cách làm** mô tả giải pháp đã triển khai, đồng bộ từ
cột F của rubric. Phần **Kết quả** ghi test đã chạy, số liệu đo được hoặc ảnh chụp (`docs/images/`).

<a id="edai-2-44"></a>
## Dùng Terraform để setup GKE hoặc các cloud services · edai-2 · IaC

**Rubric:** edai-2 · dòng 44 · 1 điểm · nhóm *IaC*

**Cần nộp (cả nhóm):** Document phải show hình ảnh Terraform và Ansible code đã chạy

**Cách làm:** [Đã có] `iac/modules/{network,gke,registry,budget}` và `iac/envs/dev`: VPC với Cloud NAT, GKE node private, pool CPU spot và pool GPU L4 (tối thiểu 0 node), Artifact Registry, cảnh báo ngân sách. [Cần làm] chụp `terraform apply`.

**Kết quả:** hạ tầng dựng bằng `terraform apply` trong `iac/envs/dev` (project `hotel-booking-edai`, asia-southeast1).
Chạy lại `terraform apply` (2026-11-18) báo `No changes`: hạ tầng thật khớp code, không có thay đổi tay ngoài
Terraform. Output là cluster `booking-ai` và registry `asia-southeast1-docker.pkg.dev/hotel-booking-edai/booking`;
state quản lý 13 tài nguyên và 2 data source (4 API, budget, VPC, subnet, router, Cloud NAT, cluster GKE, 2 node pool, Artifact Registry).

![terraform apply](../images/edai-2/terraform-apply.png)

![terraform state list](../images/edai-2/terraform-state.png)

<a id="edai-2-45"></a>
## Dùng Ansible để configure và deploy các service lên VM · edai-2 · IaC

**Rubric:** edai-2 · dòng 45 · 1 điểm · nhóm *IaC*

**Cách làm:** [Đã có] `iac/ansible` gồm `site.yml` và các role common, docker, vault, jenkins (chạy dạng container); `--syntax-check` và `ansible-lint` profile production đều sạch. [Cần làm] chạy trên VM, chụp kết quả playbook.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._

## Bổ sung final-coursework

<a id="final-44"></a>
### Dùng Terraform để setup GKE hoặc các cloud services · final · IaC

**Rubric:** final · dòng 44 · 2 điểm · nhóm *IaC*

**Cần nộp (cả nhóm):** Capture màn hình thể hiện từng setup đã chạy thành công

**Cách làm:** [Đã có] `iac/modules/{network,gke,registry,budget}` và `iac/envs/dev` (state lưu trên GCS); `terraform validate` sạch. [Cần làm] chụp `terraform apply`.

**Kết quả:** `terraform apply` báo `No changes` và `terraform state list` liệt kê đủ tài nguyên, ảnh ở
[mục edai-2 dòng 44](#edai-2-44).

<a id="final-45"></a>
### Dùng Ansible để configure và deploy các service lên VM · final · IaC

**Rubric:** final · dòng 45 · 2 điểm · nhóm *IaC*

**Cách làm:** [Đã có] `iac/ansible` gồm `site.yml` và các role common (ufw), docker, vault (container cùng `vault.hcl`), jenkins; `ansible-playbook --syntax-check` và `ansible-lint` profile production đều sạch. [Cần làm] chạy trên VM, chụp kết quả playbook.

**Kết quả:** _Chưa có. Cần số liệu, ảnh chụp hoặc link code sau khi chạy trên cluster._
