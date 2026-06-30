import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
import urllib.request
import xml.etree.ElementTree as ET
import datetime, hashlib, ssl

st.set_page_config(page_title="Big Tech Stock Explorer", layout="wide", page_icon="📈",
                   initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
    /* ── Font ── */
    html, body, [class*="css"], .stApp, input, select, textarea {
        font-family: 'Nunito', sans-serif !important;
    }
    /* Apply Nunito to all buttons */
    button { font-family: 'Nunito', sans-serif !important; }

    /* ── Sidebar collapse button ── */
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button {
        background-color: #1a56db !important;
        border: none !important;
        border-radius: 50% !important;
        width: 2.2rem !important;
        height: 2.2rem !important;
        box-shadow: 0 2px 8px rgba(26,86,219,0.4) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    /* Hide the "keyboard_double_..." text */
    [data-testid="stSidebarCollapseButton"] button span,
    [data-testid="stSidebarCollapsedControl"] button span,
    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stSidebarCollapsedControl"] button svg {
        display: none !important;
    }
    /* Draw a white arrow via pseudo-element */
    [data-testid="stSidebarCollapseButton"] button::after {
        content: "←" !important;
        color: white !important;
        font-size: 1rem !important;
        font-family: sans-serif !important;
        position: absolute !important;
        top: 50% !important; left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: "→" !important;
        color: white !important;
        font-size: 1rem !important;
        font-family: sans-serif !important;
        position: absolute !important;
        top: 50% !important; left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }

    /* ── Global text ── */
    html, body, [class*="css"], .stApp { color: #111111; }

    /* ── Page background ── */
    .stApp { background-color: #ffffff; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #f0f4ff;
        border-right: 2px solid #1a56db;
    }
    section[data-testid="stSidebar"] * { color: #111111 !important; font-family: 'Nunito', sans-serif !important; }

    /* ── Headers ── */
    h1 { color: #0d2d6b !important; font-weight: 800; font-family: 'Nunito', sans-serif !important; letter-spacing: -0.5px; }
    h2, h3 { color: #1a3a8f !important; font-weight: 700; font-family: 'Nunito', sans-serif !important; }

    /* ── Metric cards ── */
    [data-testid="stMetricLabel"] { color: #1a56db !important; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
    [data-testid="stMetricValue"] { color: #111111 !important; font-weight: 800; }
    [data-testid="stMetricDelta"] { font-weight: 600; }

    /* ── Divider ── */
    hr { border: none; border-top: 2px solid #d0daf0 !important; margin: 1.5rem 0; }

    /* ── Slider ── */
    [data-testid="stSlider"] [role="slider"] { background-color: #1a56db !important; }

    /* ── Multiselect tags ── */
    span[data-baseweb="tag"] { background-color: #1a56db !important; color: #fff !important; font-family: 'Nunito', sans-serif !important; }

    /* ── Caption ── */
    .stCaption { color: #555 !important; font-size: 0.78rem; }

    /* ── Mobile responsive ── */
    @media (max-width: 768px) {
        /* Stack all st.columns() vertically */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.5rem !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: none !important;
            min-width: 100% !important;
        }

        /* Tighten main content padding */
        .main .block-container {
            padding: 1rem 0.75rem 2rem !important;
            max-width: 100% !important;
        }

        /* Title */
        h1 { font-size: 1.6rem !important; line-height: 1.3 !important; }
        h2, h3 { font-size: 1.05rem !important; }

        /* Metrics readable on small screens */
        [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }

        /* Info boxes */
        .stApp div[style*="border-radius"] {
            padding: 12px 14px !important;
            font-size: 0.88rem !important;
        }

        /* Quote font size */
        .stApp div[style*="1.15rem"] {
            font-size: 0.98rem !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            width: 85vw !important;
            min-width: unset !important;
        }
    }

</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>Big Tech Stock Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555; margin-top:-10px;'>Built by Maja — comparing the biggest names in tech since 2016</p>", unsafe_allow_html=True)
st.divider()

ALL_TICKERS = ["AAPL", "MSFT", "GOOG", "AMZN", "NFLX", "META", "MRNA", "INTC", "AMD", "PFE", "PSKY", "^GSPC"]


@st.cache_data(ttl=3600)
def load_data():
    raw = yf.download(ALL_TICKERS, start="2016-01-01", progress=False, auto_adjust=True)
    prices = raw["Close"].reset_index()
    prices = prices.rename(columns={"Date": "date", "^GSPC": "SP500"})
    prices["date"] = pd.to_datetime(prices["date"])
    # Drop tickers yfinance returned no data for
    prices = prices.dropna(axis=1, how="all")
    return prices

df = load_data()
tickers = [c for c in df.columns if c != "date"]

# ── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.header("Settings")
chosen = st.sidebar.multiselect("Choose stocks to compare", tickers, default=["AAPL", "MSFT", "GOOG"])

if not chosen:
    st.warning("Pick at least one stock from the sidebar.")
    st.stop()

# 🎨 Stock colours
DEFAULTS = ["#1a56db", "#e63946", "#2a9d8f", "#f4a261", "#8338ec",
            "#ff006e", "#fb5607", "#3a86ff", "#06d6a0", "#ffd166", "#ef476f", "#118ab2"]
st.sidebar.markdown("---")
st.sidebar.subheader("Stock Colours")
stock_colors = {}
color_cols = st.sidebar.columns(2)
for i, t in enumerate(chosen):
    stock_colors[t] = color_cols[i % 2].color_picker(t, DEFAULTS[i % len(DEFAULTS)], key=f"color_{t}")

# 💸 Investment calculator
st.sidebar.markdown("---")
st.sidebar.subheader("Investment Calculator")
investment = st.sidebar.number_input("If I had invested (€)", min_value=100, max_value=1_000_000, value=1000, step=100)
inv_view = st.sidebar.radio("Show results as", ["Total", "Per Year (CAGR)", "Per Month"], horizontal=True)

# 📅 Date range slider
st.sidebar.markdown("---")
st.sidebar.subheader("Date Range")
min_date = df["date"].min().date()
max_date = df["date"].max().date()
date_range = st.sidebar.slider("Select period", min_value=min_date, max_value=max_date,
                                value=(min_date, max_date), format="YYYY-MM")

# Filter data by date
mask = (df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])
dff = df[mask].copy()

if dff.empty:
    st.warning("No data for selected date range.")
    st.stop()

# Re-index prices to 1.00 at first available price in selected range
for t in tickers:
    non_null = dff[t].dropna()
    if not non_null.empty:
        dff[t] = dff[t] / non_null.iloc[0]

st.sidebar.markdown("---")
st.sidebar.markdown("*Prices indexed to 1.00 at start of selected period*")

# ── Performance metrics ────────────────────────────────────────────────────
st.subheader("Performance Summary")
cols = st.columns(len(chosen))
for col, t in zip(cols, chosen):
    growth = (dff[t].iloc[-1] - 1) * 100
    col.metric(t, f"{dff[t].iloc[-1]:.2f}x", f"{growth:+.1f}%")

# 🏆 Best & most volatile
best = max(chosen, key=lambda t: dff[t].iloc[-1])
best_growth = (dff[best].iloc[-1] - 1) * 100
volatile = max(chosen, key=lambda t: dff[t].std())

col1, col2 = st.columns(2)
col1.markdown(f"""
<div style="background:#f0f4ff; border-left:4px solid #1a56db; border-radius:6px; padding:14px 18px; color:#111;">
    <b>Best performer: {best}</b> — grew <b>{best_growth:.1f}%</b> in this period
</div>""", unsafe_allow_html=True)
col2.markdown(f"""
<div style="background:#f5f5f5; border-left:4px solid #888; border-radius:6px; padding:14px 18px; color:#111;">
    <b>Most volatile: {volatile}</b> — biggest price swings in this period
</div>""", unsafe_allow_html=True)

# 💸 Investment calculator results
st.subheader("What if you had invested?")
import datetime as _dt
years_held = max((date_range[1] - date_range[0]).days / 365.25, 0.01)
months_held = max((date_range[1] - date_range[0]).days / 30.44, 0.01)

inv_cols = st.columns(len(chosen))
for col, t in zip(inv_cols, chosen):
    final_value = investment * dff[t].iloc[-1]
    profit = final_value - investment
    growth_multiple = dff[t].iloc[-1]

    if inv_view == "Total":
        col.metric(t, f"€{final_value:,.0f}", f"€{profit:+,.0f} total profit")
    elif inv_view == "Per Year (CAGR)":
        cagr = (growth_multiple ** (1 / years_held) - 1) * 100
        avg_profit_yr = profit / years_held
        col.metric(t, f"{cagr:+.1f}% / year", f"≈ €{avg_profit_yr:,.0f} avg. profit/yr")
    else:
        monthly_rate = (growth_multiple ** (1 / months_held) - 1) * 100
        avg_profit_mo = profit / months_held
        col.metric(t, f"{monthly_rate:+.2f}% / month", f"≈ €{avg_profit_mo:,.0f} avg. profit/mo")

# ── Did you know ──────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="background:#f5f5f5; border-radius:8px; padding:18px 22px; color:#111; font-size:0.95rem;">
    <span style="color:#1a56db; font-weight:700; font-size:1rem;">Did you know?</span><br><br>
    Apple became the first U.S. company to reach a <b>$3 trillion market cap</b> in 2023 —
    making it more valuable than the entire UK stock market combined. Today, the five largest
    US tech companies (Apple, Microsoft, Nvidia, Amazon, Alphabet) are worth more than
    the GDP of every country except the United States and China.
</div>
""", unsafe_allow_html=True)

# ── Latest Apple News ──────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_apple_news():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            "https://finance.yahoo.com/rss/headline?s=AAPL",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=6) as r:
            tree = ET.parse(r)
        items = tree.findall(".//item")[:3]
        return [(item.findtext("title"), item.findtext("link")) for item in items]
    except Exception:
        return []

st.divider()
st.markdown("<h3>Latest Apple News</h3>", unsafe_allow_html=True)
news_items = fetch_apple_news()
today = datetime.date.today().strftime("%d %b %Y")
if news_items:
    links_html = "".join(
        f'<b>{i+1}.</b> <a href="{url}" target="_blank" style="color:#1a56db;">{title}</a><br>'
        for i, (title, url) in enumerate(news_items)
    )
    st.markdown(f"""
<div style="background:#f5f5f5; border-radius:8px; padding:18px 22px; color:#111; font-size:0.93rem; line-height:2;">
    <span style="color:#888; font-size:0.8rem;">Live headlines from Yahoo Finance · {today}</span><br><br>
    {links_html}
</div>
""", unsafe_allow_html=True)
else:
    st.info("Could not load news headlines right now — try refreshing.")

st.divider()

# ── Line chart ────────────────────────────────────────────────────────────
st.subheader("Price Growth Over Time")
fig = px.line(
    dff, x="date", y=chosen,
    title="Normalized Stock Price (indexed to 1.00 at start of period)",
    labels={"value": "Relative Price", "date": "Date", "variable": "Stock"},
    color_discrete_map=stock_colors
)
fig.update_layout(
    hovermode="x unified",
    paper_bgcolor="white",
    plot_bgcolor="#f8faff",
    font=dict(color="#111111"),
    title_font=dict(color="#0d2d6b", size=15)
)
fig.update_xaxes(gridcolor="#e0e8f5")
fig.update_yaxes(gridcolor="#e0e8f5")
st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

# ── Bar chart ─────────────────────────────────────────────────────────────
st.subheader("Total Growth Comparison")
growth_data = pd.DataFrame({
    "Stock": chosen,
    "Total Growth (%)": [(dff[t].iloc[-1] - 1) * 100 for t in chosen]
}).sort_values("Total Growth (%)", ascending=False)

bar_fig = px.bar(
    growth_data, x="Stock", y="Total Growth (%)",
    title="Total Growth for Selected Period",
    color="Stock",
    color_discrete_map=stock_colors,
    text_auto=".1f"
)
bar_fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
bar_fig.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="#f8faff",
    font=dict(color="#111111"),
    title_font=dict(color="#0d2d6b", size=15)
)
bar_fig.update_yaxes(gridcolor="#e0e8f5")
st.plotly_chart(bar_fig, use_container_width=True, config={"responsive": True})

# ── Annual returns chart ───────────────────────────────────────────────────
st.subheader("Annual Returns by Year")

annual = dff.copy()
annual["year"] = annual["date"].dt.year
yearly = (
    annual.groupby("year")[chosen]
    .apply(lambda g: (g.iloc[-1] / g.iloc[0] - 1) * 100)
    .reset_index()
)
yearly_long = yearly.melt(id_vars="year", var_name="Stock", value_name="Return (%)")

annual_fig = px.bar(
    yearly_long, x="year", y="Return (%)", color="Stock",
    barmode="group",
    title="Annual Return per Stock (% per calendar year)",
    labels={"year": "Year", "Return (%)": "Return (%)"},
    color_discrete_map=stock_colors,
    text_auto=".1f"
)
annual_fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", cliponaxis=False)
annual_fig.add_hline(y=0, line_color="#111", line_width=1.2, opacity=0.4)
annual_fig.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="#f8faff",
    font=dict(color="#111111", family="Nunito, sans-serif"),
    title_font=dict(color="#0d2d6b", size=15),
    bargap=0.2,
    bargroupgap=0.05,
    xaxis=dict(tickmode="linear", dtick=1),
)
annual_fig.update_yaxes(gridcolor="#e0e8f5", zeroline=False)
st.plotly_chart(annual_fig, use_container_width=True, config={"responsive": True})

# ── Podcast recommendations ────────────────────────────────────────────────
st.divider()
st.subheader("Podcasts Worth Listening To")
st.markdown("""
<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:14px; margin-top:8px;">

  <a href="https://www.theinvestorspodcast.com/we-study-billionaires/" target="_blank" style="text-decoration:none;">
  <div style="background:#f0f4ff; border-left:4px solid #1a56db; border-radius:8px; padding:16px 18px; cursor:pointer; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(26,86,219,0.2)'" onmouseout="this.style.boxShadow='none'">
    <div style="font-weight:800; color:#1a56db; font-size:1rem;">We Study Billionaires ↗</div>
    <div style="font-size:0.8rem; color:#1a56db; font-weight:700; margin:4px 0 8px;">The Investors Podcast Network</div>
    <div style="font-size:0.88rem; color:#333; line-height:1.5;">Deep dives into how the world's greatest investors think — Buffett, Munger, Lynch and beyond. Great for long-term value investing mindset.</div>
  </div>
  </a>

  <a href="https://joincolossus.com/shows/invest-like-the-best/" target="_blank" style="text-decoration:none;">
  <div style="background:#f0f4ff; border-left:4px solid #2a9d8f; border-radius:8px; padding:16px 18px; cursor:pointer; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(42,157,143,0.2)'" onmouseout="this.style.boxShadow='none'">
    <div style="font-weight:800; color:#2a9d8f; font-size:1rem;">Invest Like the Best ↗</div>
    <div style="font-size:0.8rem; color:#2a9d8f; font-weight:700; margin:4px 0 8px;">Patrick O'Shaughnessy</div>
    <div style="font-size:0.88rem; color:#333; line-height:1.5;">Conversations with top investors and business leaders. Covers everything from public equities to venture capital and company building.</div>
  </div>
  </a>

  <a href="https://www.npr.org/podcasts/510289/planet-money" target="_blank" style="text-decoration:none;">
  <div style="background:#f0f4ff; border-left:4px solid #e63946; border-radius:8px; padding:16px 18px; cursor:pointer; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(230,57,70,0.2)'" onmouseout="this.style.boxShadow='none'">
    <div style="font-weight:800; color:#e63946; font-size:1rem;">Planet Money ↗</div>
    <div style="font-size:0.8rem; color:#e63946; font-weight:700; margin:4px 0 8px;">NPR</div>
    <div style="font-size:0.88rem; color:#333; line-height:1.5;">Short, story-driven episodes that explain economic concepts and market events in plain language. Perfect for building financial intuition.</div>
  </div>
  </a>

  <a href="https://www.bloomberg.com/podcasts/masters_in_business" target="_blank" style="text-decoration:none;">
  <div style="background:#f0f4ff; border-left:4px solid #f4a261; border-radius:8px; padding:16px 18px; cursor:pointer; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(244,162,97,0.2)'" onmouseout="this.style.boxShadow='none'">
    <div style="font-weight:800; color:#f4a261; font-size:1rem;">Masters in Business ↗</div>
    <div style="font-size:0.8rem; color:#f4a261; font-weight:700; margin:4px 0 8px;">Bloomberg · Barry Ritholtz</div>
    <div style="font-size:0.88rem; color:#333; line-height:1.5;">Long-form interviews with the most influential figures in finance, economics and investing. Thoughtful and in-depth every episode.</div>
  </div>
  </a>

  <a href="https://tim.blog/podcast/" target="_blank" style="text-decoration:none;">
  <div style="background:#f0f4ff; border-left:4px solid #8338ec; border-radius:8px; padding:16px 18px; cursor:pointer; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(131,56,236,0.2)'" onmouseout="this.style.boxShadow='none'">
    <div style="font-weight:800; color:#8338ec; font-size:1rem;">The Tim Ferriss Show ↗</div>
    <div style="font-size:0.8rem; color:#8338ec; font-weight:700; margin:4px 0 8px;">Tim Ferriss</div>
    <div style="font-size:0.88rem; color:#333; line-height:1.5;">World-class performers share their routines, strategies and mental models — many episodes touch on investing, wealth and decision-making.</div>
  </div>
  </a>

  <a href="https://www.acquired.fm/" target="_blank" style="text-decoration:none;">
  <div style="background:#f0f4ff; border-left:4px solid #118ab2; border-radius:8px; padding:16px 18px; cursor:pointer; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 4px 12px rgba(17,138,178,0.2)'" onmouseout="this.style.boxShadow='none'">
    <div style="font-weight:800; color:#118ab2; font-size:1rem;">Acquired ↗</div>
    <div style="font-size:0.8rem; color:#118ab2; font-weight:700; margin:4px 0 8px;">Ben Gilbert & David Rosenthal</div>
    <div style="font-size:0.88rem; color:#333; line-height:1.5;">Exhaustive deep dives on the greatest companies of all time — Apple, NVIDIA, Microsoft and more. Essential listening for any Big Tech investor.</div>
  </div>
  </a>

</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Data source: Yahoo Finance via yfinance · App by Maja")

# ── Daily investing quote ──────────────────────────────────────────────────

QUOTES = [
    ("The stock market is a device for transferring money from the impatient to the patient.", "Warren Buffett"),
    ("In investing, what is comfortable is rarely profitable.", "Robert Arnott"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Risk comes from not knowing what you're doing.", "Warren Buffett"),
    ("An investment in knowledge pays the best interest.", "Benjamin Franklin"),
    ("The individual investor should act consistently as an investor and not as a speculator.", "Benjamin Graham"),
    ("Wide diversification is only required when investors do not understand what they are doing.", "Warren Buffett"),
    ("It's not how much money you make, but how much money you keep.", "Robert Kiyosaki"),
    ("The four most dangerous words in investing are: 'this time it's different.'", "Sir John Templeton"),
    ("Don't look for the needle in the haystack. Just buy the haystack.", "John Bogle"),
    ("Time in the market beats timing the market.", "Ken Fisher"),
    ("Invest for the long haul. Don't get too greedy and don't get too scared.", "Shelby M.C. Davis"),
    ("The stock market is filled with individuals who know the price of everything, but the value of nothing.", "Philip Fisher"),
    ("Behind every stock is a company. Find out what it's doing.", "Peter Lynch"),
    ("Compound interest is the eighth wonder of the world.", "Albert Einstein"),
]

today_str = datetime.date.today().isoformat()
idx = int(hashlib.md5(today_str.encode()).hexdigest(), 16) % len(QUOTES)
quote_text, quote_author = QUOTES[idx]

st.divider()
st.markdown(f"""
<div style="background:#f5f5f5; border-radius:8px; padding:22px 28px; color:#111; text-align:center; font-family:'Nunito',sans-serif;">
    <div style="font-size:1.15rem; font-style:italic; color:#1a3a8f; font-weight:600; line-height:1.6;">
        "{quote_text}"
    </div>
    <div style="margin-top:10px; font-size:0.88rem; color:#555; font-weight:700; letter-spacing:0.05em; text-transform:uppercase;">
        — {quote_author}
    </div>
    <div style="margin-top:6px; font-size:0.75rem; color:#aaa;">Quote of the day · updates every morning</div>
</div>
""", unsafe_allow_html=True)
