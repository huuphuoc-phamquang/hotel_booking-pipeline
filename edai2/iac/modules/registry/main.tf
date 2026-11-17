# Artifact Registry cho image của Jenkins (booking-mcp, drift-api, cancel-risk, generator, Spark, Flink).
variable "region" { type = string }

resource "google_artifact_registry_repository" "booking" {
  repository_id = "booking"
  location      = var.region
  format        = "DOCKER"
}

output "url" { value = "${var.region}-docker.pkg.dev/${google_artifact_registry_repository.booking.project}/booking" }
