# Stock Trade Management Program

This repository preserves and modernizes a high school Computer Science project: a Python and MySQL stock trade management program.

The original project report is stored at:

- `docs/original-stock-trade-management-report.pdf`

## What It Does

The app tracks stock transactions and supports:

- Adding buy/sell stock records
- Viewing all stock records
- Filtering records by date range
- Calculating overall profit/loss
- Calculating stock-wise, industry-wise, period-wise, and monthly profit/loss
- Showing stocks by industry
- Plotting industry profit/loss
- Showing an industry profit pie chart

## Project Structure

```text
.
├── docs/
│   ├── original-stock-trade-management-report.pdf
│   └── build-options.md
├── src/
│   └── stock_trade_management.py
├── .env.example
├── CREDITS.md
├── README.md
└── requirements.txt
```

## Setup

1. Create a MySQL database:

```sql
CREATE DATABASE stock_trade;
```

2. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update your MySQL settings.

4. Run the app:

```bash
python src/stock_trade_management.py
```

## Next Build Options

See `docs/build-options.md` for practical ways to build on top of this project, from a small cleanup to a full web dashboard.

## Credits

See `CREDITS.md`.
