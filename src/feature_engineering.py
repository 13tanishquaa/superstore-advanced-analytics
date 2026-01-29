def add_time_features(df):
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['order_year'] = df['Order Date'].dt.year
    df['order_month'] = df['Order Date'].dt.month
    df['order_quarter'] = df['Order Date'].dt.quarter
    return df
