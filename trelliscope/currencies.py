import pkgutil
from io import BytesIO

import pandas as pd

# How to load a static file in a python package?
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
# In particular: https://stackoverflow.com/a/58941536
CURRENCY_FILE = "external_data/currencies.csv"


def get_valid_currencies() -> list():
    data = pkgutil.get_data(__name__, CURRENCY_FILE)
    currency_df = pd.read_csv(BytesIO(data))

    result = currency_df["code_alpha"].dropna().unique()
    return result.tolist()
