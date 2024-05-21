#!/usr/bin/env python
"""KFP components"""

import argparse
import os

import google.cloud.aiplatform as aip
from kfp import compiler, dsl


def args_parser() -> tuple[argparse.Namespace, list[str]]:
    """CLI argument parser"""
    parser = argparse.ArgumentParser(description="CLI arguments parser")
    parser.add_argument(
        "--env-name",
        type=str,
        default="customersegmentation-d-15ad",
        help="Dev, test or prod environment name",
    )
    parser.add_argument("--region", type=str, default="europe-west1", help="Region")
    parser.add_argument(
        "--bucket-name",
        type=str,
        default="customer_lifetime_value_bucket",
        help="Storage bucket",
    )
    parser.add_argument(
        "--cron-sched", type=str, default="Europe/Stockholm 0 17 * * 0", help="Cron schedule"
    )
    parser.add_argument("--run-job", action="store_true", help="Run pipeline job immediately")
    parser.add_argument(
        "--compile-only", action="store_true", help="Only compile pipeline, do not run"
    )
    parser.add_argument("--key-file", type=str, default="", help="Service account json key file")
    return parser.parse_known_args()


@dsl.component(base_image="python:3.10", packages_to_install=["google-cloud-aiplatform"])
def run_cltv(env_name: str, out_dir: str, region: str, img: str, key_file: str) -> None:
    """Run cltv model docker image"""
    # pylint: disable=import-outside-toplevel,reimported
    from google.cloud import aiplatform

    aiplatform.init(project=env_name, staging_bucket=out_dir, location=region)
    custom_training_job = aiplatform.CustomContainerTrainingJob(
        display_name="cltv_model_run", container_uri=img
    )
    _ = custom_training_job.run(
        args=[
            "--env-name",
            env_name,
            "--out-dir",
            out_dir.replace("gs://", "/gcs/"),
            "--key-file",
            key_file,
        ],
        base_output_dir=out_dir,
        replica_count=1,
        machine_type="e2-standard-32",
    )


@dsl.pipeline(name="cltv_pipeline")
def pipeline(
    project_id: str, region: str, bucket_name: str, container_img: str, key_file: str
) -> None:
    """Attribute prediction training pipeline
    Args:
        project_id: Id for the GCP project
        region: Region in GCP
        data_root: Root directory for data images, annotations etc.
    """
    _ = run_cltv(
        env_name=project_id,
        out_dir=bucket_name,
        region=region,
        img=container_img,
        key_file=key_file,
    )


def main() -> None:
    """Main function"""
    args, _ = args_parser()
    args.bucket_name = "gs://" + args.bucket_name
    os.makedirs("./pipelines", exist_ok=True)

    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path="./pipelines/cltv_pipeline.yml",
        # pipeline_parameters={
        #     "project_id": args.env_name,
        #     "region": args.region,
        #     "bucket_name": args.bucket_name,
        #     "container_img": f"europe-west1-docker.pkg.dev/{args.env_name}/api-store/cltv:latest",
        #     "key_file": args.key_file,
        # },
    )

    if args.compile_only:
        return

    aip.init(project=args.env_name, location=args.region)
    pipeline_job = aip.PipelineJob(
        template_path="./pipelines/cltv_pipeline.yml",
        display_name="cltv_pipeline_job",
        pipeline_root=args.bucket_name,
        enable_caching=False,
        parameter_values={
            "project_id": args.env_name,
            "region": args.region,
            "bucket_name": args.bucket_name,
            "container_img": f"europe-west1-docker.pkg.dev/{args.env_name}/api-store/cltv:latest",
            "key_file": args.key_file,
        },
    )
    service_account = f"project-service-account@{args.env_name}.iam.gserviceaccount.com"
    if args.run_job:
        pipeline_job.submit(service_account=service_account)
    else:
        cron = "TZ=" + args.cron_sched
        _ = pipeline_job.create_schedule(
            display_name="cltv_schedule",
            cron=cron,
            max_concurrent_run_count=1,
            max_run_count=1,
            service_account=service_account,
        )


if __name__ == "__main__":
    main()