data "google_storage_transfer_project_service_account" "default_storage_account" {
  project = var.main.project_id
}

resource "google_storage_bucket" "storage_bucket" {
  for_each                    = var.bucket
  name                        = "${each.value.name}-${var.main.env}"
  storage_class               = "STANDARD"
  project                     = var.main.project_id
  location                    = var.main.region
  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "default_storage_account_access" {
  for_each   = var.bucket
  bucket     = "${each.value.name}-${var.main.env}"
  role       = "roles/storage.admin"
  member     = "serviceAccount:${var.main.service_account}"
  depends_on = [google_storage_bucket.storage_bucket]
}
