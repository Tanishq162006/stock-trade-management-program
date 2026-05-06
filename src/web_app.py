from __future__ import annotations

import csv
import io
import os
import sqlite3
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .portfolio_logic import (
    best_and_worst,
    group_profit_loss,
    holdings_by_ticker,
    linear_forecast,
    monthly_profit_loss,
    moving_average_signal,
    portfolio_value,
    simple_volatility,
    total_profit_loss,
    total_volume,
)


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = Path(os.getenv("SQLITE_DB_PATH", DATA_DIR / "stock_trade.db"))
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Stock Trade Management")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def setup_database() -> None:
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stock_name TEXT NOT NULL,
                ticker TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                trade_type TEXT NOT NULL CHECK(trade_type IN ('Buy', 'Sell')),
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                industry TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO users (user_id, name, email) VALUES (1, 'Demo User', 'demo@example.com')"
        )


@app.on_event("startup")
def startup() -> None:
    setup_database()


def current_user_id(request: Request) -> int:
    raw_user_id = request.cookies.get("stock_user_id")
    if raw_user_id and raw_user_id.isdigit():
        return int(raw_user_id)
    return 1


def get_user(user_id: int) -> dict:
    with connect() as connection:
        row = connection.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    return dict(row) if row else {"user_id": 1, "name": "Demo User", "email": "demo@example.com"}


def list_trades(user_id: int) -> list[dict]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT * FROM trades
            WHERE user_id = ?
            ORDER BY trade_date DESC, trade_id DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def validate_trade(trade_date: str, trade_type: str, price: float, quantity: int) -> str | None:
    try:
        date.fromisoformat(trade_date)
    except ValueError:
        return "Trade date must use YYYY-MM-DD."
    if trade_type not in {"Buy", "Sell"}:
        return "Trade type must be Buy or Sell."
    if price <= 0:
        return "Price must be positive."
    if quantity <= 0:
        return "Quantity must be positive."
    return None


def price_for_ticker(ticker: str) -> float:
    ticker = ticker.upper()
    if os.getenv("ENABLE_LIVE_PRICES", "false").lower() == "true":
        try:
            import yfinance as yf

            history = yf.Ticker(ticker).history(period="5d", timeout=3)
            if not history.empty:
                return float(history["Close"].dropna().iloc[-1])
        except Exception:
            pass

    # Offline deterministic fallback so classroom demos work without an API key.
    return round(75 + (sum(ord(char) for char in ticker) % 180) * 1.35, 2)


def market_prices(trades: list[dict]) -> dict[str, float]:
    tickers = sorted({trade["ticker"].upper() for trade in trades})
    return {ticker: price_for_ticker(ticker) for ticker in tickers}


def stock_price_points(trades: list[dict], ticker: str) -> list[float]:
    rows = [trade for trade in trades if trade["ticker"].upper() == ticker.upper()]
    rows.sort(key=lambda trade: trade["trade_date"])
    return [float(trade["price"]) for trade in rows]


def money(value) -> str:
    amount = float(value or 0)
    prefix = "-" if amount < 0 else ""
    return f"{prefix}Rs.{abs(amount):,.2f}"


def dashboard_context(request: Request, message: str | None = None, error: str | None = None) -> dict:
    user_id = current_user_id(request)
    user = get_user(user_id)
    trades = list_trades(user_id)
    prices = market_prices(trades)
    holdings = list(holdings_by_ticker(trades).values())
    stock_rows = group_profit_loss(trades, "stock_name")
    industry_rows = group_profit_loss(trades, "industry")
    month_rows = monthly_profit_loss(trades)
    selected_ticker = trades[0]["ticker"] if trades else ""
    price_points = stock_price_points(trades, selected_ticker) if selected_ticker else []
    forecast_values = linear_forecast(price_points)
    monthly_values = [row["profit_loss"] for row in month_rows]

    return {
        "request": request,
        "user": user,
        "message": message,
        "error": error,
        "trades": trades,
        "holdings": holdings,
        "prices": prices,
        "summary": {
            "profit_loss": total_profit_loss(trades),
            "trade_count": len(trades),
            "total_volume": total_volume(trades),
            "industry_count": len({trade["industry"] for trade in trades}),
            "portfolio_value": portfolio_value(trades, prices),
            "volatility": simple_volatility(monthly_values),
        },
        "industry_rows": industry_rows,
        "stock_rows": stock_rows,
        "monthly_rows": month_rows,
        "best_worst": best_and_worst(trades),
        "forecast": {
            "ticker": selected_ticker,
            "history": price_points,
            "values": forecast_values,
            "signal": moving_average_signal(price_points),
        },
        "chart": {
            "industry_labels": [row["label"] for row in industry_rows if row["profit_loss"] > 0],
            "industry_values": [row["profit_loss"] for row in industry_rows if row["profit_loss"] > 0],
            "month_labels": [row["month"] for row in month_rows],
            "month_values": [row["profit_loss"] for row in month_rows],
            "forecast_labels": [f"Point {index + 1}" for index in range(len(price_points) + len(forecast_values))],
            "forecast_history": price_points,
            "forecast_values": [None for _ in price_points] + forecast_values,
        },
        "money": money,
    }


@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", dashboard_context(request))


@app.post("/users")
def create_user(name: str = Form(...), email: str = Form(...)):
    with connect() as connection:
        connection.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", (name.strip(), email.strip()))
        row = connection.execute("SELECT user_id FROM users WHERE email = ?", (email.strip(),)).fetchone()
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("stock_user_id", str(row["user_id"]), httponly=True, samesite="lax")
    return response


@app.post("/trades")
def create_trade(
    request: Request,
    stock_name: str = Form(...),
    ticker: str = Form(...),
    trade_date: str = Form(...),
    trade_type: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    industry: str = Form(...),
):
    cleaned_type = trade_type.strip().title()
    error = validate_trade(trade_date, cleaned_type, price, quantity)
    if error:
        return templates.TemplateResponse("dashboard.html", dashboard_context(request, error=error), status_code=400)

    with connect() as connection:
        connection.execute(
            """
            INSERT INTO trades (user_id, stock_name, ticker, trade_date, trade_type, price, quantity, industry)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_user_id(request),
                stock_name.strip(),
                ticker.strip().upper(),
                trade_date,
                cleaned_type,
                price,
                quantity,
                industry.strip(),
            ),
        )
    return RedirectResponse("/", status_code=303)


@app.post("/trades/{trade_id}/delete")
def delete_trade(request: Request, trade_id: int):
    with connect() as connection:
        connection.execute(
            "DELETE FROM trades WHERE trade_id = ? AND user_id = ?",
            (trade_id, current_user_id(request)),
        )
    return RedirectResponse("/", status_code=303)


@app.post("/seed")
def seed_data(request: Request):
    user_id = current_user_id(request)
    rows = [
        ("Tata Consultancy Services", "TCS.NS", "2024-01-10", "Buy", 3650.00, 5, "Technology"),
        ("Infosys", "INFY.NS", "2024-02-18", "Buy", 1480.00, 8, "Technology"),
        ("HDFC Bank", "HDFCBANK.NS", "2024-03-04", "Buy", 1420.00, 10, "Finance"),
        ("Tata Consultancy Services", "TCS.NS", "2024-04-12", "Sell", 3920.00, 2, "Technology"),
        ("Reliance", "RELIANCE.NS", "2024-05-20", "Buy", 2860.00, 4, "Energy"),
        ("Infosys", "INFY.NS", "2024-06-14", "Sell", 1545.00, 3, "Technology"),
    ]
    with connect() as connection:
        connection.executemany(
            """
            INSERT INTO trades (user_id, stock_name, ticker, trade_date, trade_type, price, quantity, industry)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(user_id, *row) for row in rows],
        )
    return RedirectResponse("/", status_code=303)


@app.get("/trades/export")
def export_trades(request: Request):
    trades = list_trades(current_user_id(request))
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["stock_name", "ticker", "trade_date", "trade_type", "price", "quantity", "industry"],
    )
    writer.writeheader()
    for trade in trades:
        writer.writerow({field: trade[field] for field in writer.fieldnames})
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=stock-trades.csv"},
    )


@app.post("/trades/import")
async def import_trades(request: Request, file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    for row in reader:
        trade_type = row["trade_type"].strip().title()
        price = float(row["price"])
        quantity = int(row["quantity"])
        error = validate_trade(row["trade_date"], trade_type, price, quantity)
        if error:
            return templates.TemplateResponse("dashboard.html", dashboard_context(request, error=error), status_code=400)
        rows.append(
            (
                current_user_id(request),
                row["stock_name"].strip(),
                row["ticker"].strip().upper(),
                row["trade_date"],
                trade_type,
                price,
                quantity,
                row["industry"].strip(),
            )
        )

    with connect() as connection:
        connection.executemany(
            """
            INSERT INTO trades (user_id, stock_name, ticker, trade_date, trade_type, price, quantity, industry)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return RedirectResponse("/", status_code=303)
