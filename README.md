# Stock Trade Management Program

A Class XII Computer Science school project (2024) upgraded into a browser-based stock portfolio web app. The original CLI code is preserved and credited; the new web app runs on top of it.

Original project report: `docs/original-stock-trade-management-report.pdf`

---

## What Has Been Built

### Original CLI (preserved)
`src/stock_trade_management.py` — the original school project. Connects to MySQL, runs a text menu, and supports:

- Add buy/sell stock records
- View all records, filter by date range
- Overall, stock-wise, industry-wise, period-wise, and monthly profit/loss
- matplotlib industry pie chart and profit/loss line chart

### Web App (new — merged from `feature/html-dashboard`)
A FastAPI + SQLite web dashboard that runs in the browser without needing MySQL.

**`src/web_app.py`** — FastAPI application with routes for:

| Route | What it does |
|-------|-------------|
| `GET /` | Dashboard with summary cards and charts |
| `POST /add` | Add a new trade |
| `POST /delete/{id}` | Delete a trade |
| `GET /export` | Download all trades as CSV |
| `POST /import` | Upload a CSV of trades |
| `POST /load-sample` | Load built-in sample data |
| `GET /switch-user` | Switch between demo user portfolios |

**`src/portfolio_logic.py`** — pure Python calculation library (no database dependency):

- `total_profit_loss` — overall P&L across all trades
- `total_volume` — total money transacted
- `group_profit_loss` — P&L grouped by any field (stock, industry, etc.)
- `monthly_profit_loss` — P&L broken down by month
- `holdings_by_ticker` — net share holdings per ticker
- `portfolio_value` — current market value of open positions
- `best_and_worst` — highest and lowest performing stocks
- `simple_volatility` — standard deviation of a price series
- `linear_forecast` — simple linear regression forecast for next N periods
- `moving_average_signal` — Uptrend / Downtrend / Flat signal from moving averages

**`tests/test_portfolio_logic.py`** — pytest unit tests covering all calculation functions.

**`src/templates/dashboard.html`** + **`src/static/`** — HTML/CSS/JS dashboard with Chart.js charts.

---

## Project Structure

```text
.
├── docs/
│   ├── build-options.md
│   ├── original-stock-trade-management-report.pdf
│   └── upgrade-plan.md
├── src/
│   ├── static/
│   │   ├── dashboard.js        # Chart.js chart rendering
│   │   └── styles.css          # Dashboard styles
│   ├── templates/
│   │   └── dashboard.html      # Main web UI
│   ├── portfolio_logic.py      # Pure Python P&L calculations
│   ├── web_app.py              # FastAPI web application
│   └── stock_trade_management.py  # Original CLI (MySQL)
├── tests/
│   └── test_portfolio_logic.py # pytest unit tests
├── .env.example
├── CREDITS.md
├── README.md
└── requirements.txt
```

---

## Setup & Running

### Web App (recommended — no MySQL needed)

Install dependencies globally:

```bash
pip install fastapi uvicorn jinja2 python-multipart python-dotenv matplotlib mysql-connector-python
```

Copy the env file:

```bash
cp .env.example .env
```

Run the web app:

```bash
uvicorn src.web_app:app --reload
```

Open in browser:

```
http://127.0.0.1:8000
```

The web app uses **SQLite by default** — the database file is created automatically at `data/stock_trade.db`. No MySQL setup needed.

To change the database path, set `SQLITE_DB_PATH` in `.env`.

### Original CLI App (MySQL required)

Set up a MySQL database:

```sql
CREATE DATABASE stock_trade;
```

Fill in MySQL credentials in `.env`:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=stock_trade
```

Run the CLI:

```bash
python src/stock_trade_management.py
```

### Run Tests

```bash
pip install pytest
pytest tests/ -v
```

### Live Market Prices (optional)

By default the web app uses an offline price fallback (deterministic, based on ticker hash) so demos work without internet. To enable live prices:

```bash
pip install yfinance
```

Then set in `.env`:

```
ENABLE_LIVE_PRICES=true
```

---

## What's Next

See `docs/upgrade-plan.md` for the full 6-phase roadmap. Remaining phases:

- **Phase 3** — User authentication, multi-user accounts, watchlist
- **Phase 4** — Real ticker symbols, realized vs. unrealized P&L, Alpha Vantage / yfinance integration
- **Phase 5** — Sector allocation, volatility dashboard, CSV/PDF export, moving averages
- **Phase 6** — AI forecasting, backtesting, model comparison

---

## Collaboration

- Work on feature branches (`feature/...`)
- Keep `main` stable
- Open pull requests before merging
- Add your name to `CREDITS.md`
- Never commit `.env`, passwords, or API keys

## Credits

See `CREDITS.md`.
