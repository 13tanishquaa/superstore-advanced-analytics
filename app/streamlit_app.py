import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import requests
import plotly.express as px
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------
# Page Configuration
# ------------------------------------------------------
st.set_page_config(
    page_title="Superstore Advanced Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------
# Header
# ------------------------------------------------------
st.markdown(
    """
    <h1 style='text-align: center;'>Superstore Advanced Analytics Dashboard</h1>
    <p style='text-align: center; color: gray;'>
    Forecasting • Customer Segmentation • Executive Insights
    </p>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------
# Load Data & Models
# ------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(BASE_DIR / "data" / "processed" / "featured_data.csv")
    segments = pd.read_csv(BASE_DIR / "data" / "processed" / "customer_segments.csv")
    return df, segments


@st.cache_resource
def load_model():
    return joblib.load("models/sales_forecasting.pkl")

df, segments = load_data()
model = load_model()

# ------------------------------------------------------
# Sidebar Navigation
# ------------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select View",
    ["Executive Overview", "Sales Forecasting", "Customer Segmentation"]
)

# ------------------------------------------------------
# EXECUTIVE OVERVIEW (CLIENT-READY)
# ------------------------------------------------------
if page == "Executive Overview":

    st.title("📊 Executive Business Overview")
    st.caption("High-level performance snapshot for leadership decision-making")

    # --------------------------------------------------
    # Monthly Aggregation (Business Standard)
    # --------------------------------------------------
    df["Order Date"] = pd.to_datetime(df["Order Date"])

    monthly_summary = (
        df
        .groupby(pd.Grouper(key="Order Date", freq="ME"))
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Avg_Discount=("Discount", "mean"),
            Quantity=("Quantity", "sum")
        )
        .reset_index()
    )

    # --------------------------------------------------
    # KPI CARDS (EXECUTIVE LEVEL)
    # --------------------------------------------------
    total_sales = monthly_summary["Sales"].sum()
    total_profit = monthly_summary["Profit"].sum()
    avg_discount = monthly_summary["Avg_Discount"].mean()
    profit_margin = (total_profit / total_sales) * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
    col2.metric("📈 Total Profit", f"${total_profit:,.0f}")
    col3.metric("🏷 Avg Discount", f"{avg_discount:.1%}")
    col4.metric("📊 Profit Margin", f"{profit_margin:.1f}%")

    st.markdown("---")

    # --------------------------------------------------
    # SALES vs PROFIT TREND (INTERACTIVE)
    # --------------------------------------------------
    st.subheader("📈 Sales & Profit Trend (Monthly)")

    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly_summary["Order Date"],
            y=monthly_summary["Sales"],
            name="Sales",
            mode="lines+markers",
            line=dict(width=3)
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_summary["Order Date"],
            y=monthly_summary["Profit"],
            name="Profit",
            mode="lines+markers",
            yaxis="y2",
            line=dict(width=3, dash="dot")
        )
    )

    fig.update_layout(
        title="Monthly Sales vs Profit Performance",
        xaxis_title="Month",
        yaxis=dict(title="Sales"),
        yaxis2=dict(
            title="Profit",
            overlaying="y",
            side="right"
        ),
        template="plotly_white",
        height=500,
        legend=dict(orientation="h", y=-0.25)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # EXECUTIVE INSIGHTS (NON-TECHNICAL)
    # --------------------------------------------------
    st.subheader("🧠 Key Executive Insights")

    st.markdown("""
    - Sales show **clear seasonal patterns**, useful for inventory planning  
    - Profit does **not always increase proportionally** with sales  
    - Higher discount periods are associated with **margin pressure**  
    - Opportunity exists to **optimize discount strategy** without hurting revenue
    """)

    # --------------------------------------------------
    # STRATEGIC ACTIONS
    # --------------------------------------------------
    st.subheader("🎯 Recommended Business Actions")

    st.markdown("""
    ✅ Align inventory with seasonal demand patterns  
    ✅ Limit aggressive discounting during high-demand months  
    ✅ Focus promotions on **low-margin periods**  
    ✅ Monitor profit alongside sales, not independently
    """)

# ------------------------------------------------------
# SALES FORECASTING
# ------------------------------------------------------
elif page == "Sales Forecasting":

    st.subheader("Monthly Sales Forecast")

    df = pd.read_csv("data/processed/featured_data.csv")
    df['Order Date'] = pd.to_datetime(df['Order Date'])

    monthly = (
    df
    .groupby(pd.Grouper(key='Order Date', freq='ME'))
    .agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Discount': 'mean',
        'Quantity': 'sum',
        'profit_margin': 'mean'
    })
    .reset_index()
    )

    monthly['month'] = monthly['Order Date'].dt.month
    monthly['year'] = monthly['Order Date'].dt.year

    X = monthly.drop(columns=['Sales', 'Order Date'])
    model = joblib.load("models/sales_forecasting.pkl")
    monthly['Predicted Sales'] = model.predict(X)
    st.subheader("Monthly Sales: Actual vs Predicted")

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        monthly['Order Date'],
        monthly['Sales'],
        label='Actual Sales',
        marker='o'
    )

    ax.plot(
        monthly['Order Date'],
        monthly['Predicted Sales'],
        label='Predicted Sales',
        linestyle='--'
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Sales")
    ax.set_title("Monthly Sales Forecast (ML Model)")
    ax.legend()

    st.pyplot(fig)

# ------------------------------------------------------
# CUSTOMER SEGMENTATION
# ------------------------------------------------------
elif page == "Customer Segmentation":

    # -------------------------------
    # Title & Description
    # -------------------------------
    st.title("Customer Personas & Value Insights")
    st.caption("Executive-friendly view of customer value and retention risk")

    # -------------------------------
    # Load notebook output (SOURCE OF TRUTH)
    # -------------------------------
    rfm = pd.read_csv("data/processed/customer_rfm.csv")

    # -------------------------------
    # Map clusters to business personas
    # -------------------------------
    persona_map = {
        0: "💎 Champions",
        1: "🧍 Regular Customers",
        2: "💤 At-Risk Customers",
        3: "🆕 New Customers"
    }

    rfm["Persona"] = rfm["Segment"].map(persona_map)

    # -------------------------------
    # Executive KPI Cards
    # -------------------------------
    total_customers = rfm["Customer ID"].nunique()
    champion_pct = (rfm["Persona"] == "💎 Champions").mean() * 100
    at_risk_pct = (rfm["Persona"] == "💤 At-Risk Customers").mean() * 100
    avg_revenue = rfm["Monetary"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("High-Value Customers", f"{champion_pct:.1f}%")
    col3.metric("At-Risk Customers", f"{at_risk_pct:.1f}%")
    col4.metric("Avg Revenue / Customer", f"${avg_revenue:,.0f}")

    # -------------------------------
    # Persona Summary Table
    # -------------------------------
    st.subheader("Customer Persona Overview")

    persona_summary = (
        rfm
        .groupby("Persona")
        .agg(
            Customers=("Customer ID", "nunique"),
            Total_Revenue=("Monetary", "sum")
        )
        .reset_index()
    )

    persona_summary["Revenue Share (%)"] = (
        persona_summary["Total_Revenue"] / persona_summary["Total_Revenue"].sum() * 100
    )

    st.dataframe(
        persona_summary[["Persona", "Customers", "Revenue Share (%)"]],
        use_container_width=True
    )
    st.caption(
    "Each persona represents customers with similar buying behavior based on purchase recency, frequency, and spending."
)

    # -------------------------------
    # Customer Distribution Chart
    # -------------------------------
    st.subheader("Customer Distribution by Persona")

    fig1, ax1 = plt.subplots()
    rfm["Persona"].value_counts().plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax1
    )
    ax1.set_ylabel("")
    ax1.set_title("Customer Share by Persona")

    st.pyplot(fig1)

    # -------------------------------
    # Revenue Contribution Chart
    # -------------------------------
    st.subheader("Revenue Contribution by Persona")

    revenue_by_persona = (
        rfm
        .groupby("Persona")["Monetary"]
        .sum()
        .sort_values(ascending=False)
    )

    fig2, ax2 = plt.subplots()
    revenue_by_persona.plot(kind="bar", ax=ax2)
    ax2.set_ylabel("Total Revenue")
    ax2.set_xlabel("Customer Persona")
    ax2.set_title("Revenue by Customer Persona")

    st.pyplot(fig2)

    # -------------------------------
    # Business Action Playbook
    # -------------------------------
    st.subheader("Recommended Business Actions")

    st.markdown("""
    ### 💎 Champions
    - Focus on loyalty programs and early access
    - Avoid heavy discounts
    - Prioritize retention

    ### 🧍 Regular Customers
    - Upsell and cross-sell opportunities
    - Product bundles and personalized offers

    ### 💤 At-Risk Customers
    - Targeted win-back campaigns
    - Time-limited discounts
    - Proactive outreach

    ### 🆕 New Customers
    - Onboarding journeys
    - Education-focused campaigns
    - First-purchase incentives
    """)

# ------------------------------------------------------
# Footer
# ------------------------------------------------------
st.markdown(
    "<hr style='margin-top: 50px;'>"
    "<p style='text-align: center; color: gray;'>"
    "Built for real-world decision making • Internship-ready analytics project"
    "</p>",
    unsafe_allow_html=True
)
