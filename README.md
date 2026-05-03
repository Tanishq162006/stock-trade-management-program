# Stock Trade Management Program

This repository preserves and upgrades a high school Computer Science project completed in 2024: a Python and MySQL stock trade management program.

The original version was built as a Class XII Computer Science project for managing stock transactions, calculating profit/loss, filtering records, and showing charts. The current goal is to keep that original work credited and intact while upgrading it into a more complete modern application.

The original project report is stored at:

- `docs/original-stock-trade-management-report.pdf`

## Current Upgrade Plan

Right now, this repo is planned as a collaborative upgrade from the original school project into a browser-based stock portfolio app.

The upgrade direction is:

- Keep the original Python/MySQL CLI project as the foundation.
- Clean up the code structure and calculation logic.
- Build a proper HTML/CSS web dashboard.
- Add a FastAPI backend.
- Add real stock market data support.
- Add portfolio analytics.
- Add experimental AI/forecasting features.

The full roadmap is in:

- `docs/upgrade-plan.md`
- `docs/build-options.md`

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
│   ├── build-options.md
│   ├── original-stock-trade-management-report.pdf
│   └── upgrade-plan.md
├── src/
│   ├── static/
│   ├── templates/
│   ├── web_app.py
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

4. Run the original CLI app:

```bash
python src/stock_trade_management.py
```

5. Run the upgraded web app:

```bash
uvicorn src.web_app:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## Next Build Options

See `docs/build-options.md` for practical ways to build on top of this project, from a small cleanup to a full HTML/CSS web dashboard.

See `docs/upgrade-plan.md` for the full team collaboration plan.

## Collaboration

This repo is intended for teammate collaboration during the upgrade. Contributors should:

- Work on feature branches.
- Keep `main` stable.
- Open pull requests for major changes.
- Add their names to `CREDITS.md`.
- Avoid committing passwords, API keys, `.env` files, or private data.

## Credits

See `CREDITS.md`.
