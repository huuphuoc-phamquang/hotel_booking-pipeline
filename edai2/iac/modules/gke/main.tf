# GKE zonal (1 cluster zonal được miễn phí quản lý). 2 node pool:
#   - cpu : spot e2-standard-8 (rẻ hơn ~60-70%, có thể bị thu hồi -> mọi workload đều chạy lại được), autoscale
#   - gpu : g2-standard-8 + 1 L4 cho vLLM, min 0 -> chỉ tốn tiền khi có pod xin GPU
variable "name" { type = string }
variable "zone" { type = string }
variable "network" { type = string }
variable "subnetwork" { type = string }
variable "cpu_max_nodes" { type = number }
variable "gpu_max_nodes" { type = number }

resource "google_container_cluster" "main" {
  name                     = var.name
  location                 = var.zone
  network                  = var.network
  subnetwork               = var.subnetwork
  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = false
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  workload_identity_config { workload_pool = "${data.google_project.this.project_id}.svc.id.goog" }
}

data "google_project" "this" {}

resource "google_container_node_pool" "cpu" {
  name     = "cpu-spot"
  cluster  = google_container_cluster.main.name
  location = var.zone
  autoscaling {
    min_node_count = 0
    max_node_count = var.cpu_max_nodes
  }
  node_config {
    machine_type = "e2-standard-8"
    spot         = true
    disk_size_gb = 100
    disk_type    = "pd-balanced"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    workload_metadata_config { mode = "GKE_METADATA" }
  }
}

resource "google_container_node_pool" "gpu" {
  name     = "gpu-l4"
  cluster  = google_container_cluster.main.name
  location = var.zone
  autoscaling {
    min_node_count = 0
    max_node_count = var.gpu_max_nodes
  }
  node_config {
    machine_type = "g2-standard-8"
    spot         = true
    disk_size_gb = 200 # image vLLM + model Qwen
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    guest_accelerator {
      type  = "nvidia-l4"
      count = 1
      gpu_driver_installation_config { gpu_driver_version = "LATEST" }
    }
    taint {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }
  }
}

output "name" { value = google_container_cluster.main.name }
