from __future__ import annotations

import pkgutil
from io import BytesIO

import pandas as pd

# How to load a static file in a python package?
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
# In particular: https://stackoverflow.com/a/58941536
CURRENCY_FILE = "external_data/currencies.csv"


def get_valid_currencies() -> list[str]:
    """Get a list of pre-defined currencies.

    Returns:
        A list of the ISO 4217 alpha code of common currencies.
    """
    data = pkgutil.get_data(__name__, CURRENCY_FILE)
    currency_df = pd.read_csv(BytesIO(data))

    result = currency_df["code_alpha"].dropna().unique()
    return result.tolist()
