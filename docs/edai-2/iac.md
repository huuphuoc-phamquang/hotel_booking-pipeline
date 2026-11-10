# Infrastructure as Code

Terraform cho GKE, Ansible cho VM.

Mỗi mục ứng với một dòng rubric. **Cách làm** lấy từ thiết kế (cột F của rubric);
**Kết quả** điền khi đã chạy: số liệu, ảnh chụp (`docs/images/`), link code.

<a id="edai-2-44"></a>
## Dùng Terraform để setup GKE hoặc các cloud services · edai-2 · IaC

**Rubric:** edai-2 · dòng 44 · 1 điểm · nhóm *IaC*

**Cần nộp (cả nhóm):** Document phải show hình ảnh Terraform và Ansible code đã chạy

**Cách làm:** [Đã có] iac/gke/main.tf: cluster + node pool CPU/GPU. [Cần làm] tách folder theo service; chụp terraform apply.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="edai-2-45"></a>
## Dùng Ansible để configure và deploy các service lên VM · edai-2 · IaC

**Rubric:** edai-2 · dòng 45 · 1 điểm · nhóm *IaC*

**Cách làm:** [Cần làm] chưa có Ansible: roles cho VM (vd Jenkins, Vault); chụp playbook chạy.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

## Bổ sung final-coursework

<a id="final-44"></a>
### Dùng Terraform để setup GKE hoặc các cloud services · final · IaC

**Rubric:** final · dòng 44 · 2 điểm · nhóm *IaC*

**Cần nộp (cả nhóm):** Capture màn hình thể hiện từng setup đã chạy thành công

**Cách làm:** [Đã có] iac/gke/main.tf (GKE + node pool CPU/GPU). [Thiết kế] tách iac/modules/{network,gke,gcs} + iac/envs/dev.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_

<a id="final-45"></a>
### Dùng Ansible để configure và deploy các service lên VM · final · IaC

**Rubric:** final · dòng 45 · 2 điểm · nhóm *IaC*

**Cách làm:** [Thiết kế] VM Jenkins + Vault, role common, docker, jenkins, vault (như edai-2). [Cần làm] chụp playbook.

**Kết quả:** _chưa có — số liệu, ảnh chụp, link code_
