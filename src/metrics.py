
from pathlib import Path

from validate_orders import validate_orders


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ORDERS_FILE = PROJECT_ROOT / "data" / "orders.csv"


def calculate_metrics(df):
    # Calculate the value of each order row.
    df = df.copy()
    df["row_value"] = df["quantity"] * df["unit_price"]

    # Count rows by order status.
    status_counts = df["status"].value_counts().to_dict()

    # Calculate sales using our initial prototype rules.
    delivered_sales = df.loc[
        df["status"] == "delivered", "row_value"
    ].sum()

    placed_gmv = df.loc[
        df["status"] == "placed", "row_value"
    ].sum()

    delivered_orders = df.loc[
        df["status"] == "delivered", "order_id"
    ].nunique()

    delivered_aov = (
        delivered_sales / delivered_orders
        if delivered_orders > 0
        else 0
    )

    return {
        "total_order_rows": len(df),
        "status_counts": status_counts,
        "delivered_sales": float(delivered_sales),
        "placed_gmv": float(placed_gmv),
        "delivered_orders": int(delivered_orders),
        "delivered_aov": float(delivered_aov),
    }


def run_metrics(file_path=ORDERS_FILE):
    orders = validate_orders(file_path)
    return calculate_metrics(orders)


if __name__ == "__main__":
    metrics = run_metrics()

    print("D2C METRICS REPORT")
    print("-" * 30)

    for metric, value in metrics.items():
        print(f"{metric}: {value}")
