"""CLTV model"""

import concurrent.futures as cf
import logging
import math
from typing import Optional

import pandas as pd
from google.cloud import bigquery
from pymc_marketing import clv
from tqdm import tqdm

from config_manager.manager import Params
from utils.utils import RESULTS_PER_PAGE


class CLTV:
    """Calculate the customer lifetime value metrics"""

    @classmethod
    def build_model(
        cls, confs: Params, data: pd.DataFrame
    ) -> tuple[clv.BetaGeoModel, clv.GammaGammaModel]:
        """Initialise model"""
        sampler_config = {
            "tune": confs.tune,
            "draws": confs.draws,
            "chains": confs.chains,
            "cores": confs.cores,
            "progressbar": False,
        }
        bgm = clv.BetaGeoModel(data=data, sampler_config=sampler_config)
        bgm.build_model()

        gg = clv.GammaGammaModel(data=data, sampler_config=sampler_config)
        gg.build_model()
        return bgm, gg

    @classmethod
    def fit_predict(
        cls, bgm: clv.BetaGeoModel, gg: clv.GammaGammaModel, data: pd.DataFrame, time_step: int
    ) -> pd.DataFrame:
        """Fit model and predict on test set"""
        bgm.fit()
        p_alive = bgm.expected_probability_alive(
            customer_id=data["customer_id"],
            frequency=data["frequency"],
            recency=data["recency"],
            T=data["T"],
        )
        res1 = p_alive.mean(["chain", "draw"]).to_pandas().round(2)

        gg.fit()
        clv_res = gg.expected_customer_lifetime_value(
            transaction_model=bgm,
            customer_id=data["customer_id"],
            mean_transaction_value=data["mean_transaction_value"],
            frequency=data["frequency"],
            recency=data["recency"],
            T=data["T"],
            time=time_step,
            discount_rate=0.01,
            freq="W",
        )
        res2 = clv_res.mean(["chain", "draw"]).to_pandas().round(2)

        res = pd.concat(
            [
                data.set_index("customer_id")[
                    ["business_partner_id", "country_rk", "corporate_brand_rk", "currency_rk"]
                ],
                res1.rename("expected_repurchase_rate"),
                res2.rename("expected_revenue"),
            ],
            axis=1,
        )
        res = res.drop(res[res.expected_revenue < 0.0].index)
        return res.reset_index().rename(columns={"customer_id": "customer_brand_id"})

    @classmethod
    def run_step(
        cls, confs: Params, data: pd.DataFrame, file_name: str, batch_num: Optional[int] = None
    ) -> None:
        """One iteration of run_batched"""
        data.recency = pd.to_timedelta(data.recency, "D") / pd.Timedelta(1, "W")
        data["T"] = pd.to_timedelta(data["T"], "D") / pd.Timedelta(1, "W")

        bgm, gg = cls.build_model(confs, data)
        res = cls.fit_predict(bgm, gg, data, confs.time_step)
        if batch_num is None:
            res.to_csv(file_name, mode="a", index=False)
        else:
            res.to_csv(file_name[:-4] + "_" + str(batch_num) + file_name[-4:], index=False)

    @classmethod
    def run_batched(
        cls, confs: Params, res_iter: bigquery.table.RowIterator, file_name: str
    ) -> None:
        """Run in batched mode"""
        tot = math.ceil(res_iter.total_rows / RESULTS_PER_PAGE)
        logging.info("Model prediction.")
        for data in tqdm(res_iter.to_dataframe_iterable(), total=tot, unit="pages"):
            cls.run_step(confs, data, file_name, None)


def run_batched_mt(confs: Params, res_iter: bigquery.table.RowIterator, file_name: str) -> None:
    """Run batched in multi-threaded executor"""
    tot = math.ceil(res_iter.total_rows / RESULTS_PER_PAGE)
    logging.info("Total pages: %d, Results per page: %d", tot, RESULTS_PER_PAGE)
    logging.info("Model prediction.")
    with tqdm(total=tot, unit="pages") as pbar:
        with cf.ProcessPoolExecutor(max_workers=confs.num_workers) as tpe:
            results = [
                tpe.submit(CLTV.run_step, confs, data, file_name, i)  # type: ignore[arg-type]
                for i, data in enumerate(res_iter.to_dataframe_iterable())
            ]
            for _ in cf.as_completed(results):
                pbar.update(1)