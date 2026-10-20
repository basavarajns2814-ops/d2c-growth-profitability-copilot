
from pathlib import Path
import sys
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from metrics import calculate_metrics
from metrics import run_metrics


def test_metrics_from_sample_orders():
    orders = pd.read_csv(PROJECT_ROOT / "data" / "orders.csv")

    result = calculate_metrics(orders)

    assert result["total_order_rows"] == 10
    assert result["status_counts"] == {
        "delivered": 5,
        "placed": 2,
        "cancelled": 1,
        "rto": 1,
        "returned": 1,
    }
    assert result["delivered_sales"] == 6700.0
    assert result["placed_gmv"] == 3800.0
    assert result["delivered_orders"] == 5
    assert result["delivered_aov"] == 1340.0

def test_metrics_when_no_orders_are_delivered():
    orders = pd.DataFrame({
        "order_id": ["ORD101", "ORD102"],
        "quantity": [1, 2],
        "unit_price": [500, 800],
        "status": ["placed", "cancelled"],
    })

    result = calculate_metrics(orders)

    assert result["delivered_sales"] == 0.0
    assert result["delivered_orders"] == 0
    assert result["delivered_aov"] == 0


def test_metrics_pipeline_validates_and_calculates_clean_sample():
    result = run_metrics(PROJECT_ROOT / "data" / "orders.csv")

    assert result["delivered_sales"] == 6700.0
    assert result["placed_gmv"] == 3800.0
    assert result["delivered_orders"] == 5
    assert result["delivered_aov"] == 1340.0


def test_metrics_pipeline_stops_before_calculation_for_invalid_data():
    from unittest.mock import patch

    with patch("metrics.calculate_metrics") as calculate_metrics_mock:
        with pytest.raises(ValueError, match="Order data validation failed"):
            run_metrics(PROJECT_ROOT / "data" / "orders_bad.csv")

    calculate_metrics_mock.assert_not_called()
