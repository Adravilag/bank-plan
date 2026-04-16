/**
 * Clientside callbacks for Dash charts.
 *
 * Config injected via window.dashConfig:
 *   angularOrigin, expenseColors, barColors,
 *   toolbarBtnActive, toolbarBtn
 */

if (!window.dash_clientside) { window.dash_clientside = {}; }

window.dash_clientside.charts = {

    // ── PostMessage listener ───────────────────────────────────────────────
    postMessageListener: function (n) {
        if (window._pmListenerAdded) return window.dash_clientside.no_update;
        window._pmListenerAdded = true;
        var cfg = window.dashConfig || {};

        window.addEventListener('message', function (event) {
            if (event.origin !== cfg.angularOrigin) return;
            var msg = event.data;
            if (msg && msg.type === 'dash-filter') {
                var store = document.getElementById('angular-filter');
                if (store) {
                    store.setAttribute('data-filter', JSON.stringify(msg.payload || {}));
                }
            }
            if (msg && msg.type === 'crossfilter') {
                window._crossfilterLabel = msg.payload ? msg.payload.label : null;
                window.dispatchEvent(new CustomEvent('crossfilter'));
            }
        });
        return window.dash_clientside.no_update;
    },

    // ── Cash flow entry animation ──────────────────────────────────────────
    cashflowAnimation: function (n) {
        if (!n) return window.dash_clientside.no_update;
        var g = document.querySelector('#cashflow-graph .js-plotly-plot');
        if (!g || !g.data || g.data.length < 2) return window.dash_clientside.no_update;

        var barY = g.data[0].y.slice();
        var lineY = g.data[1].y.slice();
        Plotly.restyle(g, { y: [barY.map(function () { return 0; })] }, [0]);
        Plotly.restyle(g, { y: [lineY.map(function () { return 0; })] }, [1]);

        setTimeout(function () {
            Plotly.animate(g, {
                data: [{ y: barY }, { y: lineY }],
                traces: [0, 1], layout: {}
            }, {
                transition: { duration: 1200, easing: 'cubic-in-out' },
                frame: { duration: 1200, redraw: true }
            });
        }, 300);
        return window.dash_clientside.no_update;
    },

    // ── Cash flow toggle button styling ────────────────────────────────────
    toggleStyling: function (n12, n6, n3) {
        var toggles = document.querySelectorAll('[id^="toggle-"]');
        var tid = window.dash_clientside.callback_context.triggered_id;

        // Press animation on the clicked toggle
        var clicked = document.getElementById(tid || 'toggle-12m');
        if (clicked) {
            clicked.style.transform = 'scale(0.90)';
            setTimeout(function () { clicked.style.transform = ''; }, 150);
        }

        toggles.forEach(function (b) {
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
    },

    // ── Expense hover (disabled – keep colors stable) ────────────────────
    expenseHover: function () {
        return window.dash_clientside.no_update;
    },

    // ── Liquidity entry animation + interactions ───────────────────────────
    liquidityAnimation: function (n) {
        if (!n) return window.dash_clientside.no_update;
        var g = document.querySelector('#liquidity-graph .js-plotly-plot');
        if (!g || !g.data) return window.dash_clientside.no_update;

        var cfg = window.dashConfig || {};
        var bc = cfg.barColors || [];
        var nb = g.data[0].x ? g.data[0].x.length : 0;
        var colors = bc.slice(0, nb);
        var realY = g.data[0].y.slice();

        Plotly.restyle(g, { y: [realY.map(function () { return 0; })] }, [0]);
        setTimeout(function () {
            Plotly.animate(g, {
                data: [{ y: realY }], traces: [0], layout: {}
            }, {
                transition: { duration: 1000, easing: 'cubic-in-out' },
                frame: { duration: 1000, redraw: true }
            });
        }, 600);

        g.on('plotly_click', function (e) {
            var pt = e.points[0];
            Plotly.relayout(g, {
                annotations: [{
                    x: pt.x, y: pt.y,
                    text: '<b>€' + pt.y.toLocaleString() + '</b>',
                    showarrow: true, arrowhead: 2, arrowcolor: '#004481',
                    ax: 0, ay: -35,
                    font: { size: 13, color: '#002e5a', family: 'Inter' },
                    bgcolor: '#fff', bordercolor: '#c2c6d2',
                    borderwidth: 1, borderpad: 6
                }]
            });
            setTimeout(function () { Plotly.relayout(g, { annotations: [] }); }, 3000);
        });

        window.addEventListener('message', function (event) {
            if (event.origin !== cfg.angularOrigin) return;
            if (event.data && event.data.type === 'crossfilter') {
                var label = event.data.payload ? event.data.payload.label : null;
                if (label) {
                    var m = colors.map(function (c) { return c + '30'; });
                    Plotly.restyle(g, { 'marker.color': [m], 'marker.opacity': [0.5] }, [0]);
                } else {
                    Plotly.restyle(g, { 'marker.color': [colors], 'marker.opacity': [0.9] }, [0]);
                }
            }
        });
        return window.dash_clientside.no_update;
    },

    // ── Toolbar: zoom / pan / reset ────────────────────────────────────────
    toolbar: function (zoom_n, pan_n, reset_n) {
        var ctx = window.dash_clientside.callback_context;
        if (!ctx || !ctx.triggered.length) return window.dash_clientside.no_update;

        var g = document.querySelector('#cashflow-graph .js-plotly-plot');
        if (!g) return window.dash_clientside.no_update;

        var cfg = window.dashConfig || {};
        var btn = ctx.triggered[0].prop_id.split('.')[0];

        if (btn === 'tb-zoom') {
            Plotly.relayout(g, { dragmode: 'zoom' });
        } else if (btn === 'tb-pan') {
            Plotly.relayout(g, { dragmode: 'pan' });
        } else if (btn === 'tb-reset') {
            Plotly.relayout(g, {
                'xaxis.autorange': true,
                'yaxis.autorange': true,
                'yaxis2.autorange': true,
            });
        }

        var active = cfg.toolbarBtnActive || {};
        var normal = cfg.toolbarBtn || {};
        var zoomS = btn === 'tb-zoom' ? active : normal;
        var panS = btn === 'tb-pan' ? active : normal;
        var resetS = normal;

        // Remove focus ring after click
        if (document.activeElement) document.activeElement.blur();

        // Press animation on the clicked button
        var el = document.getElementById(btn);
        if (el) {
            el.style.transform = 'scale(0.90)';
            setTimeout(function () { el.style.transform = ''; }, 150);
        }

        return [zoomS, panS, resetS, window.dash_clientside.no_update];
    }
};
