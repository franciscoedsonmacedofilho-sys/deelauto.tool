"""
Visual language lifted from rebelgroup.com screenshots: a warm coral brand
color, deep-navy ink, a cream page background, an editorial serif for
headlines over a clean grotesk for body/UI text, and a navy ring motif.
Exact hex values were sampled from the supplied screenshots, not guessed.
"""
from pathlib import Path

CORAL = "#EC423C"
CORAL_DARK = "#C93830"
CORAL_TINT = "#F6C4BF"
NAVY = "#152B4E"
NAVY_TINT = "#5B7091"
CREAM = "#FFF8F8"
WHITE = "#FFFFFF"

# Chart palette: navy = "policy norm / status quo", coral = "with carsharing"
# (the brand's own accent color standing in for the change the tool argues for).
COLOR_BEFORE = NAVY
COLOR_AFTER = CORAL
COLOR_MIN = CORAL_TINT
COLOR_MAX = CORAL
COLOR_NEG = NAVY

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400;1,9..144,500&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, sans-serif;
    color: {NAVY};
}}
.stApp {{
    background-color: {CREAM};
    background-image: radial-gradient(1100px 460px at 12% -8%, rgba(236,66,60,0.07), transparent 60%),
                       radial-gradient(900px 420px at 100% 0%, rgba(21,43,78,0.05), transparent 55%);
    background-attachment: fixed;
}}

/* ---- hide Streamlit's own chrome (header bar, hamburger menu, footer badge) ---- */
header[data-testid="stHeader"] {{
    background: transparent !important;
    box-shadow: none !important;
}}
#MainMenu {{ visibility: hidden; }}
div[data-testid="stToolbar"] {{ visibility: hidden; }}
div[data-testid="stDeployButton"] {{ display: none; }}
div[data-testid="stStatusWidget"] {{ display: none; }}
footer {{ visibility: hidden; }}
div[data-testid="stDecoration"] {{ display: none; }}
.block-container {{ padding-top: 1.1rem; }}

/* ---- headline serif everywhere Streamlit renders h1-h3 ---- */
h1, h2, h3, .rebel-serif {{
    font-family: 'Fraunces', Georgia, serif !important;
    color: {NAVY} !important;
    font-weight: 500 !important;
    letter-spacing: -0.01em;
}}
h1 {{ font-size: 2.6rem !important; }}
h2 {{ font-size: 1.7rem !important; }}
h3 {{ font-size: 1.65rem !important; margin-top: 0.3rem !important; }}
h6 {{
    font-family: 'Inter', sans-serif !important;
    font-size: 1.12rem !important;
    font-weight: 700 !important;
    color: {NAVY} !important;
    letter-spacing: -0.005em;
    margin-top: 0.4rem !important;
}}

/* ---- eyebrow label, mimicking "A quick intro" ---- */
.rebel-eyebrow {{
    font-family: 'Fraunces', Georgia, serif;
    font-style: italic;
    color: {CORAL};
    font-size: 1.1rem;
    margin-bottom: -0.6rem;
    margin-top: 0.6rem;
}}

/* ---- captions: a touch larger than Streamlit's default so they hold up
   next to the bigger headings/cards, but clearly a step below body text ---- */
[data-testid="stCaptionContainer"], .stCaption {{
    font-size: 0.92rem !important;
    line-height: 1.5 !important;
}}

/* ---- hero banner ---- */
.rebel-hero {{
    position: relative;
    background: {CORAL};
    background-size: cover;
    background-position: center 65%;
    color: {WHITE};
    padding: 4.2rem 3rem 2.2rem 3rem;
    margin: -1rem -1rem 2rem -1rem;
    overflow: hidden;
    border-radius: 0 0 22px 22px;
    min-height: 340px;
    display: flex;
    align-items: center;
    box-shadow: 0 18px 40px rgba(21,43,78,0.28);
}}
.rebel-hero .rebel-hero-text {{
    flex: 1 1 auto;
    max-width: 660px;
    position: relative;
    z-index: 1;
}}
.rebel-hero .rebel-hero-tag {{
    display: inline-block;
    text-transform: uppercase;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    padding: 0.35rem 0.8rem;
    border: 1px solid rgba(255,255,255,0.55);
    border-radius: 999px;
    margin-bottom: 1.1rem;
    backdrop-filter: blur(2px);
    background: rgba(21,43,78,0.28);
}}
.rebel-hero h1 {{
    color: {WHITE} !important;
    font-size: 3.4rem !important;
    margin-bottom: 0.9rem !important;
    line-height: 1.02;
    text-shadow: 0 4px 24px rgba(21,43,78,0.55);
}}
.rebel-hero p {{
    color: {WHITE};
    font-size: 1.12rem;
    max-width: 580px;
    line-height: 1.45;
    text-shadow: 0 2px 14px rgba(21,43,78,0.55);
}}
.rebel-hero .rebel-ring {{
    position: absolute;
    right: -60px;
    top: -80px;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    border: 26px solid {NAVY};
    opacity: 0.55;
    z-index: 0;
}}
.rebel-hero .rebel-ring-2 {{
    position: absolute;
    right: 120px;
    bottom: -110px;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    border: 16px solid {WHITE};
    opacity: 0.22;
    z-index: 0;
}}
.rebel-crumb {{
    font-size: 0.82rem;
    letter-spacing: 0.02em;
    opacity: 0.95;
    margin-top: 1.6rem;
    text-shadow: 0 1px 10px rgba(21,43,78,0.5);
}}

/* ---- tabs styled like the top nav ---- */
button[data-baseweb="tab"] {{
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    font-size: 0.82rem !important;
    color: {NAVY} !important;
}}
div[data-baseweb="tab-highlight"] {{
    background-color: {CORAL} !important;
    height: 3px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {CORAL} !important;
}}
div[data-baseweb="tab-border"] {{ background-color: #F0DEDC !important; }}

/* ---- sidebar ---- */
section[data-testid="stSidebar"] {{
    background-color: {WHITE};
    border-right: 1px solid #F0DEDC;
}}
section[data-testid="stSidebar"][aria-expanded="true"] {{
    min-width: 420px !important;
    max-width: 420px !important;
}}
.rebel-sidebar-title {{
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin: 0 0 0.2rem 0;
}}
.rebel-sidebar-title span {{
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.9rem;
    font-weight: 600;
    color: {CORAL};
    line-height: 1.15;
}}

/* ---- location picker: styled red/coral so it reads as "start here" ----
   (the marker div sits inside the preceding st.markdown block; :has() lets
   us select that whole block so '+' can reach the selectbox block right
   after it, since Streamlit renders each call as its own sibling container) */
div:has(> .rebel-location-marker) + div div[data-baseweb="select"] > div,
div:has(.rebel-location-marker) + div div[data-baseweb="select"] > div {{
    border: 2px solid {CORAL} !important;
    background-color: rgba(236,66,60,0.07) !important;
    box-shadow: 0 0 0 3px rgba(236,66,60,0.12) !important;
}}
div:has(.rebel-location-marker) + div div[data-baseweb="select"] span {{
    color: {CORAL_DARK} !important;
    font-weight: 600 !important;
}}
div:has(.rebel-location-marker) + div svg {{ color: {CORAL} !important; }}
.rebel-location-tag {{
    display: inline-block;
    color: {CORAL};
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.3rem;
}}

/* ---- metric widgets ---- */
div[data-testid="stMetric"] {{
    background-color: {WHITE};
    border: 1px solid #F0DEDC;
    border-radius: 6px;
    padding: 0.9rem 1rem 0.7rem 1rem;
}}
div[data-testid="stMetricLabel"] {{
    color: {NAVY_TINT} !important;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.72rem !important;
    letter-spacing: 0.03em;
}}
div[data-testid="stMetricValue"] {{
    color: {NAVY} !important;
    font-family: 'Fraunces', Georgia, serif !important;
    font-weight: 500 !important;
}}

/* ---- coral headline stat card (custom HTML) ---- */
.rebel-stat-card {{
    background: {CORAL};
    background-image: linear-gradient(155deg, {CORAL} 0%, {CORAL_DARK} 100%);
    color: {WHITE};
    border-radius: 8px;
    padding: 1.4rem 1.5rem;
    height: 100%;
    min-height: 172px;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.rebel-stat-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(201,56,48,0.28);
}}
.rebel-stat-card .label {{
    text-transform: uppercase;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    opacity: 0.92;
    font-weight: 700;
    min-height: 2.2em;
    display: flex;
    align-items: flex-start;
    line-height: 1.2;
}}
.rebel-stat-card .label .icon {{
    margin-right: 0.4rem;
    font-size: 1.05rem;
    opacity: 1;
}}
.rebel-stat-card .value {{
    font-family: 'Fraunces', Georgia, serif;
    font-size: 2.85rem;
    font-weight: 500;
    margin-top: 0.2rem;
    line-height: 1.08;
    min-height: 2.16em;
}}
.rebel-stat-card .sub {{
    font-size: 0.92rem;
    opacity: 0.88;
    margin-top: auto;
    padding-top: 0.6rem;
    min-height: calc(0.6rem + 1.2em);
    line-height: 1.2;
}}

/* ---- light (non-coral) stat tile, for dense rows ---- */
.rebel-light-card {{
    background: {WHITE};
    border: 1px solid #F0DEDC;
    border-radius: 8px;
    padding: 1.15rem 1.25rem;
    height: 100%;
    min-height: 138px;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}}
.rebel-light-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 22px rgba(21,43,78,0.10);
    border-color: {CORAL_TINT};
}}
.rebel-light-card .label {{
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.04em;
    font-weight: 700;
    color: {NAVY_TINT};
    min-height: 2.2em;
    display: flex;
    align-items: flex-start;
    line-height: 1.2;
}}
.rebel-light-card .label .icon {{
    margin-right: 0.4rem;
    font-size: 1rem;
}}
.rebel-light-card .value {{
    font-family: 'Fraunces', Georgia, serif;
    font-size: 2.5rem;
    font-weight: 500;
    margin-top: 0.2rem;
    line-height: 1.08;
    min-height: 2.16em;
}}
.rebel-light-card .sub {{
    font-size: 0.86rem;
    color: {NAVY_TINT};
    margin-top: auto;
    padding-top: 0.5rem;
    min-height: calc(0.5rem + 1.2em);
    line-height: 1.2;
}}

/* ---- remark callout ---- */
.rebel-remark {{
    background: {WHITE};
    border: 1px solid #F0DEDC;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-top: 0.6rem;
    margin-bottom: 1.4rem;
}}
.rebel-remark .tag {{
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 700;
    color: {CORAL};
}}
.rebel-remark p {{
    margin: 0.25rem 0 0 0;
    font-size: 0.85rem;
    line-height: 1.5;
    color: {NAVY_TINT};
}}

/* ---- garbage-in-garbage-out warning banner ---- */
.rebel-warn {{
    background: {NAVY};
    color: {WHITE};
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.4rem 0 1.6rem 0;
}}
.rebel-warn b {{
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 500;
    font-size: 0.95rem;
}}
.rebel-warn p {{
    margin: 0.2rem 0 0 0;
    font-size: 0.82rem;
    opacity: 0.9;
    line-height: 1.5;
}}

/* ---- sidebar section divider spacing ---- */
section[data-testid="stSidebar"] .streamlit-expanderHeader {{
    font-weight: 600;
}}

/* ---- sidebar widgets picking up the brand accent instead of Streamlit's default red ---- */
div[data-baseweb="slider"] div[style*="background-color: rgb(255, 75, 75)"],
div[data-baseweb="slider"] > div > div:nth-child(2) {{
    background: {CORAL} !important;
}}
div[data-baseweb="slider"] div[role="slider"] {{
    background-color: {WHITE} !important;
    border: 3px solid {CORAL} !important;
    box-shadow: 0 1px 4px rgba(21,43,78,0.3) !important;
}}
div[data-testid="stSlider"] div[data-testid="stTickBarMin"],
div[data-testid="stSlider"] div[data-testid="stTickBarMax"] {{
    color: {NAVY_TINT} !important;
}}
div[data-testid="stNumberInput"] button {{
    border-color: #F0DEDC !important;
    color: {NAVY} !important;
}}
div[data-testid="stNumberInput"] button:hover {{
    background-color: {CORAL_TINT} !important;
    color: {CORAL_DARK} !important;
}}
div[data-testid="stNumberInput"] input,
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"] {{
    border-color: #F0DEDC !important;
}}
div[data-testid="stNumberInput"] input:focus,
div[data-baseweb="select"]:focus-within > div {{
    border-color: {CORAL} !important;
    box-shadow: 0 0 0 1px {CORAL} !important;
}}
div[role="radiogroup"] label div:first-child {{
    border-color: {NAVY_TINT} !important;
}}
div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div,
div[role="radiogroup"] label input:checked ~ div:first-child {{
    background-color: {CORAL} !important;
    border-color: {CORAL} !important;
}}
.stCheckbox input:checked + div, [data-testid="stCheckbox"] svg {{
    color: {CORAL} !important;
}}
section[data-testid="stSidebar"] div[data-testid="stExpander"] {{
    border-color: #F0DEDC !important;
    border-radius: 8px !important;
}}
section[data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {{
    color: {CORAL} !important;
}}

/* ---- custom HTML data table (replaces default st.dataframe look for the emissions table) ---- */
.rebel-table-wrap {{
    overflow-x: auto;
    border: 1px solid #F0DEDC;
    border-radius: 10px;
    margin-top: 0.3rem;
}}
.rebel-table {{
    border-collapse: collapse;
    width: 100%;
    font-size: 0.88rem;
    font-family: 'Inter', sans-serif;
}}
.rebel-table thead th {{
    background: {NAVY};
    color: {WHITE};
    text-align: right;
    padding: 0.7rem 1rem;
    font-weight: 600;
    font-size: 0.76rem;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    white-space: nowrap;
}}
.rebel-table thead th.idx {{ text-align: left; }}
.rebel-table td {{
    padding: 0.55rem 0.95rem;
    text-align: right;
    white-space: nowrap;
    color: {NAVY};
    border-bottom: 1px solid #F5E7E5;
}}
.rebel-table td.idx {{
    text-align: left;
    font-weight: 500;
    color: {NAVY};
}}
.rebel-table tbody tr:nth-child(odd) td {{ background: #FBF1F0; }}
.rebel-table tbody tr:hover td {{ background: {CORAL_TINT}66; }}
.rebel-table tbody tr:last-child td, .rebel-table tbody tr:nth-last-child(2) td {{
    font-weight: 600;
    border-top: 1px solid #E6C9C6;
}}

/* ---- scenario comparison cards (dumbbell range), replaces plain bar charts ---- */
.rebel-scn-wrap {{
    background: {WHITE};
    border: 1px solid #F0DEDC;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
}}
.rebel-scn-row {{
    display: grid;
    grid-template-columns: 168px 1fr 170px;
    align-items: center;
    gap: 22px;
    padding: 1.35rem 0.7rem;
    border-bottom: 1px solid #F0DEDC;
    border-radius: 6px;
    transition: background 0.15s ease;
}}
.rebel-scn-row:hover {{ background: {CREAM}; }}
.rebel-scn-row:last-child {{ border-bottom: none; }}
.rebel-scn-name {{
    font-weight: 700;
    font-size: 1.0rem;
    color: {NAVY};
}}
.rebel-scn-desc {{
    font-size: 0.8rem;
    color: {NAVY_TINT};
    margin-top: 0.25rem;
    line-height: 1.4;
}}
.rebel-scn-track {{
    position: relative;
    height: 11px;
    background: linear-gradient(90deg, {CREAM}, #F5E7E5);
    border-radius: 6px;
}}
.rebel-scn-fill {{
    position: absolute;
    top: 0; bottom: 0;
    background: linear-gradient(90deg, {CORAL_TINT}, {CORAL});
    border-radius: 6px;
}}
.rebel-scn-dot {{
    position: absolute;
    top: 50%;
    width: 22px; height: 22px;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    border: 3px solid {WHITE};
    box-shadow: 0 2px 6px rgba(21,43,78,0.4);
    z-index: 1;
}}
.rebel-scn-val {{
    text-align: right;
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.25rem;
    font-weight: 500;
    color: {NAVY};
    white-space: nowrap;
}}
@media (max-width: 700px) {{
    .rebel-scn-row {{ grid-template-columns: 100px 1fr 110px; gap: 10px; }}
}}

/* ---- buttons / inputs accent ---- */
.stButton > button, .stDownloadButton > button {{
    background-color: {CORAL};
    color: {WHITE};
    border: none;
    border-radius: 4px;
    font-weight: 600;
}}
.stButton > button:hover {{ background-color: {CORAL_DARK}; color: {WHITE}; }}
div[role="radiogroup"] label {{ font-family: 'Inter', sans-serif; }}

/* ---- the report-export button gets extra emphasis: bigger, bolder, a little lift ---- */
.stDownloadButton > button {{
    background-image: linear-gradient(135deg, {CORAL} 0%, {CORAL_DARK} 100%);
    font-size: 1.05rem;
    font-weight: 700;
    padding: 0.9rem 1.6rem;
    border-radius: 8px;
    box-shadow: 0 6px 18px rgba(201,56,48,0.30);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.rebel-export-btn .stDownloadButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(201,56,48,0.38);
}}

/* tighten default top padding */
.block-container {{ padding-top: 1.4rem; }}

/* ---- footer: "Powered by" + partner logos ---- */
.rebel-footer {{
    text-align: center;
    padding: 2.6rem 0 1.8rem 0;
    margin-top: 1rem;
    border-top: 1px solid {CORAL_TINT};
}}
.rebel-footer .label {{
    font-family: 'Fraunces', Georgia, serif;
    font-style: italic;
    font-size: 1.5rem;
    color: {CORAL};
    margin-bottom: 1.2rem;
}}
.rebel-advanced-header {{
    margin: 0.2rem 0 1rem 0;
}}
.rebel-advanced-header .row {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.3rem;
}}
.rebel-advanced-header .title {{
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 700;
    font-size: 1.3rem;
    color: {CORAL};
    line-height: 1.15;
}}
.rebel-advanced-header .subtitle {{
    font-family: 'Fraunces', Georgia, serif;
    font-style: italic;
    font-size: 0.92rem;
    color: {NAVY};
    line-height: 1.4;
    margin: 0;
}}
.rebel-footer .logos {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 3.2rem;
    flex-wrap: wrap;
}}
</style>
"""

def scenario_chart(names: list[str], low: list[float], high: list[float], value_fmt: str = "{:.2f}",
                    title: str | None = None):
    """Compact horizontal bar chart comparing a metric across scenarios --
    modelled on the source workbook's own 'Comparing scenarios' chart
    (Carsharing statistics!R6:T9): one thin row per scenario, low/high side
    by side, value labels at the bar end, no axis clutter."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Low", y=names, x=low, orientation="h",
        marker_color=CORAL_TINT,
        text=[value_fmt.format(v) for v in low], textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="High", y=names, x=high, orientation="h",
        marker_color=CORAL,
        text=[value_fmt.format(v) for v in high], textposition="outside",
    ))
    fig.update_layout(
        title=title, barmode="group", height=64 + 56 * len(names),
        margin=dict(t=44 if title else 10, b=10, l=10, r=60),
        showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1),
        xaxis=dict(visible=False), yaxis=dict(autorange="reversed"),
        **PLOTLY_LAYOUT,
    )
    return fig


def scenario_cards(names: list[str], low: list[float], high: list[float], value_fmt: str = "{:.2f}",
                    unit: str = "", descriptions: list[str] | None = None) -> str:
    """A row-per-scenario dumbbell/range card -- the brand-styled replacement
    for scenario_chart()'s plain bar chart. All rows share one domain (the
    overall max across every row) so a dot's horizontal position is directly
    comparable from one scenario to the next -- a scenario with a bigger
    number reads as sitting further right, not just differently scaled.

    Position uses a square-root scale rather than linear: with a linear
    scale, one outlier scenario (e.g. a flat "1 per 20 households" rule of
    thumb next to a handful of percentile-based estimates) stretches the
    axis so far that the other scenarios' dots all bunch up near zero and
    become indistinguishable. Square-rooting the values before mapping them
    to position compresses that stretch -- the outlier still reads as
    clearly the largest, but the small/medium scenarios spread out enough
    to compare against each other too."""
    all_vals = [float(v) for v in list(low) + list(high)]
    overall_span = max(all_vals) if all_vals else 0.0
    domain = overall_span * 1.08 if overall_span > 0 else 1.0
    domain_sqrt = domain ** 0.5

    def _pos(v: float) -> float:
        v = max(0.0, v)
        return max(0.0, min(100.0, (v ** 0.5) / domain_sqrt * 100)) if domain_sqrt > 0 else 0.0

    rows = []
    for i, name in enumerate(names):
        lo, hi = float(low[i]), float(high[i])
        lo_pct = _pos(lo)
        hi_pct = _pos(hi)
        left_pct, right_pct = min(lo_pct, hi_pct), max(lo_pct, hi_pct)
        desc = descriptions[i] if descriptions else ""
        val_text = value_fmt.format(lo) + unit if abs(lo - hi) < 1e-9 else f"{value_fmt.format(lo)}{unit} – {value_fmt.format(hi)}{unit}"
        desc_html = f'<div class="rebel-scn-desc">{desc}</div>' if desc else ""
        # Built as one unbroken line (no leading whitespace per line): Streamlit's
        # markdown renderer treats a 4+ space indented line as a code block, which
        # would otherwise dump this HTML out as literal text instead of rendering it.
        rows.append(
            '<div class="rebel-scn-row">'
            f'<div><div class="rebel-scn-name">{name}</div>{desc_html}</div>'
            '<div class="rebel-scn-track">'
            f'<div class="rebel-scn-fill" style="left:{left_pct:.2f}%;right:{100 - right_pct:.2f}%;"></div>'
            f'<div class="rebel-scn-dot" style="left:{lo_pct:.2f}%;background:{NAVY_TINT};"></div>'
            f'<div class="rebel-scn-dot" style="left:{hi_pct:.2f}%;background:{CORAL};"></div>'
            '</div>'
            f'<div class="rebel-scn-val">{val_text}</div>'
            '</div>'
        )
    return '<div class="rebel-scn-wrap">' + "".join(rows) + '</div>'


PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", color=NAVY),
    plot_bgcolor=WHITE,
    paper_bgcolor="rgba(0,0,0,0)",
    title_font=dict(family="Fraunces, Georgia, serif", size=18, color=NAVY),
)


def hero(title: str, subtitle: str, crumb: str = "", image_path: str | None = None, tag: str = ""):
    import base64
    import streamlit as st

    # Coral-to-navy scrim over the photo, darkest on the left where the
    # text sits, so white text stays readable without hiding the image.
    bg_style = f"background-color:{CORAL};"
    if image_path:
        try:
            b64 = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
            ext = Path(image_path).suffix.lstrip(".") or "jpeg"
            bg_style = (
                f"background-image:"
                f"linear-gradient(100deg, rgba(21,43,78,0.85) 0%, rgba(236,66,60,0.78) 42%, rgba(236,66,60,0.4) 78%),"
                f"url(data:image/{ext};base64,{b64});"
                f"background-size:cover;background-position:center 60%;"
            )
        except OSError:
            pass

    tag_html = f'<div class="rebel-hero-tag">{tag}</div>' if tag else ""
    crumb_html = f'<div class="rebel-crumb">{crumb}</div>' if crumb else ""
    # Built as one unbroken string (no embedded newlines/leading whitespace) --
    # see the note in scenario_cards() on why indented multi-line HTML passed
    # to st.markdown can silently render as literal text instead of markup.
    html = ('<div class="rebel-hero" style="' + bg_style + '">'
            '<div class="rebel-ring"></div><div class="rebel-ring-2"></div>'
            '<div class="rebel-hero-text">' + tag_html
            + f'<h1>{title}</h1><p>{subtitle}</p>' + crumb_html
            + '</div></div>')

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def eyebrow(text: str):
    import streamlit as st
    st.markdown(f'<div class="rebel-eyebrow">{text}</div>', unsafe_allow_html=True)


def sidebar_title(text: str) -> str:
    """The sidebar's own headline -- the exact isometric building icon
    pulled from the source Excel's own "Describe your project" header
    (xl/media/image1.png in the workbook, saved to assets/building_icon.png)
    sitting right next to a large, bold, coral heading. Built as one
    unbroken string -- see the note in scenario_cards() on the
    HTML-rendering bug this avoids."""
    import base64
    icon_path = Path(__file__).parent / "assets" / "building_icon.png"
    b64 = base64.b64encode(icon_path.read_bytes()).decode("ascii")
    icon_html = (f'<img src="data:image/png;base64,{b64}" '
                 'style="height:52px;width:auto;flex-shrink:0;" alt=""/>')
    return '<div class="rebel-sidebar-title">' + icon_html + f'<span>{text}</span></div>'


def stat_card(label: str, value: str, sub: str = "", icon: str = "", value_size: str = ""):
    # The sub-line div is always rendered -- even empty -- so every card in a
    # row reserves the same vertical space for it. Without this, a card with
    # a sub caption (e.g. "from the unit mix") comes out taller than its row
    # siblings that have none, and the row's bottoms visibly step down.
    sub_html = f'<div class="sub">{sub}</div>' if sub else '<div class="sub">&nbsp;</div>'
    icon_html = f'<span class="icon">{icon}</span>' if icon else ""
    value_style = f' style="font-size:{value_size};"' if value_size else ""
    return (f'<div class="rebel-stat-card"><div class="label">{icon_html}{label}</div>'
            f'<div class="value"{value_style}>{value}</div>{sub_html}</div>')


def light_card(label: str, value: str, sub: str = "", value_color: str = NAVY, icon: str = ""):
    """A white (non-coral) stat tile -- used when several tiles sit side by
    side and an all-coral row would be too heavy."""
    sub_html = f'<div class="sub">{sub}</div>' if sub else '<div class="sub">&nbsp;</div>'
    icon_html = f'<span class="icon">{icon}</span>' if icon else ""
    return (f'<div class="rebel-light-card"><div class="label">{icon_html}{label}</div>'
            f'<div class="value" style="color:{value_color};">{value}</div>{sub_html}</div>')


def data_table(df, index_label: str = "") -> str:
    """A branded HTML table (coral/navy header, zebra rows, bold total rows)
    replacing st.dataframe's default look for result tables the person will
    actually read closely. Expects df's cells to already be display-formatted
    strings. Built as single unbroken strings per cell/row -- see the note in
    scenario_cards() on why (Streamlit's markdown renderer turns an indented
    multi-line HTML blob into literal visible text instead of rendering it)."""
    cols = list(df.columns)
    thead = (f'<tr><th class="idx">{index_label}</th>'
              + "".join(f'<th>{c}</th>' for c in cols) + '</tr>')
    body_rows = []
    for idx, row in df.iterrows():
        cells = f'<td class="idx">{idx}</td>' + "".join(f'<td>{v}</td>' for v in row)
        body_rows.append(f'<tr>{cells}</tr>')
    return ('<div class="rebel-table-wrap"><table class="rebel-table"><thead>' + thead
            + '</thead><tbody>' + "".join(body_rows) + '</tbody></table></div>')


def remark(text: str):
    import streamlit as st
    st.markdown(
        f"""<div class="rebel-remark"><span class="tag">Remark</span><p>{text}</p></div>""",
        unsafe_allow_html=True,
    )


def warn_banner(text: str, title: str = "Garbage in, garbage out."):
    import streamlit as st
    st.markdown(
        f"""<div class="rebel-warn"><b>{title}</b><p>{text}</p></div>""",
        unsafe_allow_html=True,
    )


def advanced_header(title: str, subtitle: str) -> str:
    """A small "Advanced inputs" banner for the power-user sections (City-level
    policy, Country-level assumptions) -- the same building icon + bold coral
    title pairing as sidebar_title(), scaled down, with an italic navy
    subtitle wrapping underneath. Built as one unbroken string -- see the
    note in scenario_cards() on the HTML-rendering bug this avoids."""
    import base64
    icon_path = Path(__file__).parent / "assets" / "building_icon.png"
    b64 = base64.b64encode(icon_path.read_bytes()).decode("ascii")
    icon_html = (f'<img src="data:image/png;base64,{b64}" '
                 'style="height:30px;width:auto;flex-shrink:0;" alt=""/>')
    return ('<div class="rebel-advanced-header">'
            '<div class="row">' + icon_html + f'<span class="title">{title}</span></div>'
            f'<p class="subtitle">{subtitle}</p>'
            '</div>')


def footer(label: str = "Powered by:") -> str:
    """The page footer: a small italic coral "Powered by:" label above the
    two partner logos (Rebel, Natuurlijk Deelmobiliteit), both with
    transparent backgrounds so they sit cleanly on the cream page background.
    Built as one unbroken string -- see the note in scenario_cards() on the
    HTML-rendering bug this avoids."""
    import base64
    assets = Path(__file__).parent / "assets"
    rebel_b64 = base64.b64encode((assets / "rebel_logo.png").read_bytes()).decode("ascii")
    nat_b64 = base64.b64encode((assets / "natuurlijk_deelmobiliteit_logo.png").read_bytes()).decode("ascii")
    rebel_img = (f'<img src="data:image/png;base64,{rebel_b64}" '
                 'style="height:52px;width:auto;" alt="Rebel"/>')
    nat_img = (f'<img src="data:image/png;base64,{nat_b64}" '
               'style="height:70px;width:auto;" alt="Natuurlijk Deelmobiliteit"/>')
    return ('<div class="rebel-footer"><div class="label">' + label + '</div>'
            '<div class="logos">' + rebel_img + nat_img + '</div></div>')
