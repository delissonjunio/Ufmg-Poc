import functools

import pandas as pd
from pypfopt import EfficientCVaR, expected_returns, DiscreteAllocation
from flask import Flask, request
from pypfopt.exceptions import OptimizationError

HISTORIC_DATA = pd.read_csv("b3_stocks_processed.csv", parse_dates=True, index_col="date").dropna(axis='columns', how='any')
LATEST_PRICES = HISTORIC_DATA.iloc[-1:, :].squeeze(axis=0)
MEAN_HISTORIC_RETURNS = expected_returns.mean_historical_return(HISTORIC_DATA)
HISTORIC_RETURNS = expected_returns.returns_from_prices(HISTORIC_DATA)
ALL_TICKERS = set(MEAN_HISTORIC_RETURNS.keys())
DEFAULT_BETA = 0.95

app = Flask(__name__)


def render_optimized_portfolio(optimized_portfolio, cvar, value, latest_prices):
    allocator = DiscreteAllocation(optimized_portfolio, latest_prices, total_portfolio_value=value)
    allocated_portfolio, leftover = allocator.lp_portfolio()

    mean_return, cvar_val = cvar.portfolio_performance()
    return {
        "portfolio": {k: int(v) for k, v in allocated_portfolio.items()},
        "leftover": round(leftover, 2),
        "expected_annual_return": round(mean_return, 6),
        "conditional_value_at_risk": round(cvar_val, 6)
    }


@app.route("/tickers", methods=["GET"])
def ticker_list():
    return {"tickers": dict(LATEST_PRICES)}


@app.route("/evaluate/<method>", methods=["GET"])
def calculate(method):
    portfolio_unparsed = request.args.get("portfolio")
    portfolio_universe = {ticker for ticker in portfolio_unparsed.split(",") if ticker in ALL_TICKERS}


@app.route("/optimize/<method>", methods=["GET"])
def optimize(method):
    beta = request.args.get("beta")
    if beta is None:
        beta = DEFAULT_BETA
    else:
        beta = float(beta)

    target = request.args.get("target")
    if target:
        target = float(target)

    value = float(request.args.get("value"))

    portfolio_unparsed = request.args.get("portfolio")

    mean_historic_return = MEAN_HISTORIC_RETURNS
    historic_returns = HISTORIC_RETURNS
    latest_prices = LATEST_PRICES

    if portfolio_unparsed:
        portfolio_universe = {ticker for ticker in portfolio_unparsed.split(",") if ticker in ALL_TICKERS}
        tickers_to_remove = ALL_TICKERS - portfolio_universe

        mean_historic_return = mean_historic_return.drop(tickers_to_remove)
        latest_prices = latest_prices.drop(tickers_to_remove)
        historic_returns = historic_returns.drop(tickers_to_remove, axis=1)

    cv = EfficientCVaR(mean_historic_return, historic_returns, beta=beta)
    optimize_function = {
        "min_cvar": lambda: cv.min_cvar(),
        "efficient_risk": lambda: cv.efficient_risk(target),
        "efficient_return": lambda: cv.min_cvar(target),
    }

    if method not in optimize_function:
        return {"error": f"unknown optimization method {method}, use one of {optimize_function.keys()}"}, 500

    try:
        optimized_portfolio = optimize_function[method]()
    except OptimizationError:
        return {"error": "optimization was not feasible, please try using different inputs", "code": "infeasible"}

    return render_optimized_portfolio(optimized_portfolio, cv, value, latest_prices)

