from __future__ import annotations

import os
from datetime import date
from decimal import Decimal

import matplotlib.pyplot as plt
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error


load_dotenv()


def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            database=os.getenv("MYSQL_DATABASE", "stock_trade"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
        )
        if connection.is_connected():
            print("Connected to MySQL database.")
            return connection
    except Error as error:
        print(f"Database connection error: {error}")
    return None


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


def read_date(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        try:
            date.fromisoformat(value)
            return value
        except ValueError:
            print("Use YYYY-MM-DD format.")


def read_decimal(prompt: str) -> Decimal:
    while True:
        value = input(prompt).strip()
        try:
            amount = Decimal(value)
            if amount <= 0:
                raise ValueError
            return amount
        except Exception:
            print("Enter a positive number.")


def read_int(prompt: str) -> int:
    while True:
        value = input(prompt).strip()
        try:
            amount = int(value)
            if amount <= 0:
                raise ValueError
            return amount
        except ValueError:
            print("Enter a positive whole number.")


def read_trade_type() -> str:
    while True:
        value = input("Buy or Sell? ").strip().title()
        if value in {"Buy", "Sell"}:
            return value
        print("Enter Buy or Sell.")


def add_stock(connection) -> None:
    stock_name = input("Enter stock name: ").strip()
    trade_date = read_date("Enter trade date (YYYY-MM-DD): ")
    trade_type = read_trade_type()
    price = read_decimal("Enter price: ")
    quantity = read_int("Enter quantity: ")
    industry = input("Enter industry: ").strip()

    query = """
    INSERT INTO stocks (stock_name, trade_date, trade_type, price, quantity, industry)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (stock_name, trade_date, trade_type, price, quantity, industry))
    connection.commit()
    print("Stock transaction added.")


def signed_trade_value_sql() -> str:
    return "CASE WHEN trade_type = 'Sell' THEN price * quantity ELSE -price * quantity END"


def print_profit_loss(label: str, value) -> None:
    value = value or Decimal("0")
    if value > 0:
        print(f"{label} Profit: Rs.{value:.2f}")
    elif value < 0:
        print(f"{label} Loss: Rs.{abs(value):.2f}")
    else:
        print(f"{label}: no profit or loss.")


def calculate_overall_profit(connection) -> None:
    query = f"SELECT SUM({signed_trade_value_sql()}) FROM stocks"
    with connection.cursor() as cursor:
        cursor.execute(query)
        total = cursor.fetchone()[0]
    print_profit_loss("Overall", total)


def calculate_stockwise_profit_loss(connection) -> None:
    stock_name = input("Enter stock name: ").strip()
    query = f"SELECT SUM({signed_trade_value_sql()}) FROM stocks WHERE stock_name = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (stock_name,))
        total = cursor.fetchone()[0]
    print_profit_loss(f"{stock_name}", total)


def display_stock_records(connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT stock_id, stock_name, trade_date, trade_type, price, quantity, industry
            FROM stocks
            ORDER BY trade_date, stock_id
            """
        )
        records = cursor.fetchall()

    if not records:
        print("No stock records found.")
        return

    for record in records:
        print(record)


def filter_and_display_by_date(connection) -> None:
    start_date = read_date("Enter start date (YYYY-MM-DD): ")
    end_date = read_date("Enter end date (YYYY-MM-DD): ")
    query = """
    SELECT stock_id, stock_name, trade_date, trade_type, price, quantity, industry
    FROM stocks
    WHERE trade_date BETWEEN %s AND %s
    ORDER BY trade_date, stock_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (start_date, end_date))
        records = cursor.fetchall()

    if not records:
        print("No records found for this date range.")
        return

    for record in records:
        print(record)


def calculate_industry_profit_loss(connection) -> None:
    industry = input("Enter industry: ").strip()
    query = f"SELECT SUM({signed_trade_value_sql()}) FROM stocks WHERE industry = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (industry,))
        total = cursor.fetchone()[0]
    print_profit_loss(industry, total)


def show_stocks_by_industry(connection) -> None:
    industry = input("Enter industry: ").strip()
    query = """
    SELECT stock_id, stock_name, trade_date, trade_type, price, quantity, industry
    FROM stocks
    WHERE industry = %s
    ORDER BY trade_date, stock_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (industry,))
        records = cursor.fetchall()

    if not records:
        print(f"No records found for {industry}.")
        return

    for record in records:
        print(record)


def calculate_period_profit_loss(connection) -> None:
    start_date = read_date("Enter start date (YYYY-MM-DD): ")
    end_date = read_date("Enter end date (YYYY-MM-DD): ")
    query = f"""
    SELECT SUM({signed_trade_value_sql()})
    FROM stocks
    WHERE trade_date BETWEEN %s AND %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (start_date, end_date))
        total = cursor.fetchone()[0]
    print_profit_loss(f"{start_date} to {end_date}", total)


def monthly_profit_loss(connection) -> None:
    year = read_int("Enter year (YYYY): ")
    month = read_int("Enter month (1-12): ")
    query = f"""
    SELECT SUM({signed_trade_value_sql()})
    FROM stocks
    WHERE YEAR(trade_date) = %s AND MONTH(trade_date) = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (year, month))
        total = cursor.fetchone()[0]
    print_profit_loss(f"{month}/{year}", total)


def industry_percentage_pie_chart(connection) -> None:
    query = f"""
    SELECT industry, SUM({signed_trade_value_sql()}) AS profit
    FROM stocks
    GROUP BY industry
    HAVING profit > 0
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if not rows:
        print("No profitable industries found.")
        return

    industries = [row[0] for row in rows]
    profits = [float(row[1]) for row in rows]
    plt.figure(figsize=(8, 8))
    plt.pie(profits, labels=industries, autopct="%1.1f%%")
    plt.title("Industry Profit Percentage")
    plt.show()


def industry_investment(connection) -> None:
    industry = input("Enter industry: ").strip()
    query = """
    SELECT SUM(price * quantity)
    FROM stocks
    WHERE industry = %s AND trade_type = 'Buy'
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (industry,))
        total = cursor.fetchone()[0] or Decimal("0")
    print(f"Total investment in {industry}: Rs.{total:.2f}")


def plot_industry_profit_loss(connection) -> None:
    industry = input("Enter industry: ").strip()
    query = f"""
    SELECT trade_date, SUM({signed_trade_value_sql()}) AS profit
    FROM stocks
    WHERE industry = %s
    GROUP BY trade_date
    ORDER BY trade_date
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (industry,))
        rows = cursor.fetchall()

    if not rows:
        print(f"No records found for {industry}.")
        return

    dates = [row[0] for row in rows]
    profits = [float(row[1]) for row in rows]
    plt.figure(figsize=(10, 4))
    plt.plot(dates, profits, marker="o")
    plt.title(f"Profit/Loss for {industry}")
    plt.xlabel("Date")
    plt.ylabel("Profit/Loss")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def menu() -> None:
    actions = {
        "1": add_stock,
        "2": calculate_overall_profit,
        "3": calculate_stockwise_profit_loss,
        "4": display_stock_records,
        "5": filter_and_display_by_date,
        "6": calculate_industry_profit_loss,
        "7": show_stocks_by_industry,
        "8": calculate_period_profit_loss,
        "9": monthly_profit_loss,
        "10": industry_percentage_pie_chart,
        "11": industry_investment,
        "12": plot_industry_profit_loss,
    }

    connection = create_connection()
    if connection is None:
        return

    create_table(connection)
    try:
        while True:
            print("\nStock Trade Management")
            print("1. Add a stock transaction")
            print("2. Calculate overall profit/loss")
            print("3. Calculate stock-wise profit/loss")
            print("4. Display stock records")
            print("5. Filter by date range")
            print("6. Calculate industry-wise profit/loss")
            print("7. Show stocks by industry")
            print("8. Calculate period profit/loss")
            print("9. Calculate monthly profit/loss")
            print("10. Show industry profit pie chart")
            print("11. Calculate industry investment")
            print("12. Plot industry profit/loss")
            print("0. Exit")

            choice = input("Enter your choice: ").strip()
            if choice == "0":
                break

            action = actions.get(choice)
            if action is None:
                print("Invalid choice.")
                continue

            try:
                action(connection)
            except Error as error:
                print(f"Database error: {error}")
    finally:
        connection.close()
        print("Connection closed.")


if __name__ == "__main__":
    menu()
