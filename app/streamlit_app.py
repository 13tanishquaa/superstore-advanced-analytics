import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# PATHS
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = DATA_DIR / "results"

# APP CONFIG
st.set_page_config(
    page_title="RetailPulse",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}

.kpi-card {
    background: linear-gradient(135deg, #161b22, #1f2630);
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.06);
}

.kpi-label {
    font-size: 12px;
    color: #9aa0a6;
    text-transform: uppercase;
}

.kpi-value {
    font-size: 30px;
    font-weight: 600;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "Executive"

# LOGIN
def login_page():
    st.markdown("<h1 style='text-align:center;'>RetailPulse</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#9aa0a6;'>Executive Retail Intelligence Platform</p>",
        unsafe_allow_html=True
    )

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

# DATA LOADING 
@st.cache_data
def load_data():
    return {
        "executive": pd.read_csv(
            PROCESSED_DIR / "executive_metrics_monthly.csv",
            parse_dates=["Order_Month"]
        ),
        "sales": pd.read_csv(
            PROCESSED_DIR / "featured_data.csv",
            parse_dates=["Order Date"]
        ),
        "forecast": pd.read_csv(
            RESULTS_DIR / "predictions.csv",
            parse_dates=["Order Date"]
        ),
        "customers": pd.read_csv(
            PROCESSED_DIR / "customer_business_insights.csv"
        ),
        "customer_kpis": pd.read_csv(
            PROCESSED_DIR / "customer_kpis.csv"
        )
    }

data = load_data()

# SIDEBAR
with st.sidebar:
    st.markdown("## RetailPulse")
    st.markdown("<hr>", unsafe_allow_html=True)

    for page in ["Executive", "Sales", "Forecast", "Customers"]:
        if st.button(page + " Overview", use_container_width=True):
            st.session_state.page = page

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# KPI COMPONENT
def kpi(label, value):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# EXECUTIVE OVERVIEW
def executive_page():
    st.markdown("## Executive Overview")
    st.caption("Business health, momentum, and profitability")

    df = data["executive"]
    latest = df.iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    kpi("Total Sales", f"${latest['total_sales']:,.0f}")
    kpi("Total Profit", f"${latest['total_profit']:,.0f}")
    kpi("Profit Margin", f"{latest['profit_margin']*100:.2f}%")
    kpi("Sales MoM Growth", f"{latest['sales_mom']*100:.1f}%")

    df["Sales_Index"] = df.total_sales / df.total_sales.iloc[0] * 100
    df["Profit_Index"] = df.total_profit / df.total_profit.iloc[0] * 100

    fig = px.line(
        df,
        x="Order_Month",
        y=["Sales_Index", "Profit_Index"],
        template="plotly_dark",
        title="Growth Trajectory (Indexed)"
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

# SALES PERFORMANCE
def sales_page():
    st.markdown("## Sales Performance")

    df = data["sales"]

    # EXECUTIVE KPIs
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    profit_margin = total_profit / total_sales

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"${total_sales:,.0f}")
    c2.metric("Total Profit", f"${total_profit:,.0f}")
    c3.metric("Overall Margin", f"{profit_margin*100:.1f}%")

    st.caption(
        "Revenue shows scale, profit shows health, and margin reflects pricing efficiency."
    )

    # VISUAL 1: CATEGORY PERFORMANCE
    category = (
        df.groupby("Category", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    )

    fig1 = px.bar(
        category,
        x="Category",
        y="Sales",
        color="Profit",
        template="plotly_dark",
        title="Revenue by Category (Profit-Aware)"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # VISUAL 2: REGION PROFIT MAP
    region = (
        df.groupby("Region", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    )

    fig2 = px.scatter(
        region,
        x="Sales",
        y="Profit",
        size="Sales",
        color="Region",
        template="plotly_dark",
        title="Regional Sales vs Profit Efficiency"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.caption(
        "Top-right regions generate both scale and profit. "
        "High-sales but low-profit regions need pricing or cost correction."
    )

    # VISUAL 3: DISCOUNT IMPACT 
    df_discount = df.copy()

    df_discount["Discount_Band"] = pd.cut(
        df_discount["Discount"],
        bins=[0, 0.2, 0.4, 0.6, 1],
        labels=["0–20%", "20–40%", "40–60%", "60%+"],
        include_lowest=True
    )

    discount_effect = (
        df_discount
        .groupby("Discount_Band", as_index=False)
        .agg(
            Avg_Sales=("Sales", "mean"),
            Avg_Profit=("Profit", "mean")
        )
    )

    fig3 = px.line(
        discount_effect,
        x="Discount_Band",
        y=["Avg_Sales", "Avg_Profit"],
        template="plotly_dark",
        title="Impact of Discounting on Sales & Profit"
    )

    fig3.update_traces(line=dict(width=3))
    st.plotly_chart(fig3, use_container_width=True)

    # PRODUCT PERFORMANCE INTELLIGENCE

    st.markdown("### Product Portfolio Performance")
    st.caption("Revenue vs profitability view to guide pricing, marketing, and portfolio decisions")

    product_perf = (
        df.groupby("Product Name", as_index=False)
        .agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Quantity_Sold=("Quantity", "sum")
    )
    )

    # PRODUCT PERFORMANCE INTELLIGENCE
    st.markdown("### Product Portfolio Intelligence")
    st.caption(
        "Identifies products that drive scale vs profitability to guide pricing, promotion, and assortment decisions"
    )

    product_perf = (
        df.groupby("Product Name", as_index=False)
        .agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Quantity_Sold=("Quantity", "sum")
        )
    )

    top_sales_product = product_perf.sort_values(
        "Total_Sales", ascending=False
    ).iloc[0]

    top_profit_product = product_perf.sort_values(
        "Total_Profit", ascending=False
    ).iloc[0]

    c1, c2 = st.columns(2)

    c1.metric(
        "Revenue Driver Product",
        top_sales_product["Product Name"],
        f"${top_sales_product['Total_Sales']:,.0f}"
    )

    c2.metric(
        "Profit Driver Product",
        top_profit_product["Product Name"],
        f"${top_profit_product['Total_Profit']:,.0f}"
    )

    # Top 10 Products Table
    st.markdown("#### Top 10 Products by Revenue")

    top10 = (
        product_perf
        .sort_values("Total_Sales", ascending=False)
        .head(10)
    )

    st.dataframe(
        top10.style.format({
            "Total_Sales": "${:,.0f}",
            "Total_Profit": "${:,.0f}",
            "Quantity_Sold": "{:,.0f}"
        }),
        use_container_width=True
    )


# SALES FORECASTING
def forecast_page():
    st.markdown("## Revenue Risk & Business Planning")

    df = data["forecast"].copy()
    df["Error"] = df["Sales"] - df["gbr_forecast"]
    df["Abs_Error"] = df["Error"].abs()

    # EXECUTIVE KPIs (DECISION LEVEL)
    total_forecast = df["gbr_forecast"].sum()
    total_actual = df["Sales"].sum()
    revenue_risk = df["Abs_Error"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Forecasted Revenue", f"${total_forecast:,.0f}")
    c2.metric("Revenue Volatility (Risk)", f"${revenue_risk:,.0f}")
    c3.metric(
        "Forecast Bias",
        "Over Forecast"
        if df["Error"].mean() < 0 else "Under Forecast"
    )

    # EXECUTIVE VISUAL 1:
    # ACTUAL vs FORECAST 
    fig1 = px.line(
        df,
        x="Order Date",
        y=["Sales", "gbr_forecast"],
        template="plotly_dark",
        title="Revenue Reality vs Planned Revenue"
    )
    fig1.update_traces(line=dict(width=3))
    st.plotly_chart(fig1, use_container_width=True)

    # EXECUTIVE VISUAL 2:
    # VOLATILITY HEAT 
    fig2 = px.bar(
        df,
        x="Order Date",
        y="Abs_Error",
        template="plotly_dark",
        title="Daily Revenue Volatility (Risk Exposure)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # EXECUTIVE VISUAL 3:
    # BEST / WORST CASE SCENARIOS
    scenario = pd.DataFrame({
        "Scenario": ["Best Case", "Planned", "Worst Case"],
        "Revenue": [
            total_forecast + revenue_risk,
            total_forecast,
            total_forecast - revenue_risk
        ]
    })

    fig3 = px.bar(
        scenario,
        x="Scenario",
        y="Revenue",
        template="plotly_dark",
        title="Revenue Scenarios for Planning"
    )
    st.plotly_chart(fig3, use_container_width=True)

# CUSTOMER INSIGHTS
def customer_page():
    st.markdown("## Customer Intelligence & Growth Strategy")

    rfm = data["customers"]
    kpis = data["customer_kpis"].iloc[0]

    # Top KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Customers", int(kpis["total_customers"]))
    c2.metric("Revenue from Top 20%", f"{kpis['revenue_concentration']*100:.1f}%")
    c3.metric("High-Risk Customers", int(kpis["high_risk_customers"]))

    # Segment Distribution
    fig1 = px.pie(
        rfm,
        names="Business_Action",
        template="plotly_dark",
        title="Customer Strategy Segmentation"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # CLV by Segment
    clv_seg = rfm.groupby("Business_Action", as_index=False)["CLV"].sum()

    fig2 = px.bar(
        clv_seg,
        x="Business_Action",
        y="CLV",
        template="plotly_dark",
        title="Customer Lifetime Value by Segment"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Churn Risk Table
    high_risk = rfm[rfm["Churn_Risk"] == 1].sort_values("Monetary", ascending=False).head(10)

    st.markdown("### 🚨 Top Revenue Customers at Churn Risk")
    st.dataframe(
        high_risk[["Customer ID", "Recency", "Frequency", "Monetary", "CLV"]],
        use_container_width=True
    )

    st.success(
        "🎯 **Action Plan**:\n"
        "- Retain high-CLV churn-risk customers immediately\n"
        "- Upsell loyal segments\n"
        "- Reduce dependency on top 20% revenue customers"
    )

# ROUTER
if st.session_state.page == "Executive":
    executive_page()
elif st.session_state.page == "Sales":
    sales_page()
elif st.session_state.page == "Forecast":
    forecast_page()
elif st.session_state.page == "Customers":
    customer_page()
