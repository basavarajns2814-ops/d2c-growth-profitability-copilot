from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from validate_orders import validate_orders


def test_validate_orders_returns_clean_sample_data():
    orders = validate_orders(PROJECT_ROOT / "data" / "orders.csv")

    assert len(orders) == 10
    assert orders["order_id"].is_unique


def test_validate_orders_rejects_corrupted_sample_data():
    with pytest.raises(ValueError, match="Order data validation failed"):
        validate_orders(PROJECT_ROOT / "data" / "orders_bad.csv")
