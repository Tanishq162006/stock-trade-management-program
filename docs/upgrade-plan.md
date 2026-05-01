# Upgrade Plan

Goal: upgrade the original Stock Trade Management Program into a complete portfolio-ready web app while preserving the school project history and crediting the original team.

This plan covers all six upgrade areas:

1. Clean CLI version
2. HTML/CSS web dashboard
3. Full web app
4. Real stock market data
5. Analytics upgrade
6. AI/forecasting upgrade

## Collaboration Rules

- Keep `main` stable.
- Create a branch for each upgrade area.
- Open pull requests before merging.
- Credit contributors in `CREDITS.md`.
- Do not commit `.env`, passwords, API keys, database dumps, or private notes.
- Keep the original PDF in `docs/original-stock-trade-management-report.pdf`.

Suggested branch names:

- `feature/cli-cleanup`
- `feature/html-dashboard`
- `feature/full-web-app`
- `feature/market-data`
- `feature/analytics`
- `feature/forecasting`

## Phase 1: Clean CLI Version

Purpose: make the current Python program reliable before building over it.

Tasks:

- Separate database logic from menu/input logic.
- Add validation for dates, buy/sell values, prices, and quantities.
- Add CSV import/export.
- Add sample seed data.
- Add unit tests for profit/loss calculations.
- Add a simple setup command or script.

Deliverables:

- Cleaner CLI code
- Test coverage for calculations
- Updated README setup instructions

Suggested owner: one teammate.

## Phase 2: HTML/CSS Web Dashboard

Purpose: replace the command-line interface with a browser UI.

Tasks:

- Create FastAPI backend routes.
- Create HTML pages for dashboard, trades, reports, and settings.
- Create CSS design system for layout, buttons, forms, tables, and charts.
- Add JavaScript for filters and chart updates.
- Use Chart.js for charts.
- Add trade create/read/update/delete screens.

Pages:

- Dashboard
- Trade list
- Add/edit trade
- Industry report
- Stock report
- Monthly report

Deliverables:

- Browser-based app
- HTML/CSS UI
- Working chart views

Suggested owner: one teammate for backend, one teammate for frontend.

## Phase 3: Full Web App

Purpose: turn the dashboard into a real multi-user app.

Tasks:

- Add login/signup.
- Add user-specific portfolios.
- Add portfolio table.
- Add watchlist.
- Add edit/delete trade actions.
- Add account settings.
- Add database migrations.
- Add error pages and empty states.

Recommended stack:

- FastAPI
- Jinja templates or simple HTML pages
- CSS
- JavaScript
- SQLAlchemy
- MySQL or PostgreSQL

Deliverables:

- Multi-user app
- Authenticated dashboard
- User-specific data

Suggested owner: backend-focused teammate.

## Phase 4: Real Stock Market Data

Purpose: compare recorded trades against current or historical market prices.

Tasks:

- Add ticker symbols to stock records.
- Add market data provider integration.
- Pull latest prices.
- Pull historical prices.
- Calculate current portfolio value.
- Calculate realized and unrealized profit/loss.
- Add API key settings through environment variables.

Possible providers:

- Yahoo Finance via `yfinance`
- Alpha Vantage
- Twelve Data

Deliverables:

- Current prices
- Historical price lookup
- Realized/unrealized profit/loss

Suggested owner: data/API-focused teammate.

## Phase 5: Analytics Upgrade

Purpose: add useful portfolio analysis beyond basic profit/loss.

Tasks:

- Sector/industry allocation.
- Monthly and yearly performance.
- Best and worst performing stocks.
- Moving averages.
- Volatility.
- Portfolio concentration.
- CSV/PDF report export.

Charts:

- Portfolio value over time
- Profit/loss by industry
- Monthly profit/loss
- Allocation pie chart
- Stock performance line chart

Deliverables:

- Analytics dashboard
- Exportable reports
- Clear visual summaries

Suggested owner: frontend/data teammate.

## Phase 6: AI/Forecasting Upgrade

Purpose: add experimental forecasting and strategy testing.

Tasks:

- Add historical price dataset.
- Add moving-average strategy signals.
- Add simple forecasting model.
- Add backtesting page.
- Show forecast confidence clearly.
- Label forecasts as educational/experimental, not financial advice.

Possible models:

- Moving average baseline
- Linear regression
- Random forest regression
- ARIMA or Prophet later, only if needed

Deliverables:

- Forecast chart
- Backtesting results
- Strategy comparison page

Suggested owner: teammate interested in ML/data science.

## First Milestone

Build this first:

- FastAPI app shell
- HTML/CSS dashboard
- Trades table
- Add trade form
- Overall profit/loss card
- Industry pie chart
- README run instructions

This gives the team a usable web app quickly and creates a base for the remaining upgrades.

## Suggested Task Split

Person 1:

- FastAPI setup
- Database models
- API routes
- Auth later

Person 2:

- HTML pages
- CSS styling
- Dashboard layout
- JavaScript chart wiring

Person 3:

- Market data
- Analytics formulas
- Forecasting experiments
- Test data

## Definition of Done

Each phase is done when:

- The app runs from README instructions.
- No secrets are committed.
- Main workflows are tested manually.
- Any calculation logic has tests.
- `CREDITS.md` includes every contributor.
