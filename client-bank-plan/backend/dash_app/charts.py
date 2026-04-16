"""Pure figure-construction functions — no Dash components, no callbacks."""

import plotly.graph_objects as go

from services.analytics import (
    get_cash_flow_by_month,
    get_transactions_by_type,
    get_balance_by_account_type,
    get_loan_summary,
)
from .theme import (
    PRIMARY, PRIMARY_CONTAINER, BLUE_900,
    SLATE_400, SLATE_500,
    EXPENSE_COLORS, BAR_COLORS,
    HOVERLABEL, FONT_FAMILY_PLOTLY,
)


# ── Shared layout helper ────────────────────────────────────────────────────

def apply_common_layout(fig: go.Figure) -> go.Figure:
    """Apply shared styling with improved typography."""
    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        autosize=True,
        font=dict(family=FONT_FAMILY_PLOTLY, size=12, color='#334155'),
        title_font=dict(size=15, color=PRIMARY, weight=600),
        xaxis=dict(
            tickfont=dict(size=11, color='#64748b', weight=400),
            title_font=dict(size=12, color='#475569', weight=500),
        ),
        yaxis=dict(
            tickfont=dict(size=11, color='#64748b', weight=400),
            title_font=dict(size=12, color='#475569', weight=500),
        ),
        legend=dict(font=dict(size=11, color='#475569', weight=400)),
    )
    return fig


# ── Cash Flow ────────────────────────────────────────────────────────────────

def build_cash_flow(months_slice=None) -> go.Figure:
    """Dual-axis: net-monthly bars + cumulative spline."""
    data = get_cash_flow_by_month()
    if not data:
        return apply_common_layout(go.Figure())

    if months_slice:
        data = data[-months_slice:]

    months = [d['month'] for d in data]
    net_flows = [d['net_flow'] for d in data]

    cumulative = []
    acc = 0
    for nf in net_flows:
        acc += nf
        cumulative.append(acc)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Neto Mensual', x=months, y=net_flows, yaxis='y2',
        marker=dict(
            color=[
                'rgba(0,102,68,0.3)' if v >= 0 else 'rgba(220,38,38,0.3)'
                for v in net_flows
            ],
            line=dict(
                color=[
                    'rgba(0,102,68,0.6)' if v >= 0 else 'rgba(220,38,38,0.6)'
                    for v in net_flows
                ],
                width=1,
            ),
        ),
        hovertemplate='<b>%{x}</b><br>Neto: <b>€%{y:,.0f}</b><extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        name='Acumulado', x=months, y=cumulative,
        mode='lines+markers', fill='tozeroy',
        line=dict(color=PRIMARY_CONTAINER, width=3, shape='spline'),
        marker=dict(color=PRIMARY_CONTAINER, size=8),
        fillcolor='rgba(0,68,129,0.08)',
        hovertemplate='<b>%{x}</b><br>Acumulado: <b>€%{y:,.0f}</b><extra></extra>',
    ))

    max_cum = max(cumulative) if cumulative else 1
    min_net = min(0, min(net_flows)) if net_flows else 0
    max_net = max(net_flows) if net_flows else 1

    fig.update_layout(
        barmode='group', bargap=0.4,
        hovermode='x unified', hoverlabel=HOVERLABEL,
        margin=dict(t=10, b=40, l=70, r=70),
        xaxis=dict(
            gridcolor='#f0f0f0', linecolor='#e2e2e2', type='category',
            showspikes=True, spikemode='across', spikethickness=1,
            spikecolor='#cbd5e1', spikedash='dot', spikesnap='cursor',
        ),
        yaxis=dict(
            gridcolor='#f0f0f0', linecolor='#e2e2e2',
            tickprefix='€', tickformat=',.0f',
            range=[0, max_cum * 1.12],
            title=dict(text='Acumulado', font=dict(size=10, color=SLATE_400), standoff=8),
            showspikes=True, spikemode='across', spikethickness=1,
            spikecolor='#cbd5e1', spikedash='dot',
        ),
        yaxis2=dict(
            overlaying='y', side='right', gridcolor='rgba(0,0,0,0)',
            tickprefix='€', tickformat=',.0f',
            range=[min_net * 1.3, max_net * 1.3],
            title=dict(text='Neto', font=dict(size=10, color=SLATE_400), standoff=8),
            showgrid=False,
        ),
        legend=dict(
            orientation='h', y=-0.15, x=0.5, xanchor='center',
            font=dict(size=11, color=SLATE_500),
        ),
        dragmode='zoom',
    )
    return apply_common_layout(fig)


# ── Expense Distribution ────────────────────────────────────────────────────

def build_expense_distribution(selected_index=None) -> go.Figure:
    """Deep donut with optional slice selection."""
    data = get_transactions_by_type()
    if not data:
        return apply_common_layout(go.Figure())

    type_labels = {
        'deposit': 'Depósito', 'withdrawal': 'Retiro', 'transfer': 'Transferencia',
        'payment': 'Pago', 'fee': 'Comisión',
    }

    labels = [type_labels.get(d['transaction_type'], d['transaction_type']) for d in data]
    values = [d['count'] for d in data]
    total = sum(values)

    colors = list(EXPENSE_COLORS[:len(labels)])
    pull = [0] * len(labels)
    if selected_index is not None and 0 <= selected_index < len(labels):
        colors = [c if i == selected_index else c + '40' for i, c in enumerate(colors)]
        pull = [0.1 if i == selected_index else 0 for i in range(len(labels))]

    # Center annotation text
    if selected_index is not None and 0 <= selected_index < len(labels):
        center_pct = f"{(values[selected_index] / total * 100):.1f}%"
        center_label = labels[selected_index]
        center_sub = f"{values[selected_index]} txns"
        center_text = (
            f"<b style='color:{EXPENSE_COLORS[selected_index]}'>{center_pct}</b><br>"
            f"<span style='font-size:10px;text-transform:uppercase;"
            f"letter-spacing:1.5px;color:{SLATE_500}'>{center_label}</span><br>"
            f"<span style='font-size:9px;color:{SLATE_400}'>{center_sub}</span>"
        )
    else:
        center_text = (
            f"<b>{total}</b><br>"
            f"<span style='font-size:10px;text-transform:uppercase;"
            f"letter-spacing:1.5px;color:{SLATE_500}'>Transacciones</span>"
        )

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.68,
        marker=dict(colors=colors, line=dict(color='#fff', width=2)),
        textinfo='none',
        hovertemplate=(
            '<b>%{label}</b><br>%{value} transacciones<br>%{percent}<extra></extra>'
        ),
        rotation=-40, direction='clockwise', sort=False,
        pull=pull,
    )])

    fig.add_annotation(
        text=center_text, x=0.5, y=0.5,
        xref='paper', yref='paper', showarrow=False,
        font=dict(size=22, color=BLUE_900, family='Inter'),
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation='v', yanchor='middle', y=0.5, xanchor='left', x=1.02,
            font=dict(size=12, color=SLATE_500),
            bgcolor='rgba(0,0,0,0)', itemsizing='constant',
        ),
        margin=dict(l=10, r=140, t=10, b=10),
        hoverlabel=HOVERLABEL,
    )
    return apply_common_layout(fig)


# ── Liquidity Forecast ──────────────────────────────────────────────────────

def build_liquidity_forecast(muted=False) -> go.Figure:
    """Navy-palette bars with text labels."""
    data = get_balance_by_account_type()
    if not data:
        return apply_common_layout(go.Figure())

    type_labels = {
        'savings': 'Ahorro', 'checking': 'Corriente',
        'credit': 'Crédito', 'investment': 'Inversión',
    }

    labels = [type_labels.get(d['account_type'], d['account_type']) for d in data]
    values = [float(d['total_balance']) for d in data]
    total = sum(values) or 1

    bar_colors = BAR_COLORS[:len(labels)]
    if muted:
        bar_colors = [c + '30' for c in bar_colors]

    fig = go.Figure(data=[go.Bar(
        x=labels, y=values,
        marker=dict(color=bar_colors, line=dict(width=0), opacity=0.9),
        text=[f"€{v:,.0f}" for v in values],
        textposition='outside',
        textfont=dict(size=10, color=SLATE_500, family='Inter'),
        customdata=[
            [
                d['count'],
                f"{(float(d['total_balance']) / total * 100):.1f}",
                f"€{float(d['avg_balance']):,.0f}",
                f"€{float(d['max_balance']):,.0f}",
            ]
            for d in data
        ],
        hovertemplate=(
            '<b>%{x}</b><br>Balance: <b>€%{y:,.0f}</b><br>'
            'Cuentas: %{customdata[0]}<br>Promedio: %{customdata[2]}<br>'
            'Mayor: %{customdata[3]}<br>Participación: %{customdata[1]}%<extra></extra>'
        ),
    )])

    max_val = max(values) if values else 1
    fig.update_layout(
        bargap=0.35,
        margin=dict(t=30, b=40, l=70, r=20),
        xaxis=dict(gridcolor='rgba(0,0,0,0)'),
        yaxis=dict(
            gridcolor='#f0f0f0', tickprefix='€', tickformat=',.0f',
            range=[0, max_val * 1.25],
            zeroline=True, zerolinecolor='#e2e8f0',
        ),
        hoverlabel=HOVERLABEL, dragmode=False,
    )
    return apply_common_layout(fig)


# ── Loan Summary ────────────────────────────────────────────────────────────

def build_loan_summary() -> go.Figure:
    """Loan summary bars."""
    data = get_loan_summary()
    if not data:
        return apply_common_layout(go.Figure())

    status_labels = {'active': 'Activo', 'paid': 'Pagado', 'defaulted': 'Impago'}
    colors = {'active': PRIMARY_CONTAINER, 'paid': '#723101', 'defaulted': '#dc2626'}

    fig = go.Figure(data=[go.Bar(
        x=[status_labels.get(d['status'], d['status']) for d in data],
        y=[float(d['total']) for d in data],
        text=[f"{d['count']} préstamos" for d in data],
        textposition='outside',
        textfont=dict(size=10, color=SLATE_500, family='Inter'),
        marker=dict(
            color=[colors.get(d['status'], SLATE_400) for d in data],
            line=dict(width=0), opacity=0.9,
        ),
        hovertemplate=(
            '<b>%{x}</b><br>Total: <b>€%{y:,.0f}</b><br>%{text}<extra></extra>'
        ),
    )])

    max_val = max(float(d['total']) for d in data) if data else 1
    fig.update_layout(
        bargap=0.35,
        margin=dict(t=30, b=40, l=70, r=20),
        xaxis=dict(gridcolor='rgba(0,0,0,0)'),
        yaxis=dict(
            gridcolor='#f0f0f0', tickprefix='€', tickformat=',.0f',
            range=[0, max_val * 1.25],
        ),
        hoverlabel=HOVERLABEL, dragmode=False,
    )
    return apply_common_layout(fig)
