"""Dash micro-frontend — app factory.

Submodules:
    theme      – colors, fonts, shared CSS dicts
    charts     – pure Plotly figure builders
    layouts    – layout wrappers (figure + controls)
    callbacks  – server-side and clientside callbacks
"""

import json

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

from .theme import (
    FONT_FAMILY, GOOGLE_FONTS_URL, MATERIAL_ICONS_URL,
    ANGULAR_ORIGIN, EXPENSE_COLORS, BAR_COLORS,
    TOOLBAR_BTN, TOOLBAR_BTN_ACTIVE,
)
from .callbacks import register_callbacks


def create_dash_app(flask_app):
    """Create and return the Dash application mounted on *flask_app*."""
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
        title='Bank Dashboard - Analytics',
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.BOOTSTRAP, GOOGLE_FONTS_URL, MATERIAL_ICONS_URL],
    )

    # Config passed to clientside JS via window.dashConfig
    dash_config = json.dumps({
        'angularOrigin': ANGULAR_ORIGIN,
        'expenseColors': EXPENSE_COLORS,
        'barColors': BAR_COLORS,
        'toolbarBtn': TOOLBAR_BTN,
        'toolbarBtnActive': TOOLBAR_BTN_ACTIVE,
    })

    # ── Root layout ─────────────────────────────────────────────────────────
    dash_app.layout = html.Div([
        html.Script(f'window.dashConfig = {dash_config};'),
        dcc.Store(id='angular-filter', data={'type': None, 'value': None}),
        dcc.Store(id='chart-data-store', data={}),
        dcc.Store(id='selected-expense', data=None),
        dcc.Store(id='_dummy-cashflow-anim', data=None),
        dcc.Store(id='_dummy-toggle', data=None),
        dcc.Store(id='_dummy-expense-hover', data=None),
        dcc.Store(id='_dummy-liquidity-anim', data=None),
        dcc.Store(id='_dummy-toolbar', data=None),
        dcc.Interval(id='interval-component', interval=30_000, n_intervals=0),
        dcc.Location(id='url', refresh=False),
        html.Div(id='chart-container', style={
            'width': '100%', 'height': '100vh', 'position': 'relative',
        }),
    ], style={
        'fontFamily': FONT_FAMILY,
        'padding': '0', 'margin': '0',
        'backgroundColor': 'transparent',
        'height': '100vh', 'overflow': 'hidden',
        'WebkitFontSmoothing': 'antialiased',
        'MozOsxFontSmoothing': 'grayscale',
    })

    # ── Callbacks ───────────────────────────────────────────────────────────
    register_callbacks(dash_app, flask_app)

    return dash_app
