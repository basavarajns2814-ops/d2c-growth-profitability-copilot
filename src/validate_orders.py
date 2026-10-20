
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ORDERS_FILE = PROJECT_ROOT / "data" / "orders.csv"

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "product",
    "quantity",
    "unit_price",
    "status",
]

VALID_STATUSES = {
    "placed",
    "delivered",
    "cancelled",
    "returned",
    "rto",
}


def validate_orders(file_path, show_report=True):
    if isinstance(file_path, pd.DataFrame):
        df = file_path.copy()
    else:
        df = pd.read_csv(file_path)

    # Check that all required columns exist.
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Check required fields for missing values.
    required_data = [
        "order_id",
        "order_date",
        "product",
        "quantity",
        "unit_price",
        "status",
    ]

    missing_values = df[required_data].isna().sum()

    # Check duplicate order IDs.
    duplicate_ids = df["order_id"].duplicated().sum()

    # Validate numeric fields.
    for column in ["quantity", "unit_price"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    invalid_numbers = df[["quantity", "unit_price"]].isna().sum()

    invalid_amounts = (
        (df["quantity"] <= 0) | (df["unit_price"] < 0)
    ).sum()

    # Check order statuses.
    statuses = df["status"].astype("string").str.strip().str.lower()
    invalid_statuses = (~statuses.isin(VALID_STATUSES)).sum()

    if show_report:
        print("ORDER DATA VALIDATION REPORT")
        print("-" * 30)
        print(f"Total rows: {len(df)}")
        print(f"Missing required values: {missing_values.sum()}")
        print(f"Duplicate order IDs: {duplicate_ids}")
        print(f"Invalid numeric values: {invalid_numbers.sum()}")
        print(f"Invalid quantities/prices: {invalid_amounts}")
        print(f"Invalid statuses: {invalid_statuses}")

    has_errors = (
        missing_values.sum()
        + duplicate_ids
        + invalid_numbers.sum()
        + invalid_amounts
        + invalid_statuses
    ) > 0

    if has_errors:
        if show_report:
            print("\nResult: Data needs investigation.")
        raise ValueError(
            "Order data validation failed. Fix the errors before calculating metrics."
        )

    if show_report:
        print("\nResult: Basic validation passed.")

    return df



if __name__ == "__main__":
    validate_orders(ORDERS_FILE)
