"""Layout wrappers — combine figure + controls for each chart type."""

from dash import html, dcc

from .theme import (
    CARD_HEADER_CSS, CARD_TITLE_CSS, CARD_SUBTITLE_CSS,
    TOGGLE_CSS, TOGGLE_BTN, TOGGLE_BTN_ACTIVE, TOGGLE_DIVIDER,
    TOOLBAR_CSS, TOOLBAR_BTN, TOOLBAR_BTN_ACTIVE,
)
from .charts import (
    build_cash_flow,
    build_expense_distribution,
    build_liquidity_forecast,
    build_loan_summary,
)

_CHART_STYLE = {'width': '100%', 'height': 'calc(100vh - 52px)'}
_WRAPPER_STYLE = {'position': 'relative', 'height': '100vh', 'overflow': 'hidden'}


def layout_cash_flow():
    """Cash flow with 12M/6M/3M toggles and entry animation."""
    fig = build_cash_flow()

    _icon = {'fontSize': '14px'}

    children = html.Div([
        html.Div([
            html.Div([
                html.H3('Cash Flow Trend', style=CARD_TITLE_CSS),
                html.P('Zoom, pan y selecciona rangos directamente en la gráfica',
                       style=CARD_SUBTITLE_CSS),
            ]),
            html.Div([
                html.Div([
                    html.Button(html.Span('search', className='material-symbols-outlined', style=_icon),
                                id='tb-zoom', n_clicks=0, style=TOOLBAR_BTN_ACTIVE, title='Zoom'),
                    html.Button(html.Span('pan_tool', className='material-symbols-outlined', style=_icon),
                                id='tb-pan', n_clicks=0, style=TOOLBAR_BTN, title='Pan'),
                    html.Button(html.Span('restart_alt', className='material-symbols-outlined', style=_icon),
                                id='tb-reset', n_clicks=0, style=TOOLBAR_BTN, title='Reset'),
                ], style=TOOLBAR_CSS),
                html.Div(style=TOGGLE_DIVIDER),
                html.Div([
                    html.Button('12M', id='toggle-12m', n_clicks=0, style=TOGGLE_BTN_ACTIVE),
                    html.Button('6M', id='toggle-6m', n_clicks=0, style=TOGGLE_BTN),
                    html.Button('3M', id='toggle-3m', n_clicks=0, style=TOGGLE_BTN),
                ], style={'display': 'inline-flex', 'gap': '2px'}),
            ], style=TOGGLE_CSS),
        ], style=CARD_HEADER_CSS),
        dcc.Graph(
            id='cashflow-graph', figure=fig,
            config={'responsive': True, 'displayModeBar': False,
                    'scrollZoom': True},
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
