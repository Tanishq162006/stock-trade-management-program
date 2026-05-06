from __future__ import annotations

from collections import defaultdict
from statistics import mean


def signed_trade_value(trade: dict) -> float:
    value = float(trade["price"]) * int(trade["quantity"])
    return value if trade["trade_type"] == "Sell" else -value


def total_profit_loss(trades: list[dict]) -> float:
    return sum(signed_trade_value(trade) for trade in trades)


def total_volume(trades: list[dict]) -> float:
    return sum(float(trade["price"]) * int(trade["quantity"]) for trade in trades)


def group_profit_loss(trades: list[dict], key: str) -> list[dict]:
    totals: dict[str, float] = defaultdict(float)
    for trade in trades:
        totals[str(trade[key])] += signed_trade_value(trade)
    return [
        {"label": label, "profit_loss": value}
        for label, value in sorted(totals.items(), key=lambda item: item[1], reverse=True)
    ]


def monthly_profit_loss(trades: list[dict]) -> list[dict]:
    totals: dict[str, float] = defaultdict(float)
    for trade in trades:
        month = str(trade["trade_date"])[:7]
        totals[month] += signed_trade_value(trade)
    return [{"month": month, "profit_loss": totals[month]} for month in sorted(totals)]


def holdings_by_ticker(trades: list[dict]) -> dict[str, dict]:
    holdings: dict[str, dict] = {}
    for trade in trades:
        ticker = str(trade.get("ticker") or trade["stock_name"]).upper()
        quantity = int(trade["quantity"])
        signed_quantity = quantity if trade["trade_type"] == "Buy" else -quantity
        row = holdings.setdefault(
            ticker,
            {
                "ticker": ticker,
                "stock_name": trade["stock_name"],
                "industry": trade["industry"],
                "quantity": 0,
                "invested": 0.0,
            },
        )
        row["quantity"] += signed_quantity
        if trade["trade_type"] == "Buy":
            row["invested"] += float(trade["price"]) * quantity
    return holdings


def portfolio_value(trades: list[dict], prices: dict[str, float]) -> float:
    value = 0.0
    for ticker, holding in holdings_by_ticker(trades).items():
        value += max(holding["quantity"], 0) * float(prices.get(ticker, 0))
    return value


def best_and_worst(trades: list[dict]) -> dict:
    rows = group_profit_loss(trades, "stock_name")
    if not rows:
        return {"best": None, "worst": None}
    return {"best": rows[0], "worst": rows[-1]}


def simple_volatility(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    variance = sum((value - avg) ** 2 for value in values) / (len(values) - 1)
    return variance**0.5


def linear_forecast(points: list[float], periods: int = 5) -> list[float]:
    if not points:
        return []
    if len(points) == 1:
        return [points[0] for _ in range(periods)]

    n = len(points)
    xs = list(range(n))
    x_mean = mean(xs)
    y_mean = mean(points)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, points))
    denominator = sum((x - x_mean) ** 2 for x in xs) or 1
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    return [intercept + slope * x for x in range(n, n + periods)]


def moving_average_signal(points: list[float], window: int = 3) -> str:
    if len(points) < window + 1:
        return "Not enough data"
    previous_avg = mean(points[-window - 1 : -1])
    current_avg = mean(points[-window:])
    if current_avg > previous_avg:
        return "Uptrend"
    if current_avg < previous_avg:
        return "Downtrend"
    return "Flat"
