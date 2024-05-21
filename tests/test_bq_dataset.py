"""Unit tests for BQ dataset class"""

import pytest
from pytest_mock import MockerFixture

from dataloader.bq_dataset import BQDataset


def test_bq_file_read(mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
    """Test if BQ client is called appropriately"""
    mocked_open = mocker.mock_open(read_data="")
    mocker.patch("builtins.open", mocked_open)

    bqd = BQDataset()
    data = bqd.get_feats("fake", "more fake data")

    assert "Returning none as query is empty!" in caplog.text
    assert not data
