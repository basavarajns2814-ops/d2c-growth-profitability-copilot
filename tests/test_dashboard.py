from pathlib import Path
import sys
from unittest.mock import patch

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import format_inr, process_orders_dataframe, read_uploaded_orders


def test_dashboard_processing_reuses_expected_sample_metrics():
    orders = pd.read_csv(PROJECT_ROOT / "data" / "orders.csv")

    validated_orders, metrics = process_orders_dataframe(orders)

    assert len(validated_orders) == 10
    assert metrics["delivered_sales"] == 6700.0
    assert metrics["placed_gmv"] == 3800.0
    assert metrics["delivered_orders"] == 5
    assert metrics["delivered_aov"] == 1340.0


def test_dashboard_processing_rejects_invalid_data_before_calculation():
    orders = pd.read_csv(PROJECT_ROOT / "data" / "orders_bad.csv")

    with patch("app.calculate_metrics") as calculate_metrics_mock:
        with pytest.raises(ValueError, match="Order data validation failed"):
            process_orders_dataframe(orders)

    calculate_metrics_mock.assert_not_called()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (6700, "₹6,700.00"),
        (1234567, "₹12,34,567.00"),
    ],
)
def test_format_inr_uses_indian_grouping(value, expected):
    assert format_inr(value) == expected


def test_uploaded_orders_are_read_from_file_bytes():
    class UploadedFile:
        name = "orders.csv"

        def getvalue(self):
            return b"order_id,quantity\nORD001,1\n"

    orders = read_uploaded_orders(UploadedFile())

    assert orders.to_dict("records") == [{"order_id": "ORD001", "quantity": 1}]


def test_dashboard_renders_expected_sample_kpis():
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=15)

    assert len(app.exception) == 0
    assert [metric.value for metric in app.metric] == [
        "10",
        "5",
        "₹6,700.00",
        "₹3,800.00",
        "₹1,340.00",
    ]


def test_dashboard_does_not_render_kpis_for_corrupted_upload():
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=15)
    app.radio[0].set_value("Upload a CSV").run(timeout=15)
    corrupted_csv = (PROJECT_ROOT / "data" / "orders_bad.csv").read_bytes()
    app.file_uploader[0].upload(
        "orders_bad.csv",
        corrupted_csv,
        "text/csv",
    ).run(timeout=15)

    assert len(app.exception) == 0
    assert len(app.error) == 1
    assert "Order data validation failed" in app.error[0].value
    assert len(app.metric) == 0
