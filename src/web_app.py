from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mysql.connector import Error


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Stock Trade Management")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def db_config() -> dict[str, str]:
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "database": os.getenv("MYSQL_DATABASE", "stock_trade"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
    }


@contextmanager
def db_connection():
    connection = mysql.connector.connect(**db_config())
    try:
        yield connection
    finally:
        connection.close()


def create_table(connection) -> None:
    query = """
    CREATE TABLE IF NOT EXISTS stocks (
        stock_id INT PRIMARY KEY AUTO_INCREMENT,
        stock_name VARCHAR(255) NOT NULL,
        trade_date DATE NOT NULL,
        trade_type ENUM('Buy', 'Sell') NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        quantity INT NOT NULL,
        industry VARCHAR(255) NOT NULL
    )
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
    connection.commit()


def signed_trade_value_sql() -> str:
    return "CASE WHEN trade_type = 'Sell' THEN price * quantity ELSE -price * quantity END"


def money(value) -> str:
    amount = Decimal(value or 0)
    prefix = "-" if amount < 0 else ""
    return f"{prefix}Rs.{abs(amount):,.2f}"


def fetch_trades(connection) -> list[dict]:
    query = """
    SELECT stock_id, stock_name, trade_date, trade_type, price, quantity, industry
    FROM stocks
    ORDER BY trade_date DESC, stock_id DESC
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def fetch_summary(connection) -> dict:
    signed_value = signed_trade_value_sql()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(f"SELECT COALESCE(SUM({signed_value}), 0) AS profit_loss FROM stocks")
        profit_loss = cursor.fetchone()["profit_loss"]

        cursor.execute("SELECT COUNT(*) AS trade_count FROM stocks")
        trade_count = cursor.fetchone()["trade_count"]

        cursor.execute("SELECT COALESCE(SUM(price * quantity), 0) AS total_volume FROM stocks")
        total_volume = cursor.fetchone()["total_volume"]

        cursor.execute("SELECT COUNT(DISTINCT industry) AS industry_count FROM stocks")
        industry_count = cursor.fetchone()["industry_count"]

    return {
        "profit_loss": profit_loss,
        "trade_count": trade_count,
        "total_volume": total_volume,
        "industry_count": industry_count,
    }


def fetch_industry_rows(connection) -> list[dict]:
    query = f"""
    SELECT industry, COALESCE(SUM({signed_trade_value_sql()}), 0) AS profit_loss
    FROM stocks
    GROUP BY industry
    ORDER BY profit_loss DESC
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def fetch_monthly_rows(connection) -> list[dict]:
    query = f"""
    SELECT DATE_FORMAT(trade_date, '%Y-%m') AS month,
           COALESCE(SUM({signed_trade_value_sql()}), 0) AS profit_loss
    FROM stocks
    GROUP BY month
    ORDER BY month
    """
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def positive_industry_chart_rows(industry_rows: list[dict]) -> list[dict]:
    return [row for row in industry_rows if row["profit_loss"] > 0]


def dashboard_context(request: Request, error: str | None = None) -> dict:
    try:
        with db_connection() as connection:
            create_table(connection)
            trades = fetch_trades(connection)
            summary = fetch_summary(connection)
            industry_rows = fetch_industry_rows(connection)
            monthly_rows = fetch_monthly_rows(connection)
            industry_chart_rows = positive_industry_chart_rows(industry_rows)
    except Error as exc:
        return {
            "request": request,
            "db_error": str(exc),
            "error": error,
            "trades": [],
            "summary": {
                "profit_loss": Decimal("0"),
                "trade_count": 0,
                "total_volume": Decimal("0"),
                "industry_count": 0,
            },
            "industry_rows": [],
            "monthly_rows": [],
            "industry_labels": [],
            "industry_values": [],
            "month_labels": [],
            "month_values": [],
            "money": money,
        }

    return {
        "request": request,
        "db_error": None,
        "error": error,
        "trades": trades,
        "summary": summary,
        "industry_rows": industry_rows,
        "monthly_rows": monthly_rows,
        "industry_labels": [row["industry"] for row in industry_chart_rows],
        "industry_values": [float(row["profit_loss"]) for row in industry_chart_rows],
        "month_labels": [row["month"] for row in monthly_rows],
        "month_values": [float(row["profit_loss"]) for row in monthly_rows],
        "money": money,
    }


@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", dashboard_context(request))


@app.post("/trades")
def create_trade(
    request: Request,
    stock_name: str = Form(...),
    trade_date: str = Form(...),
    trade_type: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    industry: str = Form(...),
):
    cleaned_trade_type = trade_type.strip().title()
    if cleaned_trade_type not in {"Buy", "Sell"}:
        context = dashboard_context(request, "Trade type must be Buy or Sell.")
        return templates.TemplateResponse("dashboard.html", context, status_code=400)

    try:
        date.fromisoformat(trade_date)
    except ValueError:
        context = dashboard_context(request, "Trade date must use YYYY-MM-DD.")
        return templates.TemplateResponse("dashboard.html", context, status_code=400)

    if price <= 0 or quantity <= 0:
        context = dashboard_context(request, "Price and quantity must be positive.")
        return templates.TemplateResponse("dashboard.html", context, status_code=400)

    query = """
    INSERT INTO stocks (stock_name, trade_date, trade_type, price, quantity, industry)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    with db_connection() as connection:
        create_table(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    stock_name.strip(),
                    trade_date,
                    cleaned_trade_type,
                    price,
                    quantity,
                    industry.strip(),
                ),
            )
        connection.commit()

    return RedirectResponse("/", status_code=303)
