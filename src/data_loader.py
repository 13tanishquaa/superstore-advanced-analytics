import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "SuperStoreDataset.csv"

def load_raw_data() -> pd.DataFrame:
    """
    Load raw SuperStore data with robust encoding handling.
    """

    try:
        df = pd.read_csv(RAW_DATA_PATH, encoding="utf-8")
        print("✅ Data loaded using UTF-8 encoding")
    except UnicodeDecodeError:
        df = pd.read_csv(RAW_DATA_PATH, encoding="latin-1")
        print("⚠️ UTF-8 failed. Data loaded using LATIN-1 encoding")

    return df
