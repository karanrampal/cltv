"""Cloud function to trigger Kubeflow pipeline"""

import os

import flask
import functions_framework
import google.cloud.aiplatform as aip


@functions_framework.http
def trigger_pipeline_run(request: flask.Request) -> str:
    """HTTP Cloud Function to trigger kfp pipeline run
    Args:
        request: The request object.
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
    """
    request_json = request.get_json(silent=True)

    if request_json is None:
        return "JSON is invalid, or missing"
    env_name = request_json["env_name"]
    region = request_json["region"]
    bucket_name = "gs://" + request_json["bucket_name"]
    key_file = request_json["key_file"]
    path_ = os.path.join(bucket_name, "cltv_pipeline.yml")

    aip.init(project=env_name, location=region)
    pipeline_job = aip.PipelineJob(
        template_path=path_,
        display_name="cltv_pipeline_job",
        pipeline_root=bucket_name,
        enable_caching=False,
        parameter_values={
            "project_id": env_name,
            "region": region,
            "bucket_name": bucket_name,
            "container_img": f"europe-west1-docker.pkg.dev/{env_name}/api-store/cltv:latest",
            "key_file": key_file,
        },
    )

    service_account = f"project-service-account@{env_name}.iam.gserviceaccount.com"
    pipeline_job.submit(service_account=service_account)

    return pipeline_job.name
