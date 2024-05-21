resource "google_workflows_workflow" "workflows" {
  for_each        = var.workflow
  name            = each.value.name
  region          = var.main.region
  description     = each.value.description
  service_account = var.main.service_account
  source_contents = templatefile("${each.value.workflow_content}", { project_id = var.main.project_id })
  depends_on      = [google_cloudfunctions2_function.cltv_cf]
}
