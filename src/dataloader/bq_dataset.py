"""Create a dataloader and dataset for bigquery table"""

import logging
import os
from typing import Optional

from google.cloud import bigquery

from utils.utils import RESULTS_PER_PAGE, get_credentials


class BQDataset:
    """Create dataset for BigQuery customer_sales_order_tmp table, given the environment"""

    def __init__(self) -> None:
        pass

    def read_query_file(self, env_name: str) -> str:
        """Read query from txt file"""
        logging.info("Reading query file.")

        try:
            path_ = os.path.join(os.path.dirname(__file__), "query.txt")
            with open(path_, "r", encoding="utf-8") as fptr:
                query = fptr.read()
            table_name = f"`{env_name}.customersegment_trf.customer_sales_order_tmp`"
            query = query.replace("__table_name__", table_name)
        except FileNotFoundError:
            logging.error("File not found exception occured!", exc_info=True)
            query = ""
        return query

    def get_feats(self, env_name: str, key_file: str) -> Optional[bigquery.table.RowIterator]:
        """Get rfm features from bq table"""
        query = self.read_query_file(env_name)
        if not query:
            logging.error("Returning none as query is empty!")
            return None

        logging.info("Executing query in BQ.")
        credentials = get_credentials(key_file)
        client = bigquery.Client(project=env_name, credentials=credentials)
        res = client.query(query).result(page_size=RESULTS_PER_PAGE)
        return res