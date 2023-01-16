import pytest
import ssl
import statsmodels.api as sm
from datetime import date

import pandas as pd
import os

CACHE_DIR = ".cache"
CACHE_IRIS_DF = ".cache/iris.data"

def pytest_configure(config):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

@pytest.fixture(scope="session")
def loaded_iris_df() -> pd.DataFrame:
    """
    Tries to load the iris dataset from a cached file if it can,
    if not, loads it from the web.
    """
    df = None
    if os.path.exists(CACHE_IRIS_DF):
        df = pd.read_pickle(CACHE_IRIS_DF)
    else:
        df = load_iris_df_from_web()
        df.to_pickle(CACHE_IRIS_DF)

    return df


def load_iris_df_from_web() -> pd.DataFrame:
    """
    Loads the iris dataset from the web.
    """
    # Python on macOS needs to have certificates installed.
    # This can be done in the OS, or we can allow unsafe certificates.
    # See: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
    ssl._create_default_https_context = ssl._create_unverified_context
    df = sm.datasets.get_rdataset('iris').data

    return df

@pytest.fixture
def iris_df(loaded_iris_df : pd.DataFrame):
    """
    Returns a copy of the iris dataset.
    """
    df_copy = loaded_iris_df.copy(deep=True)
    return df_copy

@pytest.fixture
def iris_plus_df(iris_df: pd.DataFrame):
    """
    Returns a copy of the iris dataset with extra columns for id and dates.
    """
    iris_df["id"] = str(iris_df.index + 1)
    iris_df["date"] = date.today()
    iris_df["datetime"] = date.today().ctime()
    iris_df["datestring"] = date.today().isoformat()

    return iris_df

