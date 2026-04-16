"""Layout wrappers — combine figure + controls for each chart type."""

from dash import html, dcc

from .theme import TOGGLE_CSS, TOGGLE_BTN, TOGGLE_BTN_ACTIVE
from .charts import (
    build_cash_flow,
    build_expense_distribution,
    build_liquidity_forecast,
    build_loan_summary,
)

_CHART_STYLE = {'width': '100%', 'height': '100vh'}
_WRAPPER_STYLE = {'position': 'relative', 'height': '100vh'}


def layout_cash_flow():
    """Cash flow with 12M/6M/3M toggles and entry animation."""
    fig = build_cash_flow()

    children = html.Div([
        html.Div([
            html.Button('12M', id='toggle-12m', n_clicks=0, style=TOGGLE_BTN_ACTIVE),
            html.Button('6M', id='toggle-6m', n_clicks=0, style=TOGGLE_BTN),
            html.Button('3M', id='toggle-3m', n_clicks=0, style=TOGGLE_BTN),
        ], style=TOGGLE_CSS),
        dcc.Graph(
            id='cashflow-graph', figure=fig,
            config={
                'responsive': True,
                'displayModeBar': 'hover',
                'modeBarButtonsToRemove': [
                    'toImage', 'sendDataToCloud', 'lasso2d',
                    'autoScale2d', 'select2d',
                ],
                'displaylogo': False,
            },
            style=_CHART_STYLE,
        ),
        dcc.Interval(id='cashflow-anim', interval=500, max_intervals=1),
    ], style=_WRAPPER_STYLE)

    return children, {}


def layout_expense_distribution():
    """Donut with click-to-select, center text, filter badge."""
    fig = build_expense_distribution()

    children = html.Div([
        html.Button('', id='expense-reset-btn', n_clicks=0, style={'display': 'none'}),
        html.Div(id='expense-filter-badge', style={'display': 'none'}),
        dcc.Graph(
            id='expense-graph', figure=fig,
            config={'responsive': True, 'displayModeBar': False},
            style=_CHART_STYLE,
        ),
    ], style=_WRAPPER_STYLE)

    return children, {}


def layout_liquidity_forecast():
    """Bar chart with hover dimming, click annotations, crossfilter."""
    fig = build_liquidity_forecast()

    children = html.Div([
        dcc.Graph(
            id='liquidity-graph', figure=fig,
            config={'responsive': True, 'displayModeBar': False},
            style=_CHART_STYLE,
        ),
        dcc.Interval(id='liquidity-anim', interval=400, max_intervals=1),
    ], style=_WRAPPER_STYLE)

    return children, {}


def layout_loan_summary():
    """Simple bar chart — no extra controls."""
    fig = build_loan_summary()

    children = html.Div([
        dcc.Graph(
            id='loan-graph', figure=fig,
            config={'responsive': True, 'displayModeBar': False},
            style=_CHART_STYLE,
        ),
    ], style=_WRAPPER_STYLE)

    return children, {}
