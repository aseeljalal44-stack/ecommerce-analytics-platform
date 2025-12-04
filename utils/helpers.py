# utils/helpers.py
import pandas as pd
from typing import Any

def prepare_dataframe_display(df: pd.DataFrame, max_rows: int = 100):
    if len(df) > max_rows:
        return df.head(max_rows)
    return df

def validate_file_upload(uploaded_file) -> dict:
    # wrapper to use EcommerceValidators if needed externally
    from .validators import EcommerceValidators
    return EcommerceValidators.validate_file_upload(uploaded_file)