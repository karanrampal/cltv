data "archive_file" "default" {
  type        = "zip"
  source_dir  = "${path.module}/../py_models/cltv/functions/"
  output_path = "/tmp/cltv_cf.zip"
}

data "google_storage_bucket" "cltv_bucket" {
  name = "${var.bucket["customer_lifetime_value"].name}-${var.main.env}"
}

resource "google_storage_bucket_object" "object" {
  name   = "cltv_cf.zip"
  bucket = data.google_storage_bucket.cltv_bucket.name
  source = data.archive_file.default.output_path
}

resource "google_cloudfunctions2_function" "cltv_cf" {
  name        = "cf-cltv_kfp"
  project     = var.main.project_id
  location    = var.main.region
  description = "Cloud function to trigger kfp pipeline for cltv model"

  build_config {
    runtime     = "python310"
    entry_point = "trigger_pipeline_run"
    source {
      storage_source {
        bucket = data.google_storage_bucket.cltv_bucket.name
        object = google_storage_bucket_object.object.name
      }
    }
  }
  service_config {
    min_instance_count    = 1
    max_instance_count    = 1
    available_memory      = "512M"
    timeout_seconds       = 3600
    service_account_email = var.main.service_account
  }
  lifecycle {
    replace_triggered_by = [google_storage_bucket_object.object]
  }
}

resource "google_cloudfunctions2_function_iam_member" "member" {
  project        = google_cloudfunctions2_function.cltv_cf.project
  location       = google_cloudfunctions2_function.cltv_cf.location
  cloud_function = google_cloudfunctions2_function.cltv_cf.name
  role           = "roles/cloudfunctions.admin"
  member         = "serviceAccount:${var.main.service_account}"
}

output "function_uri" {
  value = google_cloudfunctions2_function.cltv_cf.service_config[0].uri
}
