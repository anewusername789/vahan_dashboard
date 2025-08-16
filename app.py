import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_data
from analytics import filter_range, qoq_growth, yoy_growth, kpi_latest_delta

st.set_page_config(page_title="VAHAN Investor Dashboard", layout="wide")

@st.cache_data
def get_data():
    return load_data()

df = get_data()

st.title("📊 VAHAN-style Vehicle Registrations — Investor Dashboard")
st.caption("Demo with sample data. Replace CSV with scraped VAHAN data for final submission.")

# --- Sidebar Filters ---
st.sidebar.header("Filters")
categories_all = sorted(df["category"].unique().tolist())
manufacturers_all = sorted(df["manufacturer"].unique().tolist())

sel_categories = st.sidebar.multiselect("Vehicle Categories", categories_all, default=categories_all)
sel_manufs = st.sidebar.multiselect("Manufacturers", manufacturers_all, default=manufacturers_all)

# Date range using quarters
min_p, max_p = df["period"].min(), df["period"].max()
start_p = st.sidebar.selectbox("Start Period", pd.period_range(min_p, max_p, freq="Q"), index=0)
end_p = st.sidebar.selectbox("End Period", pd.period_range(min_p, max_p, freq="Q"), index=len(pd.period_range(min_p, max_p, freq="Q"))-1)

# Apply filters
base = df[(df["category"].isin(sel_categories)) & (df["manufacturer"].isin(sel_manufs))]
base = filter_range(base, start_p, end_p)

# --- KPI row (Totals for visible slice) ---
latest, delta, pct = kpi_latest_delta(base)
k1, k2, k3 = st.columns(3)
k1.metric("Latest Quarter Registrations (All Visible)", f"{latest:,}")
k2.metric("Δ vs Prev Quarter", f"{delta:+,}")
k3.metric("% Change QoQ", f"{pct:+.2f}%")

st.divider()

tab1, tab2 = st.tabs(["🔹 By Category (Totals)", "🔸 By Manufacturer"])

# ===== TAB 1: Total vehicles by Category =====
with tab1:
    st.subheader("Totals by Category — Trends & Growth")

    # Aggregate by category x period
    by_cat = base.groupby(["category", "period"], as_index=False)["registrations"].sum()
    by_cat["period_str"] = by_cat["period"].astype(str)

    # Plot trends
    fig1 = px.line(by_cat, x="period_str", y="registrations", color="category", markers=True,
                   title="Registrations over Time by Category")
    st.plotly_chart(fig1, use_container_width=True)

    # QoQ & YoY
    qoq_cat = qoq_growth(base, ["category"])
    yoy_cat = yoy_growth(base, ["category"])

    cat_growth = (qoq_cat
                  .merge(yoy_cat[["category","period","registrations","YoY_%"]],
                         on=["category","period","registrations"], how="left"))
    cat_growth["period_str"] = cat_growth["period"].astype(str)

    st.write("**Category Growth (QoQ & YoY)**")
    st.dataframe(cat_growth.sort_values(["category","period"]))

    # % change chart (QoQ)
    fig1b = px.bar(cat_growth, x="period_str", y="QoQ_%", color="category",
                   title="QoQ % Change by Category", barmode="group")
    st.plotly_chart(fig1b, use_container_width=True)

# ===== TAB 2: Per Manufacturer (within selected categories) =====
with tab2:
    st.subheader("Per Manufacturer — Trends & Growth")

    by_m = base.groupby(["manufacturer", "period"], as_index=False)["registrations"].sum()
    by_m["period_str"] = by_m["period"].astype(str)

    fig2 = px.line(by_m, x="period_str", y="registrations", color="manufacturer", markers=True,
                   title="Registrations over Time by Manufacturer")
    st.plotly_chart(fig2, use_container_width=True)

    qoq_m = qoq_growth(base, ["manufacturer"])
    yoy_m = yoy_growth(base, ["manufacturer"])

    manu_growth = (qoq_m
                   .merge(yoy_m[["manufacturer","period","registrations","YoY_%"]],
                          on=["manufacturer","period","registrations"], how="left"))
    manu_growth["period_str"] = manu_growth["period"].astype(str)

    st.write("**Manufacturer Growth (QoQ & YoY)**")
    st.dataframe(manu_growth.sort_values(["manufacturer","period"]))

    fig2b = px.bar(manu_growth, x="period_str", y="QoQ_%", color="manufacturer",
                   title="QoQ % Change by Manufacturer", barmode="group")
    st.plotly_chart(fig2b, use_container_width=True)

st.info("Tip: Narrow the date range or select a single category/manufacturer to get sharp investor insights.")
