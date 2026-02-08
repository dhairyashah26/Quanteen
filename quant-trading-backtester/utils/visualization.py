"""Plotly visualizations for strategies and portfolios."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_equity_curve(equity: pd.Series, drawdown: pd.Series) -> go.Figure:
    rolling_20 = drawdown.rolling(20, min_periods=1).mean()
    rolling_50 = drawdown.rolling(50, min_periods=1).mean()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08)
    fig.add_trace(go.Scatter(x=equity.index, y=equity, name="Equity"), row=1, col=1)
    fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown, name="Drawdown", fill="tozeroy"), row=2, col=1)
    fig.add_trace(go.Scatter(x=rolling_20.index, y=rolling_20, name="DD 20D"), row=2, col=1)
    fig.add_trace(go.Scatter(x=rolling_50.index, y=rolling_50, name="DD 50D"), row=2, col=1)

    fig.update_layout(title="Equity Curve & Drawdown", height=700)
    fig.update_yaxes(title_text="Equity", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown", row=2, col=1)
    return fig


def plot_price_signals(price: pd.Series, signals: pd.Series) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price.index, y=price, name="Price", line=dict(color="#1f77b4")))

    buys = signals[signals > 0]
    sells = signals[signals < 0]

    fig.add_trace(
        go.Scatter(
            x=buys.index,
            y=price.loc[buys.index],
            mode="markers",
            marker=dict(symbol="triangle-up", color="green", size=10),
            name="Buy",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sells.index,
            y=price.loc[sells.index],
            mode="markers",
            marker=dict(symbol="triangle-down", color="red", size=10),
            name="Sell",
        )
    )
    fig.update_layout(title="Price with Signals", height=500)
    return fig


def plot_strategy_heatmap(metrics: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        data=go.Heatmap(
            z=metrics.values,
            x=metrics.columns,
            y=metrics.index,
            colorscale="Viridis",
            colorbar=dict(title="Metric"),
        )
    )
    fig.update_layout(title="Strategy Comparison Heatmap", height=500)
    return fig


def plot_correlation_matrix(returns: pd.DataFrame) -> go.Figure:
    corr = returns.corr()
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
        )
    )
    fig.update_layout(title="Correlation Matrix", height=500)
    return fig
