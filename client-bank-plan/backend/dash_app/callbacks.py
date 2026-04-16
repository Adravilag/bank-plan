"""All Dash callbacks — server-side and clientside."""

import json
import urllib.parse

import dash
from dash import callback_context
from dash.dependencies import Input, Output, State

from .theme import (
    ANGULAR_ORIGIN,
    EXPENSE_COLORS, BAR_COLORS,
    FILTER_BADGE,
)
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
        f"""
        function(n) {{
            if (!window._pmListenerAdded) {{
                window._pmListenerAdded = true;
                window.addEventListener('message', function(event) {{
                    if (event.origin !== '{ANGULAR_ORIGIN}') return;
                    var msg = event.data;
                    if (msg && msg.type === 'dash-filter') {{
                        var store = document.getElementById('angular-filter');
                        if (store) {{
                            store.setAttribute(
                                'data-filter',
                                JSON.stringify(msg.payload || {{}})
                            );
                        }}
                    }}
                    if (msg && msg.type === 'crossfilter') {{
                        window._crossfilterLabel =
                            msg.payload ? msg.payload.label : null;
                        window.dispatchEvent(new CustomEvent('crossfilter'));
                    }}
                }});
            }}
            return window.dash_clientside.no_update;
        }}
        """,
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
        """
        function(n) {
            if (!n) return window.dash_clientside.no_update;
            var g = document.querySelector('#cashflow-graph .js-plotly-plot');
            if (!g || !g.data || g.data.length < 2)
                return window.dash_clientside.no_update;
            var barY = g.data[0].y.slice();
            var lineY = g.data[1].y.slice();
            Plotly.restyle(g, {y: [barY.map(function(){return 0})]}, [0]);
            Plotly.restyle(g, {y: [lineY.map(function(){return 0})]}, [1]);
            setTimeout(function() {
                Plotly.animate(g, {
                    data: [{y: barY}, {y: lineY}],
                    traces: [0, 1], layout: {}
                }, {
                    transition: {duration: 1200, easing: 'cubic-in-out'},
                    frame: {duration: 1200, redraw: true}
                });
            }, 300);
            return window.dash_clientside.no_update;
        }
        """,
        Output('_dummy-cashflow-anim', 'data'),
        Input('cashflow-anim', 'n_intervals'),
        prevent_initial_call=True,
    )

    # ── Clientside: cashflow toggle button styling ──────────────────────────
    dash_app.clientside_callback(
        """
        function(n12, n6, n3) {
            var toggles = document.querySelectorAll('[id^="toggle-"]');
            var tid = window.dash_clientside.callback_context.triggered_id;
            toggles.forEach(function(b) {
                b.style.background = 'transparent';
                b.style.color = '#64748b';
                b.style.fontWeight = '500';
                b.style.boxShadow = 'none';
            });
            var active = document.getElementById(tid || 'toggle-12m');
            if (active) {
                active.style.background = '#fff';
                active.style.color = '#002e5a';
                active.style.fontWeight = '600';
                active.style.boxShadow = '0 1px 3px rgba(0,0,0,0.06)';
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('_dummy-toggle', 'data'),
        Input('toggle-12m', 'n_clicks'),
        Input('toggle-6m', 'n_clicks'),
        Input('toggle-3m', 'n_clicks'),
        prevent_initial_call=True,
    )

    # ── Clientside: expense hover dimming ───────────────────────────────────
    dash_app.clientside_callback(
        f"""
        function(hoverData) {{
            var g = document.querySelector('#expense-graph .js-plotly-plot');
            if (!g || !g.data) return window.dash_clientside.no_update;
            var base = {json.dumps(EXPENSE_COLORS)};
            var n = g.data[0].labels ? g.data[0].labels.length : 0;
            var colors = base.slice(0, n);
            if (hoverData && hoverData.points) {{
                var idx = hoverData.points[0].pointNumber;
                var dimmed = colors.map(function(c,i){{return i===idx?c:c+'aa';}});
                var widths = colors.map(function(_,i){{return i===idx?3:2;}});
                Plotly.restyle(g,{{'marker.colors':[dimmed],'marker.line.width':[widths]}},[0]);
            }} else {{
                var cur = g.data[0].marker ? g.data[0].marker.colors : colors;
                var sel = cur && cur.some(function(c){{return c&&c.endsWith('40');}});
                if (!sel) {{
                    Plotly.restyle(g,{{
                        'marker.colors':[colors],
                        'marker.line.width':[colors.map(function(){{return 2;}})]
                    }},[0]);
                }}
            }}
            return window.dash_clientside.no_update;
        }}
        """,
        Output('_dummy-expense-hover', 'data'),
        Input('expense-graph', 'hoverData'),
        prevent_initial_call=True,
    )

    # ── Clientside: liquidity entry animation + interactions ─────────────────
    dash_app.clientside_callback(
        f"""
        function(n) {{
            if (!n) return window.dash_clientside.no_update;
            var g = document.querySelector('#liquidity-graph .js-plotly-plot');
            if (!g || !g.data) return window.dash_clientside.no_update;
            var bc = {json.dumps(BAR_COLORS)};
            var nb = g.data[0].x ? g.data[0].x.length : 0;
            var colors = bc.slice(0, nb);
            var realY = g.data[0].y.slice();
            Plotly.restyle(g, {{y:[realY.map(function(){{return 0}})]}}, [0]);
            setTimeout(function() {{
                Plotly.animate(g, {{
                    data:[{{y:realY}}], traces:[0], layout:{{}}
                }}, {{
                    transition:{{duration:1000, easing:'cubic-in-out'}},
                    frame:{{duration:1000, redraw:true}}
                }});
            }}, 600);

            g.on('plotly_hover', function(e) {{
                var idx = e.points[0].pointNumber;
                var d = colors.map(function(c,i){{return i===idx?c:c+'30';}});
                Plotly.restyle(g, {{'marker.color':[d]}}, [0]);
            }});
            g.on('plotly_unhover', function() {{
                Plotly.restyle(g, {{'marker.color':[colors]}}, [0]);
            }});

            g.on('plotly_click', function(e) {{
                var pt = e.points[0];
                Plotly.relayout(g, {{
                    annotations: [{{
                        x:pt.x, y:pt.y,
                        text:'<b>€'+pt.y.toLocaleString()+'</b>',
                        showarrow:true, arrowhead:2, arrowcolor:'#004481',
                        ax:0, ay:-35,
                        font:{{size:13, color:'#002e5a', family:'Inter'}},
                        bgcolor:'#fff', bordercolor:'#c2c6d2',
                        borderwidth:1, borderpad:6
                    }}]
                }});
                setTimeout(function(){{Plotly.relayout(g,{{annotations:[]}});}},3000);
            }});

            window.addEventListener('message', function(event) {{
                if (event.origin !== '{ANGULAR_ORIGIN}') return;
                if (event.data && event.data.type === 'crossfilter') {{
                    var label = event.data.payload ? event.data.payload.label : null;
                    if (label) {{
                        var m = colors.map(function(c){{return c+'30';}});
                        Plotly.restyle(g,{{'marker.color':[m],'marker.opacity':[0.5]}},[0]);
                    }} else {{
                        Plotly.restyle(g,{{'marker.color':[colors],'marker.opacity':[0.9]}},[0]);
                    }}
                }}
            }});
            return window.dash_clientside.no_update;
        }}
        """,
        Output('_dummy-liquidity-anim', 'data'),
        Input('liquidity-anim', 'n_intervals'),
        prevent_initial_call=True,
    )
