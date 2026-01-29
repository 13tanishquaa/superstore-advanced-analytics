import pandas as pd


# ---------------------------------------------------
# TIME-BASED FEATURES
# ---------------------------------------------------
def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds time-based features to capture seasonality and demand patterns.
    """
    df = df.copy()
    df['Order Date'] = pd.to_datetime(df['Order Date'])

    df['order_year'] = df['Order Date'].dt.year
    df['order_month'] = df['Order Date'].dt.month
    df['order_quarter'] = df['Order Date'].dt.quarter
    df['order_dayofweek'] = df['Order Date'].dt.dayofweek

    return df


# ---------------------------------------------------
# PROFIT & DISCOUNT FEATURES
# ---------------------------------------------------
def add_profit_discount_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds profitability and discount behavior features.
    """
    df = df.copy()

    df['profit_margin'] = df.apply(
        lambda x: x['Profit'] / x['Sales'] if x['Sales'] > 0 else 0,
        axis=1
    )

    df['is_discounted'] = (df['Discount'] > 0).astype(int)

    return df


# ---------------------------------------------------
# CUSTOMER AGGREGATION FEATURES
# ---------------------------------------------------
def create_customer_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates aggregated customer-level features for churn and segmentation.
    """
    customer_agg = df.groupby('Customer ID').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Discount': 'mean',
        'Order ID': 'nunique'
    }).reset_index()

    customer_agg.rename(columns={
        'Sales': 'total_sales',
        'Profit': 'total_profit',
        'Discount': 'avg_discount',
        'Order ID': 'num_orders'
    }, inplace=True)

    return customer_agg


# ---------------------------------------------------
# RFM FEATURE ENGINEERING
# ---------------------------------------------------
def create_rfm_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates RFM (Recency, Frequency, Monetary) features for customer segmentation.
    """
    df = df.copy()
    df['Order Date'] = pd.to_datetime(df['Order Date'])

    snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)

    rfm = df.groupby('Customer ID').agg({
        'Order Date': lambda x: (snapshot_date - x.max()).days,
        'Order ID': 'nunique',
        'Sales': 'sum'
    }).reset_index()

    rfm.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']

    return rfm


# ---------------------------------------------------
# MASTER FEATURE PIPELINE
# ---------------------------------------------------
def build_feature_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies all feature engineering steps required for modeling.
    """
    df = add_time_features(df)
    df = add_profit_discount_features(df)
    return df
