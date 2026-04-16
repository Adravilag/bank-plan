"""Design tokens: colors, typography, and shared CSS dicts."""

# ── Allowed origin for postMessage security ─────────────────────────────────
ANGULAR_ORIGIN = 'http://localhost:4200'

# ── Color Palette ───────────────────────────────────────────────────────────
PRIMARY = '#002e5a'
PRIMARY_CONTAINER = '#004481'
BLUE_900 = '#1e3a5f'
SLATE_400 = '#94a3b8'
SLATE_500 = '#64748b'

EXPENSE_COLORS = [PRIMARY, PRIMARY_CONTAINER, '#723101', SLATE_400, BLUE_900]
BAR_COLORS = [PRIMARY, PRIMARY_CONTAINER, BLUE_900, '#0d6efd']

# ── Typography ──────────────────────────────────────────────────────────────
GOOGLE_FONTS_URL = (
    'https://fonts.googleapis.com/css2'
    '?family=Inter:wght@300;400;500;600;700&display=swap'
)
FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_FAMILY_PLOTLY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

# ── Plotly hover label ──────────────────────────────────────────────────────
HOVERLABEL = dict(
    bgcolor='#fff',
    bordercolor='#e2e8f0',
    font=dict(family=FONT_FAMILY_PLOTLY, color=PRIMARY, size=13),
)

# ── Shared CSS dicts ────────────────────────────────────────────────────────
TOGGLE_CSS = {
    'display': 'inline-flex', 'gap': '4px', 'background': '#f1f5f9',
    'borderRadius': '6px', 'padding': '3px', 'position': 'absolute',
    'top': '8px', 'right': '12px', 'zIndex': '10',
}

TOGGLE_BTN = {
    'padding': '5px 14px', 'border': 'none', 'borderRadius': '4px',
    'fontSize': '11px', 'fontWeight': '500', 'color': SLATE_500,
    'background': 'transparent', 'cursor': 'pointer',
    'fontFamily': FONT_FAMILY_PLOTLY,
    'transition': 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    'letterSpacing': '0.01em',
}

TOGGLE_BTN_ACTIVE = {
    **TOGGLE_BTN,
    'background': '#fff', 'color': PRIMARY, 'fontWeight': '600',
    'boxShadow': '0 1px 3px rgba(0,0,0,0.06)',
}

FILTER_BADGE = {
    'display': 'inline-flex', 'alignItems': 'center', 'gap': '4px',
    'padding': '4px 12px', 'border': '1px solid #e2e8f0', 'borderRadius': '20px',
    'background': 'rgba(0,68,129,0.06)', 'color': PRIMARY,
    'fontSize': '11px', 'fontWeight': '600', 'fontFamily': FONT_FAMILY_PLOTLY,
    'cursor': 'pointer', 'position': 'absolute', 'top': '8px', 'right': '12px',
    'zIndex': '10',
}
