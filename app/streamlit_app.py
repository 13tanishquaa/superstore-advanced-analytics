# ======================================================
# RetailPulse — Executive Retail Analytics Platform
# ======================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import joblib
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ======================================================
# APP CONFIG
# ======================================================
st.set_page_config(
    page_title="RetailPulse",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# GLOBAL CSS (HIDE STREAMLIT UI + EXECUTIVE THEME)
# ======================================================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.kpi-card {
    background: linear-gradient(135deg, #161b22, #1f2630);
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.06);
}

.kpi-label {
    font-size: 12px;
    color: #9aa0a6;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.kpi-value {
    font-size: 30px;
    font-weight: 600;
    color: #ffffff;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# SESSION STATE
# ======================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "Executive"

# ======================================================
# LOGIN PAGE
# ======================================================
def login_page():
    st.markdown("<h1 style='text-align:center;'>RetailPulse</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#9aa0a6;'>Executive Retail Intelligence Platform</p>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if user == "admin" and pwd == "1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")

if not st.session_state.authenticated:
    login_page()
    st.stop()

# ======================================================
# DATA LOADING (SINGLE SOURCE OF TRUTH)
# ======================================================
monthly_metrics = pd.read_csv(
    PROJECT_ROOT / "data/processed/executive_metrics_monthly.csv",
    parse_dates=["Order_Month"]
)


# Latest month = executive snapshot
latest = monthly_metrics.iloc[-1]


# Other datasets
rfm = pd.read_csv(BASE_DIR / "data/processed/customer_rfm.csv")

# ======================================================
# SIDEBAR NAVIGATION
# ======================================================
with st.sidebar:
    st.markdown("## RetailPulse")
    st.markdown(
        "<p style='color:#9aa0a6;font-size:13px;'>Executive Analytics</p>",
        unsafe_allow_html=True
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("Executive Overview", use_container_width=True):
        st.session_state.page = "Executive"

    if st.button("Sales Performance", use_container_width=True):
        st.session_state.page = "Sales"

    if st.button("Sales Forecasting", use_container_width=True):
        st.session_state.page = "Forecast"

    if st.button("Customer Insights", use_container_width=True):
        st.session_state.page = "Customers"

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ======================================================
# KPI CARD COMPONENT
# ======================================================
def kpi(label, value, delta=None):
    delta_html = ""
    if delta is not None:
        color = "#16a34a" if delta >= 0 else "#dc2626"
        sign = "+" if delta >= 0 else ""
        delta_html = f"""
        <div style="font-size:13px;color:{color};margin-top:6px;">
            {sign}{delta*100:.1f}% MoM
        </div>
        """

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# ======================================================
def executive_page():
    st.markdown("## Executive Overview")
    st.caption("High-level view of business health and momentum")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi(
            "Total Sales",
            f"${latest['total_sales']:,.0f}",
            latest["sales_mom"]
        )

    with c2:
        kpi(
            "Total Profit",
            f"${latest['total_profit']:,.0f}",
            latest["profit_mom"]
        )

    with c3:
        kpi(
            "Profit Margin",
            f"{latest['profit_margin'] * 100:.2f}%"
        )

    with c4:
        kpi(
            "Sales MoM Growth",
            f"{latest['sales_mom'] * 100:.1f}%"
        )

    with c5:
        kpi(
            "Profit MoM Growth",
            f"{latest['profit_mom'] * 100:.1f}%"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------
    # Indexed trend (single-axis, exec-safe)
    # -------------------------------
    df = monthly_metrics.copy()

    df["Sales_Index"] = df["total_sales"] / df["total_sales"].iloc[0] * 100
    df["Profit_Index"] = df["total_profit"] / df["total_profit"].iloc[0] * 100

    fig = px.line(
        df,
        x="Order_Month",
        y=["Sales_Index", "Profit_Index"],
        template="plotly_dark",
        title="Revenue vs Profit Growth (Indexed to Base Period)"
    )

    fig.update_traces(line=dict(width=3))
    fig.update_layout(
        yaxis_title="Index (Base = 100)",
        hovermode="x unified",
        legend_title_text=""
    )

    st.plotly_chart(fig, use_container_width=True)
# ======================================================
# PAGE 2 — SALES PERFORMANCE
# ======================================================
def sales_page():
    st.markdown("## Sales Performance")
    st.caption("Operational drivers behind revenue and profitability")

    df = pd.read_csv(BASE_DIR / "data/processed/featured_data.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"])

    category = df.groupby("Category").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()

    fig1 = px.bar(
        category,
        x="Category",
        y="Sales",
        template="plotly_dark",
        title="Revenue by Product Category"
    )
    st.plotly_chart(fig1, use_container_width=True)

    region = df.groupby("Region").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()

    fig2 = px.scatter(
        region,
        x="Sales",
        y="Profit",
        size="Sales",
        template="plotly_dark",
        title="Sales vs Profit by Region"
    )
    st.plotly_chart(fig2, use_container_width=True)

    margin = (
        df.groupby("Category")
        .apply(lambda x: x.Profit.sum() / x.Sales.sum())
        .reset_index(name="Profit Margin")
    )

    fig3 = px.bar(
        margin,
        x="Category",
        y="Profit Margin",
        template="plotly_dark",
        title="Profit Efficiency by Category"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ======================================================
# PAGE 3 — SALES FORECASTING 
# ======================================================
def forecast_page():
    st.markdown("## Sales Forecasting")
    st.caption("Forward-looking revenue estimates for planning and risk assessment")

    model = joblib.load(BASE_DIR / "models/sales_forecasting.pkl")

    df = pd.read_csv(
        BASE_DIR / "data/processed/featured_data.csv",
        parse_dates=["Order Date"]
    )

    monthly = df.groupby(pd.Grouper(key="Order Date", freq="ME")).agg(
        Actual_Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Discount=("Discount", "mean"),
        Quantity=("Quantity", "sum")
    ).reset_index()

    monthly["profit_margin"] = monthly.Profit / (monthly.Profit.abs() + 1)
    monthly["month"] = monthly["Order Date"].dt.month
    monthly["year"] = monthly["Order Date"].dt.year

    X = monthly[["Profit", "Discount", "Quantity", "profit_margin", "month", "year"]]
    monthly["Predicted Sales"] = model.predict(X)

    monthly["Upper_Bound"] = monthly["Predicted Sales"] * 1.12
    monthly["Lower_Bound"] = monthly["Predicted Sales"] * 0.88

    latest_actual = monthly.iloc[-1]["Actual_Sales"]
    next_forecast = monthly.iloc[-1]["Predicted Sales"]
    uncertainty = (
        monthly.iloc[-1]["Upper_Bound"] - monthly.iloc[-1]["Lower_Bound"]
    ) / next_forecast

    c1, c2, c3 = st.columns(3)
    c1.metric("Last Month Sales", f"${latest_actual:,.0f}")
    c2.metric("Next Month Forecast", f"${next_forecast:,.0f}")
    c3.metric("Forecast Uncertainty", f"{uncertainty*100:.1f}%")

    plot_df = monthly.tail(18)

    fig = px.line(
        plot_df,
        x="Order Date",
        y=["Actual_Sales", "Predicted Sales"],
        template="plotly_dark",
        title="Actual vs Forecasted Sales"
    )

    fig.update_traces(line=dict(width=3))
    fig.update_layout(hovermode="x unified")

    st.plotly_chart(fig, use_container_width=True)

# ======================================================
# PAGE 4 — CUSTOMER INSIGHTS
# ======================================================
def customer_page():
    st.markdown("## Customer Insights")
    st.caption("Customer value, risk, and retention strategy")

    # ----------------------------------
    # Persona Mapping
    # ----------------------------------
    persona_map = {
        0: "Champions",
        1: "Loyal",
        2: "At Risk",
        3: "New"
    }
    rfm["Persona"] = rfm["Segment"].map(persona_map)

    # ----------------------------------
    # CLV Proxy
    # ----------------------------------
    rfm["CLV_Proxy"] = rfm["Monetary"] * rfm["Frequency"]

    # ----------------------------------
    # Concentration Metric (Top 20%)
    # ----------------------------------
    top_20 = rfm.sort_values("Monetary", ascending=False).head(int(len(rfm) * 0.2))
    concentration = top_20["Monetary"].sum() / rfm["Monetary"].sum()

    # ----------------------------------
    # KPI Row
    # ----------------------------------
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Customers",
        rfm["Customer ID"].nunique()
    )

    c2.metric(
        "Revenue from Top 20%",
        f"{concentration * 100:.1f}%"
    )

    c3.metric(
        "At-Risk Customers",
        (rfm["Persona"] == "At Risk").sum()
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------
    # Customer Segment Distribution
    # ----------------------------------
    fig1 = px.pie(
        rfm,
        names="Persona",
        template="plotly_dark",
        title="Customer Segment Distribution"
    )

    fig1.update_traces(textinfo="percent+label")
    fig1.update_layout(showlegend=False)

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------
    # Executive CLV View (Median, Ranked)
    # ----------------------------------
    clv_summary = (
        rfm.groupby("Persona", as_index=False)
        .agg(
            Median_CLV=("CLV_Proxy", "median"),
            Avg_CLV=("CLV_Proxy", "mean")
        )
        .sort_values("Median_CLV", ascending=False)
    )

    fig2 = px.bar(
        clv_summary,
        x="Persona",
        y="Median_CLV",
        text=clv_summary["Median_CLV"].round(0),
        template="plotly_dark",
        title="Median Customer Lifetime Value by Segment"
    )

    fig2.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig2.update_layout(
        yaxis_title="Median Customer Lifetime Value",
        xaxis_title="Customer Segment",
        uniformtext_minsize=10,
        uniformtext_mode="hide"
    )

    st.plotly_chart(fig2, use_container_width=True)
# ======================================================
# ROUTER
# ======================================================
if st.session_state.page == "Executive":
    executive_page()

elif st.session_state.page == "Sales":
    sales_page()

elif st.session_state.page == "Forecast":
    forecast_page()

elif st.session_state.page == "Customers":
    customer_page()
