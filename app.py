import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Stock Explorer", layout="wide")
st.title("📈 Stock Price Explorer")

@st.cache_data
def load_data():
    # This stock dataset is built into plotly — no file to download or push!
    df = px.data.stocks()              # columns: date + 6 big tech stocks
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()
tickers = [c for c in df.columns if c != "date"]

# Sidebar: pick which stocks to compare
chosen = st.sidebar.multiselect("Choose stocks", tickers, default=["AAPL", "MSFT", "GOOG"])
if not chosen:
    st.warning("Pick at least one stock from the sidebar.")
    st.stop()

st.caption("Prices are indexed to 1.00 at the start, so each line shows growth since Jan 2018.")

# Top grower highlight
growths = {t: (df[t].iloc[-1] - 1) * 100 for t in chosen}
top_stock = max(growths, key=growths.get)
st.success(f"🏆 Top grower: **{top_stock}** with **{growths[top_stock]:+.1f}%** growth")

# Key numbers: total growth for each chosen stock
cols = st.columns(len(chosen))
for col, t in zip(cols, chosen):
    growth = growths[t]
    col.metric(t, f"{df[t].iloc[-1]:.2f}x", f"{growth:+.1f}%")

# Line chart comparing the chosen stocks over time
fig = px.line(df, x="date", y=chosen, title="Normalized price over time")
st.plotly_chart(fig, use_container_width=True)

st.info("💡 Did you know? Microsoft was founded on April 4, 1975 in Albuquerque, New Mexico — not Seattle — by Bill Gates and Paul Allen. (Source: Wikipedia)")
