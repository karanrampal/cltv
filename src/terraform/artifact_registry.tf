resource "google_artifact_registry_repository" "artifact_reg" {
  for_each      = var.artifact_regs
  project       = var.main.project_id
  location      = var.main.region
  repository_id = each.value.name
  description   = "Docker repository for python model images"
  format        = "DOCKER"
}

resource "google_artifact_registry_repository_iam_member" "member" {
  for_each   = var.artifact_regs
  project    = var.main.project_id
  location   = var.main.region
  repository = each.value.name
  role       = "roles/artifactregistry.admin"
  member     = "serviceAccount:${var.main.service_account}"
  depends_on = [google_artifact_registry_repository.artifact_reg]
}
