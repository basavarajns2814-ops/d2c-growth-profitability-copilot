from io import BytesIO
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
ORDERS_FILE = PROJECT_ROOT / "data" / "orders.csv"
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from metrics import calculate_metrics
from validate_orders import validate_orders


def process_orders_dataframe(df):
    validated_orders = validate_orders(df, show_report=False)
    metrics = calculate_metrics(validated_orders)
    return validated_orders, metrics


def read_uploaded_orders(uploaded_file):
    return pd.read_csv(BytesIO(uploaded_file.getvalue()))


def format_inr(value):
    formatted = f"{value:,.2f}"
    whole, decimals = formatted.split(".")
    digits = whole.replace(",", "")

    if len(digits) <= 3:
        indian_grouping = digits
    else:
        last_group = digits[-3:]
        leading_digits = digits[:-3]
        groups = []
        while leading_digits:
            groups.insert(0, leading_digits[-2:])
            leading_digits = leading_digits[:-2]
        indian_grouping = ",".join(groups + [last_group])

    return f"₹{indian_grouping}.{decimals}"


def main():
    st.set_page_config(
        page_title="D2C Growth & Profitability Copilot",
        page_icon="📊",
        layout="wide",
    )
    st.title("D2C Growth & Profitability Copilot")
    st.write(
        "Analyze your direct-to-consumer order data with clear sales, order, "
        "and status insights."
    )

    st.header("Order data")
    data_source = st.radio(
        "Choose your data source",
        ["Sample dataset", "Upload a CSV"],
        horizontal=True,
    )

    if data_source == "Sample dataset":
        try:
            orders = pd.read_csv(ORDERS_FILE)
            source_description = "Sample dataset"
        except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError, OSError) as exc:
            st.error(
                "Could not read the sample CSV. Check that the file exists and "
                f"contains valid CSV data. Details: {exc}"
            )
            return
    else:
        uploaded_file = st.file_uploader(
            "Upload an order-data CSV",
            type=["csv"],
            help="Your file is processed in memory and is not saved.",
        )
        if uploaded_file is None:
            st.info("Upload a CSV file to view your order insights.")
            return
        try:
            orders = read_uploaded_orders(uploaded_file)
            source_description = uploaded_file.name
        except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError, OSError) as exc:
            st.error(
                "Could not read this CSV file. Check its format and try again. "
                f"Details: {exc}"
            )
            return

    try:
        validated_orders, metrics = process_orders_dataframe(orders)
    except ValueError:
        st.error(
            "Order data validation failed. Check that the CSV has all required "
            "columns, no missing required values or duplicate order IDs, "
            "positive quantities, non-negative prices, and supported statuses."
        )
        return

    st.success(f"Data validation passed for {source_description}.")
    st.header("Key performance indicators")

    kpi_columns = st.columns(5)
    kpi_columns[0].metric("Total order rows", metrics["total_order_rows"])
    kpi_columns[1].metric("Delivered orders", metrics["delivered_orders"])
    kpi_columns[2].metric("Delivered sales", format_inr(metrics["delivered_sales"]))
    kpi_columns[3].metric("Placed-order GMV", format_inr(metrics["placed_gmv"]))
    kpi_columns[4].metric("Delivered AOV", format_inr(metrics["delivered_aov"]))

    st.header("Order and sales insights")
    chart_columns = st.columns(2)

    status_data = pd.DataFrame(
        {
            "Order status": list(metrics["status_counts"].keys()),
            "Order rows": list(metrics["status_counts"].values()),
        }
    )
    status_chart = px.bar(
        status_data,
        x="Order status",
        y="Order rows",
        title="Order-status distribution",
        text="Order rows",
    )
    status_chart.update_layout(yaxis_title="Number of order rows")
    chart_columns[0].plotly_chart(status_chart, width="stretch")

    sales_data = pd.DataFrame(
        {
            "Sales measure": ["Delivered sales", "Placed-order GMV"],
            "Amount (₹)": [metrics["delivered_sales"], metrics["placed_gmv"]],
        }
    )
    sales_chart = px.bar(
        sales_data,
        x="Sales measure",
        y="Amount (₹)",
        title="Delivered sales vs placed-order GMV",
        text="Amount (₹)",
    )
    sales_chart.update_layout(yaxis_title="Amount (₹)")
    chart_columns[1].plotly_chart(sales_chart, width="stretch")
    st.caption(
        "Placed-order GMV represents orders with a placed status; it is not "
        "realized revenue."
    )

    st.header("Validated order preview")
    st.caption(f"Showing up to 10 of {len(validated_orders)} validated rows.")
    st.dataframe(
        validated_orders.head(10),
        width="stretch",
        hide_index=True,
    )


if __name__ == "__main__":
    main()
