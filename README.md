# D2C Growth & Profitability Copilot

A Python project for analyzing direct-to-consumer (D2C) order data. Its
Streamlit dashboard validates order CSV files and presents order and sales
metrics with interactive charts.

## Implemented features

- Validates required order columns, missing values, duplicate order IDs,
  quantities, prices, and supported order statuses.
- Loads the included synthetic sample dataset or accepts a CSV upload processed
  in memory.
- Calculates total order rows, status counts, delivered sales, placed-order GMV,
  delivered order count, and delivered AOV.
- Displays key metrics using Indian rupee formatting, Plotly charts, and a
  preview of validated orders.
- Provides a command-line metrics pipeline and automated tests.

The sample dataset currently produces:

| Metric | Result |
| --- | ---: |
| Delivered sales | ₹6,700 |
| Placed-order GMV | ₹3,800 |
| Delivered orders | 5 |
| Delivered AOV | ₹1,340 |

Placed-order GMV is not realized revenue.

## Technology stack

- Python
- Streamlit
- pandas
- Plotly
- pytest

## Project structure

```text
D2C-Copilot/
├── app.py                   # Streamlit dashboard
├── data/
│   ├── orders.csv           # Clean synthetic sample data
│   └── orders_bad.csv       # Intentionally invalid synthetic test data
├── reports/                 # Reserved for reports
├── requirements.txt         # Direct runtime and test dependencies
├── src/
│   ├── metrics.py           # Metrics calculations and CLI entry point
│   └── validate_orders.py   # Order CSV/DataFrame validation
└── tests/
    ├── test_dashboard.py
    ├── test_metrics.py
    └── test_validate_orders.py
```

## Windows setup

From the project directory in PowerShell, create and activate a virtual
environment, then install the listed dependencies:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents virtual-environment activation, run the commands below
using `.venv\Scripts\python.exe` directly.

## Run the dashboard

From the project directory:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit. Choose **Sample dataset** or upload an
order CSV. Invalid data produces a validation error; financial metrics are not
shown for invalid data.

## Run the metrics CLI

```powershell
.\.venv\Scripts\python.exe src\metrics.py
```

## Run the tests

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The latest verified test run had **13 passing tests**.

## Future plans (not implemented)

The current project does not implement a React frontend, FastAPI backend,
PostgreSQL database, or AI-generated insights. These are future possibilities,
not part of the current technology stack or functionality.
