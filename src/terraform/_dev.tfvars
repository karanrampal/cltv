main = {
  project_id           = "customersegmentation-d-15ad"
  region               = "europe-west1"
  zone                 = "europe-west1-c"
  env                  = "dev"
  player_id            = "customersegmentation"
  network              = "vpc-network-name"
  repo_name            = "customersegmentation-dbt"
  srv_read_access_grp  = "customersegment-srv-read-access@gmail.com"
  branch_name          = "development"
  dbt_target           = "development"
  dbt_environment_id   = 6042
  dbt_project_id       = 3401
  dbt_cloud_host_url   = "https://emea.dbt.com/api"
  dbt_cloud_account_id = 68
  service_account      = "project-service-account@customersegmentation-d-15ad.iam.gserviceaccount.com"
}


dataset = {
  adm_metadata = {
    dataset_id                 = "adm_metadata"
    friendly_name              = "metadata_dataset"
    description                = "Dataset for Metadata and reference tables"
    delete_contents_on_destroy = false
    tier                       = "adm"
    data_source                = "metadata"
  },
  customersegmentation_srv = {
    dataset_id                 = "customersegment_srv"
    friendly_name              = "customersegment_srv"
    description                = "Dataset for serve table"
    delete_contents_on_destroy = false
    tier                       = "srv"
    data_source                = "serve"
  },
  customersegmentation_trf = {
    dataset_id                 = "customersegment_trf"
    friendly_name              = "customersegment_trf"
    description                = "Dataset for staging table"
    delete_contents_on_destroy = false
    tier                       = "trf"
    data_source                = "transform"
  },

workflow = {
  wkf_customer_lifetime_value_load = {
    name             = "wkf_customer_lifetime_value_load"
    description      = "wkf_customer_lifetime_value_load"
    workflow_content = "../../src/workflow/wkf_cltv.yaml"
  }
}

srv_roles_acess          = ["roles/bigquery.dataViewer", "roles/bigquery.user"]
project_maintenance_role = ["roles/viewer", "roles/monitoring.admin", "roles/workflows.invoker", "roles/cloudscheduler.jobRunner", "roles/dataflow.viewer", "roles/run.viewer"]

########## SRE Workflow Component Inputs ##########
#wf_component = {
#  dashboard_name                   = "CUSTOMER_CUST_SAPCRM_WORKFLOW_DASHBOARD"
#  execution_time_threshold         = 1000000
#  execution_time_disable           = true
#  workflow_start_execution_disable = false
#}

notification_channel = {
  devloper_channel = {
    display_name  = "devloper_channel"
    email_address = "karanrampal87@gmail.com"
  },
}

########## SRE BQ Component Inputs ##########
bq_component = {
  dashboard_name     = "CUSTOMER_SEGMENTATIONS_SRE_BIGQUERY_DASHBOARD"
  exe_time_threshold = 3600000
  exe_time_disable   = false

  rows_uploaded_threshold = 1000000
  rows_uploaded_disable   = false

  query_exe_count_threshold = 20
  query_exe_count_disable   = false

  query_count_threshold = 20
  query_count_disable   = false

  job_count_threshold = 10
  job_count_disable   = false

  scanned_billed_bytes_threshold = 10000000000000
  scanned_billed_disable         = false

  uploaded_billed_bytes_threshold = 10000000000000
  uploaded_billed_disable         = false
}

bucket = {
  customer_lifetime_value = {
    name = "customer_lifetime_value"
  }
}

artifact_regs = {
  cltv_artifact_reg = {
    name = "api-store"
  },
}
