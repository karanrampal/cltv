resource "google_bigquery_dataset" "bigquery_dataset" {
  for_each                   = var.dataset
  dataset_id                 = each.value.dataset_id
  friendly_name              = each.value.friendly_name
  description                = each.value.description
  project                    = var.main.project_id
  location                   = var.main.region
  delete_contents_on_destroy = each.value.delete_contents_on_destroy
  labels = {

    env         = var.main.env
    tier        = each.value.tier
    data_source = each.value.data_source
  }
}


resource "google_bigquery_table" "bigquery_tables" {
  for_each            = var.bigquery_tables
  dataset_id          = each.value.dataset_id
  table_id            = each.value.table_id
  description         = each.value.description
  deletion_protection = each.value.deletion_protection
  project             = var.main.project_id
  schema              = file("${each.value.schema}")
  expiration_time     = null
  time_partitioning {
    field = each.value.partitioning_field
    type  = each.value.partitioning_type
  }

  labels = {
    env         = var.main.env
    tier        = each.value.tier
    source_data = each.value.data_source
  }
  depends_on = [
    google_bigquery_dataset.bigquery_dataset
  ]
}
