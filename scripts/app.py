import pandas as pd
import numpy as np
from cvxpy import SolverError
from pypfopt import EfficientCVaR, expected_returns, DiscreteAllocation, objective_functions
from flask import Flask, request
from pypfopt.exceptions import OptimizationError

HISTORIC_DATA = pd.read_csv("b3_stocks_processed.csv", parse_dates=True, index_col="date").dropna(axis='columns', how='any')
LATEST_PRICES = HISTORIC_DATA.iloc[-1:, :].squeeze(axis=0)
MEAN_HISTORIC_RETURNS = expected_returns.mean_historical_return(HISTORIC_DATA)
HISTORIC_RETURNS = expected_returns.returns_from_prices(HISTORIC_DATA)
ALL_TICKERS = set(MEAN_HISTORIC_RETURNS.keys())
DEFAULT_BETA = 0.95
OPTIMIZATION_FUNCTIONS = ("min_cvar", "efficient_risk", "efficient_return")

app = Flask(__name__)


def render_optimized_portfolio(optimized_portfolio, cvar, value, latest_prices):
    allocator = DiscreteAllocation(optimized_portfolio, latest_prices, total_portfolio_value=value)
    allocated_portfolio, leftover = allocator.lp_portfolio(solver='SCIP')

    rebuilt_portfolio = optimized_portfolio.copy()
    total_allocated_value = value - leftover
    for key, value in allocated_portfolio.items():
        rebuilt_portfolio[key] = (allocated_portfolio[key] * latest_prices[key]) / total_allocated_value if key in allocated_portfolio else 0

    orig_mean_return, orig_cvar_val = cvar.portfolio_performance()
    cvar.weights = np.array(list(rebuilt_portfolio.values()))
    mean_return, cvar_val = cvar.portfolio_performance()
    return {
        "portfolio": {k: int(v) for k, v in allocated_portfolio.items()},
        "invested": round(total_allocated_value, 2),
        "leftover": round(leftover, 2),
        "expected_annual_return": round(mean_return, 6),
        "conditional_value_at_risk": round(cvar_val, 6),
        "original_expected_annual_return": round(orig_mean_return, 6),
        "original_conditional_value_at_risk": round(orig_cvar_val, 6),
        "original_portfolio": {k: round(v, 6) for k, v in optimized_portfolio.items() if round(v, 6) != 0},
        "beta": cvar._beta
    }


def do_optimization(mean_historic_return, historic_returns, beta, target, method, diversify=True):
    cv = EfficientCVaR(mean_historic_return, historic_returns, beta=beta)
    if diversify:
        cv.add_objective(objective_functions.L2_reg, gamma=0.1)

    optimize_function = {
        "min_cvar": lambda: cv.min_cvar(),
        "efficient_risk": lambda: cv.efficient_risk(target),
        "efficient_return": lambda: cv.efficient_return(target),
    }

    if method not in optimize_function:
        return {"error": f"unknown optimization method {method}, use one of {optimize_function.keys()}"}, 500

    return cv, optimize_function[method]()


def do_optimization_attempting_diversify(**kwargs):
    try:
        return do_optimization(**kwargs, diversify=True)
    except SolverError:
        return do_optimization(**kwargs, diversify=False)


@app.route("/tickers", methods=["GET"])
def ticker_list():
    return {"tickers": dict(LATEST_PRICES)}


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

    if method not in OPTIMIZATION_FUNCTIONS:
        return {"error": f"unknown optimization method {method}, use one of {OPTIMIZATION_FUNCTIONS}"}, 500

    try:
        cv, optimized_portfolio = do_optimization_attempting_diversify(
            mean_historic_return=mean_historic_return,
            historic_returns=historic_returns,
            beta=beta,
            target=target,
            method=method
        )
    except OptimizationError:
        return {"error": "optimization was not feasible, please try using different inputs", "code": "infeasible"}

    return render_optimized_portfolio(optimized_portfolio, cv, value, latest_prices)

