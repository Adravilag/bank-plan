"""All Dash callbacks — server-side and clientside.

Clientside JS lives in assets/clientside.js under the 'charts' namespace.
Config values (colors, origin, styles) are injected via window.dashConfig
in __init__.py.
"""

import urllib.parse

import dash
from dash import callback_context, ClientsideFunction
from dash.dependencies import Input, Output, State

from .theme import FILTER_BADGE
from .charts import build_cash_flow, build_expense_distribution
from .layouts import (
    layout_cash_flow,
    layout_expense_distribution,
    layout_liquidity_forecast,
    layout_loan_summary,
)


def register_callbacks(dash_app, flask_app):
    """Register every callback on *dash_app*."""

    # ── PostMessage listener (clientside) ───────────────────────────────────
    dash_app.clientside_callback(
        ClientsideFunction('charts', 'postMessageListener'),
        Output('angular-filter', 'data'),
        Input('interval-component', 'n_intervals'),
    )

    # ── Route to chart builder ──────────────────────────────────────────────
    @dash_app.callback(
        Output('chart-container', 'children'),
        Output('chart-data-store', 'data'),
        Input('url', 'search'),
    )
    def render_chart(search):
        params = urllib.parse.parse_qs((search or '?').lstrip('?'))
        chart_name = params.get('chart', ['cash-flow'])[0]

        builders = {
            'cash-flow': layout_cash_flow,
            'expense-distribution': layout_expense_distribution,
            'liquidity-forecast': layout_liquidity_forecast,
            'loan-summary': layout_loan_summary,
        }

        with flask_app.app_context():
            builder = builders.get(chart_name, layout_cash_flow)
            return builder()

    # ── Cash Flow: toggle 12M / 6M / 3M ────────────────────────────────────
    @dash_app.callback(
        Output('cashflow-graph', 'figure'),
        Input('toggle-12m', 'n_clicks'),
        Input('toggle-6m', 'n_clicks'),
        Input('toggle-3m', 'n_clicks'),
        State('chart-data-store', 'data'),
        prevent_initial_call=True,
    )
    def update_cashflow_range(n12, n6, n3, store_data):
        triggered = callback_context.triggered_id
        months_map = {'toggle-6m': 6, 'toggle-3m': 3}
        with flask_app.app_context():
            return build_cash_flow(months_map.get(triggered))

    # ── Expense: click to select slice → crossfilter ────────────────────────
    @dash_app.callback(
        Output('expense-graph', 'figure'),
        Output('selected-expense', 'data'),
        Output('expense-filter-badge', 'children'),
        Output('expense-filter-badge', 'style'),
        Input('expense-graph', 'clickData'),
        Input('expense-reset-btn', 'n_clicks'),
        State('selected-expense', 'data'),
        prevent_initial_call=True,
    )
    def on_expense_click(click_data, reset_clicks, current_selected):
        triggered = callback_context.triggered_id

        if triggered == 'expense-reset-btn':
            with flask_app.app_context():
                fig = build_expense_distribution(selected_index=None)
            return fig, None, '', {'display': 'none'}

        if click_data and click_data.get('points'):
            idx = click_data['points'][0].get('pointNumber')
            is_deselect = (idx == current_selected)
            new_selected = None if is_deselect else idx

            with flask_app.app_context():
                fig = build_expense_distribution(selected_index=new_selected)

            if new_selected is not None:
                label = click_data['points'][0].get('label', '')
                badge_text = f'✕ Filtro: {label}'
                badge_style = FILTER_BADGE
            else:
                badge_text = ''
                badge_style = {'display': 'none'}

            return fig, new_selected, badge_text, badge_style

        return (
            dash.no_update, dash.no_update,
            dash.no_update, dash.no_update,
        )

    # ── Clientside: cashflow entry animation ────────────────────────────────
    dash_app.clientside_callback(
        ClientsideFunction('charts', 'cashflowAnimation'),
        Output('_dummy-cashflow-anim', 'data'),
        Input('cashflow-anim', 'n_intervals'),
        prevent_initial_call=True,
    )

    # ── Clientside: cashflow toggle button styling ──────────────────────────
    dash_app.clientside_callback(
        ClientsideFunction('charts', 'toggleStyling'),
        Output('_dummy-toggle', 'data'),
        Input('toggle-12m', 'n_clicks'),
        Input('toggle-6m', 'n_clicks'),
        Input('toggle-3m', 'n_clicks'),
        prevent_initial_call=True,
    )

    # ── Clientside: expense hover dimming ───────────────────────────────────
    dash_app.clientside_callback(
        ClientsideFunction('charts', 'expenseHover'),
        Output('_dummy-expense-hover', 'data'),
        Input('expense-graph', 'hoverData'),
        prevent_initial_call=True,
    )

    # ── Clientside: liquidity entry animation + interactions ────────────────
    dash_app.clientside_callback(
        ClientsideFunction('charts', 'liquidityAnimation'),
        Output('_dummy-liquidity-anim', 'data'),
        Input('liquidity-anim', 'n_intervals'),
        prevent_initial_call=True,
    )

    # ── Toolbar: zoom / pan / reset ─────────────────────────────────────────
    dash_app.clientside_callback(
        ClientsideFunction('charts', 'toolbar'),
        [Output('tb-zoom', 'style'),
         Output('tb-pan', 'style'),
         Output('tb-reset', 'style'),
         Output('_dummy-toolbar', 'data')],
        [Input('tb-zoom', 'n_clicks'),
         Input('tb-pan', 'n_clicks'),
         Input('tb-reset', 'n_clicks')],
        prevent_initial_call=True,
    )
