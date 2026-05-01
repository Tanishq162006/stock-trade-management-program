# Build Options

These are practical ways to build over the original Stock Trade Management Program.

## Option 1: Clean CLI App

Best for: keeping the project close to the school submission while making it reliable.

What to build:

- Input validation for dates, buy/sell values, prices, and quantities
- Better profit/loss formulas
- CSV import and export
- Safer database credentials through `.env`
- Unit tests for calculations

Estimated effort: low.

## Option 2: Streamlit Dashboard

Best for: quickly turning the project into a visual app.

What to build:

- Upload CSV of trades
- Interactive filters by stock, industry, and date
- Profit/loss charts
- Portfolio summary cards
- Exportable reports

Estimated effort: medium.

Recommended stack:

- Python
- Streamlit
- Pandas
- MySQL or SQLite
- Plotly

## Option 3: Full Web App

Best for: a stronger portfolio project.

What to build:

- Login/signup
- Trade entry form
- Portfolio dashboard
- Watchlist
- Real-time or delayed market prices
- User-specific portfolios
- API backend

Estimated effort: high.

Recommended stack:

- FastAPI backend
- React or Next.js frontend
- PostgreSQL
- SQLAlchemy
- Plotly/Recharts

## Option 4: Data Science Upgrade

Best for: expanding the project toward analytics.

What to build:

- Historical stock price import
- Moving averages
- Volatility analysis
- Sector allocation
- Basic forecasting model
- Backtesting of buy/sell strategies

Estimated effort: medium to high.

Recommended stack:

- Python
- Pandas
- NumPy
- scikit-learn
- yfinance
- matplotlib or Plotly

## Recommended Path

Start with Option 1, then move to Option 2. This keeps the original project recognizable while making it more useful and easier to demo.
