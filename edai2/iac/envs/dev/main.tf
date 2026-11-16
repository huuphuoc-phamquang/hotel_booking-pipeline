# Rubric edai-2 › IaC › Terraform setup GKE (chia module theo service).
# Chạy: bucket state tạo trước bằng `gcloud storage buckets create gs://<project>-tf-state --location=asia-southeast1`
#   terraform init -backend-config="bucket=<project>-tf-state" && terraform apply -var project_id=... -var billing_account=...
# Proof: docs/IaC.md chụp output `terraform apply`.
terraform {
  required_version = ">= 1.9"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
  backend "gcs" { prefix = "envs/dev" }
}

provider "google" {
  project               = var.project_id
  region                = var.region
  billing_project       = var.project_id
  user_project_override = true # billing budget API cần quota project
}

variable "project_id" { type = string }
variable "billing_account" { type = string }
variable "region" {
  type    = string
  default = "asia-southeast1"
}
variable "zone" {
  type    = string
  default = "asia-southeast1-b" # có L4
}
variable "budget" {
  type    = number
  default = 7900000 # ≈ $300, theo tiền tệ billing account (VND)
}

data "google_project" "this" {}

resource "google_project_service" "apis" {
  for_each = toset(["container.googleapis.com", "artifactregistry.googleapis.com", "compute.googleapis.com",
  "billingbudgets.googleapis.com"])
  service            = each.value
  disable_on_destroy = false
}

module "network" {
  source     = "../../modules/network"
  name       = "booking"
  region     = var.region
  depends_on = [google_project_service.apis]
}

module "gke" {
  source        = "../../modules/gke"
  name          = "booking-ai"
  zone          = var.zone
  network       = module.network.network
  subnetwork    = module.network.subnetwork
  cpu_max_nodes = 6
  gpu_max_nodes = 1
}

module "registry" {
  source     = "../../modules/registry"
  region     = var.region
  depends_on = [google_project_service.apis]
}

module "budget" {
  source          = "../../modules/budget"
  billing_account = var.billing_account
  project_number  = data.google_project.this.number
  amount          = var.budget
  depends_on      = [google_project_service.apis]
}

output "cluster" { value = module.gke.name }
output "registry" { value = module.registry.url }
