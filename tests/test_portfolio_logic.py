from src.portfolio_logic import (
    best_and_worst,
    holdings_by_ticker,
    linear_forecast,
    monthly_profit_loss,
    moving_average_signal,
    portfolio_value,
    total_profit_loss,
    total_volume,
)


TRADES = [
    {
        "stock_name": "Alpha",
        "ticker": "ALPHA",
        "trade_date": "2024-01-10",
        "trade_type": "Buy",
        "price": 100,
        "quantity": 10,
        "industry": "Technology",
    },
    {
        "stock_name": "Alpha",
        "ticker": "ALPHA",
        "trade_date": "2024-02-10",
        "trade_type": "Sell",
        "price": 120,
        "quantity": 4,
        "industry": "Technology",
    },
    {
        "stock_name": "Beta",
        "ticker": "BETA",
        "trade_date": "2024-02-12",
        "trade_type": "Buy",
        "price": 50,
        "quantity": 5,
        "industry": "Finance",
    },
]


def test_profit_loss_and_volume():
    assert total_profit_loss(TRADES) == -770
    assert total_volume(TRADES) == 1730


def test_holdings_and_portfolio_value():
    holdings = holdings_by_ticker(TRADES)
    assert holdings["ALPHA"]["quantity"] == 6
    assert holdings["BETA"]["quantity"] == 5
    assert portfolio_value(TRADES, {"ALPHA": 130, "BETA": 55}) == 1055


def test_monthly_profit_loss():
    rows = monthly_profit_loss(TRADES)
    assert rows == [
        {"month": "2024-01", "profit_loss": -1000.0},
        {"month": "2024-02", "profit_loss": 230.0},
    ]


def test_best_worst_and_forecast():
    result = best_and_worst(TRADES)
    assert result["best"]["label"] == "Beta"
    assert result["worst"]["label"] == "Alpha"
    assert linear_forecast([100, 110, 120], periods=2) == [130, 140]
    assert moving_average_signal([100, 105, 110, 120]) == "Uptrend"
