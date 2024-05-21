"""Utility functions"""

import json
import logging
import os
from typing import Optional

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from tqdm import tqdm

from config_manager.manager import Params

RESULTS_PER_PAGE = 10_000


def set_logger(log_path: Optional[str] = None) -> None:
    """Set the logger to log info in terminal and file at log_path.
    Args:
        log_path: (string) location of log file
    """
    for name in ["pymc", "pymc3"]:
        pymc_logger = logging.getLogger(name)
        pymc_logger.propagate = False
        pymc_logger.setLevel(logging.ERROR)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s: %(message)s"))
        logger.addHandler(stream_handler)

        if log_path:
            file_handler = logging.FileHandler(log_path, mode="w")
            file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s: %(message)s"))
            logger.addHandler(file_handler)


def concat_csv_data(out_path: str) -> pd.DataFrame:
    """Concat the list of csv files"""
    csv_files = [f for f in os.listdir(out_path) if f.endswith(".csv")]
    df_list = []
    for csvf in tqdm(csv_files):
        df = pd.read_csv(os.path.join(out_path, csvf))
        if not df.empty:
            df_list.append(df)
    final_df = pd.concat(df_list, ignore_index=True)
    return final_df


def add_meta_data(data: pd.DataFrame) -> pd.DataFrame:
    """Add meta data to dataframe"""
    data["meta_change_timestamp"] = pd.Timestamp.now()
    data["meta_change_by"] = None
    return data


def upload_to_bq(data: pd.DataFrame, confs: Params) -> None:
    """Upload data to BigQuery"""
    credentials = get_credentials(confs.key_file)
    client = bigquery.Client(project=confs.env_name, credentials=credentials)
    table_id = f"{confs.env_name}.customersegment_srv.customer_lifetime_value"

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField(
                "customer_brand_id",
                bigquery.SqlTypeNames.INTEGER,
                description="Customer brand identifier",
            ),
            bigquery.SchemaField(
                "business_partner_id",
                bigquery.SqlTypeNames.INTEGER,
                description="Business partner identifier",
            ),
            bigquery.SchemaField(
                "country_rk", bigquery.SqlTypeNames.STRING, description="Country identifier"
            ),
            bigquery.SchemaField(
                "corporate_brand_rk",
                bigquery.SqlTypeNames.INTEGER,
                description="Corporate brand identifier. 0= H&M",
            ),
            bigquery.SchemaField(
                "currency_rk",
                bigquery.SqlTypeNames.STRING,
                description="Currency identifier.",
            ),
            bigquery.SchemaField(
                "expected_repurchase_rate",
                bigquery.SqlTypeNames.FLOAT,
                description="Expected repurchase probability for a customer",
            ),
            bigquery.SchemaField(
                "expected_revenue",
                bigquery.SqlTypeNames.FLOAT,
                description="Expected customer lifetime revenue for the next 1 year",
            ),
            bigquery.SchemaField(
                "meta_change_timestamp",
                bigquery.SqlTypeNames.TIMESTAMP,
                description="Date/Time when record was updated",
            ),
            bigquery.SchemaField(
                "meta_change_by",
                bigquery.SqlTypeNames.STRING,
                description="Job/User who last changes record it is populated only for manual load",
            ),
        ],
        write_disposition="WRITE_TRUNCATE",
        clustering_fields=["country_rk", "customer_brand_id"],
    )

    job = client.load_table_from_dataframe(
        data,
        table_id,
        job_config=job_config,
    )
    job.result()


def get_credentials(key_file: str) -> service_account.Credentials:
    """Get credentials from secret manager"""
    # creds, _ = google.auth.default(
    #     scopes=["https://www.googleapis.com/auth/cloud-platform"], quota_project_id=proj_name
    # )
    # name = f"projects/{proj_name}/secrets/{secret_name}/versions/latest"
    # secret_client = secretmanager.SecretManagerServiceClient(credentials=creds)

    # response = secret_client.access_secret_version(request={"name": name})
    # sa_info = json.loads(response.payload.data.decode("utf-8"))
    sa_info = json.loads(key_file)
    credentials = service_account.Credentials.from_service_account_info(sa_info)
    return credentials


def convert_currency(confs: Params) -> None:
    """Upload data to BigQuery"""
    credentials = get_credentials(confs.key_file)
    client = bigquery.Client(project=confs.env_name, credentials=credentials)
    table_id = f"{confs.env_name}.customersegment_srv.customer_lifetime_value"
    query = f"""
    UPDATE
        `{table_id}` AS t1
    SET
        t1.expected_revenue = ROUND(t1.expected_revenue * t2.RATE_VALUE, 2),
        t1.currency_rk = 'SEK'
    FROM
        `entstruct-manual-p-7df5.entstruct_manual_srv.currency_rate` AS t2
    WHERE
        t1.currency_rk = t2.currency_code
        AND t2.rate_type_code = 'YB'
        AND t2.date_to = '9999-12-31'
        AND t2.currency_code_to = 'SEK'
    """
    client.query(query.strip()).result()
