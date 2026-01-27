import pandas as pd
def clean_data(df):
    df = df.drop_duplicates()
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df = df[df['Ship Date'] >= df['Order Date']]
    return df
