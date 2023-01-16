import pytest
import ssl
import statsmodels.api as sm

import pandas as pd
import os

CACHE_DIR = ".cache"
CACHE_IRIS_DF = ".cache/iris.data"

def pytest_configure(config):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

@pytest.fixture(scope="session")
def loaded_iris_df() -> pd.DataFrame:
    df = None
    if os.path.exists(CACHE_IRIS_DF):
        df = pd.read_pickle(CACHE_IRIS_DF)
    else:
        df = load_iris_df_from_web()
        df.to_pickle(CACHE_IRIS_DF)

    return df


def load_iris_df_from_web() -> pd.DataFrame:
    # Python on macOS needs to have certificates installed.
    # This can be done in the OS, or we can allow unsafe certificates.
    # See: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
    ssl._create_default_https_context = ssl._create_unverified_context
    df = sm.datasets.get_rdataset('iris').data

    return df

@pytest.fixture
def iris_df(loaded_iris_df : pd.DataFrame):
    df_copy = loaded_iris_df.copy(deep=True)
    return df_copy


