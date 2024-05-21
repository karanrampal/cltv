####### MAIN VARIABLES #######
variable "main" {
  type = object({
    project_id           = string
    region               = string
    zone                 = string
    env                  = string
    player_id            = string
    network              = string
    branch_name          = string
    repo_name            = string
    srv_read_access_grp  = string
    dbt_target           = string
    dbt_environment_id   = number
    dbt_project_id       = number
    dbt_cloud_host_url   = string
    dbt_cloud_account_id = number
    service_account      = string

  })
  validation {
    condition     = contains(["dev", "test", "prod"], var.main.env)
    error_message = "Allowed values are dev, test and prod."
  }
}
##############################
variable "dataset" {
  type = map(object({
    dataset_id                 = string
    friendly_name              = string
    description                = string
    delete_contents_on_destroy = bool
    tier                       = string
    data_source                = string
  }))
}

variable "workflow" {
  type = map(object({
    name             = string
    description      = string
    workflow_content = string
  }))
}

variable "bigquery_tables" {
  type = map(object({
    dataset_id          = string
    table_id            = string
    description         = string
    tier                = string
    deletion_protection = bool
    schema              = string
    partitioning_field  = string
    partitioning_type   = string
    data_source         = string
    }
  ))
}

######### MONITORING AND ALERTING VARIABLES ##########

variable "notification_channel" {
  type = map(object({
    display_name  = string
    email_address = string
  }))
}

########## BigQuery Monitoring Variables ##########
variable "bq_component" {
  type = object({
    dashboard_name                  = string
    exe_time_threshold              = number
    rows_uploaded_threshold         = number
    query_exe_count_threshold       = number
    query_count_threshold           = number
    job_count_threshold             = number
    scanned_billed_bytes_threshold  = number
    uploaded_billed_bytes_threshold = number
    exe_time_disable                = bool
    rows_uploaded_disable           = bool
    query_exe_count_disable         = bool
    query_count_disable             = bool
    job_count_disable               = bool
    scanned_billed_disable          = bool
    uploaded_billed_disable         = bool
  })
}

########## Workflow Component Variables ##########
variable "wf_component" {
  type = object({
    dashboard_name                   = string
    execution_time_threshold         = string
    execution_time_disable           = bool
    workflow_start_execution_disable = bool
  })
}

variable "bucket" {
  type = map(object({
    name = string
  }))
}

variable "artifact_regs" {
  type = map(object({
    name = string
  }))
}
