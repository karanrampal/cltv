#!/usr/bin/env python3
"""Script to run CLTV model"""

import argparse
import logging
import os
import time

from config_manager.manager import Params
from dataloader.bq_dataset import BQDataset
from models.cltv import run_batched_mt
from utils.utils import (
    add_meta_data,
    concat_csv_data,
    convert_currency,
    set_logger,
    upload_to_bq,
)


def args_parser() -> tuple[argparse.Namespace, list[str]]:
    """CLI argument parser"""
    parser = argparse.ArgumentParser(description="CLTV cli arguments parser")
    parser.add_argument(
        "--env-name",
        type=str,
        default="customersegmentation-d-15ad",
        help="Dev, test or prod environment dataset name",
    )
    parser.add_argument("--out-dir", type=str, default="./output", help="Output directory")
    parser.add_argument(
        "--num-workers",
        type=int,
        default=(os.cpu_count() or 2) - 1,
        help="Number of workers to use",
    )
    parser.add_argument("--key-file", type=str, default="", help="Service account json key file")
    parser.add_argument("--cores", type=int, default=1, help="Number of cores to use")
    parser.add_argument("--chains", type=int, default=2, help="Number of chains")
    parser.add_argument("--draws", type=int, default=64, help="Number of sample draws")
    parser.add_argument("--tune", type=int, default=4, help="Number of tuning draws")
    parser.add_argument("--time-step", type=int, default=8, help="Number of timesteps")
    return parser.parse_known_args()


def main() -> None:
    """Main function"""
    set_logger()

    args, _ = args_parser()
    confs = Params(vars(args))
    logging.info("Config: %s", confs)

    bqd = BQDataset()
    feats_iter = bqd.get_feats(env_name=confs.env_name, key_file=confs.key_file)

    tmp = os.path.join(confs.out_dir, f"run_{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(tmp, exist_ok=True)
    output_file = os.path.join(tmp, "cltv.csv")
    if feats_iter:
        run_batched_mt(confs, feats_iter, output_file)
        logging.info("Concatenating csv files.")
        final_df = concat_csv_data(tmp)
        final_df = add_meta_data(final_df)
        logging.info("Uploading data to BigQuery.")
        upload_to_bq(final_df, confs)
        logging.info("Converting currency.")
        convert_currency(confs)
    else:
        logging.error("Model could not be run as no data!")


if __name__ == "__main__":
    main()
