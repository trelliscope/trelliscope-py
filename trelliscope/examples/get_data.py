"""Get data that was included with the trelliscope-py package."""
from typing import Literal

import pandas as pd

try:
    import importlib.resources as importlib_resources
except ImportError:
    import importlib_resources

GAPMINDER_CSV_URL = "https://raw.githubusercontent.com/trelliscope/trelliscope-py/main/trelliscope/examples/external_data/gapminder.csv"


def get_example_data(
    dataset: Literal["mars_rover", "gapminder", "iris"],
) -> pd.DataFrame:
    """Get example dataframe from trelliscope-py.

    There are three datasets available for examples that are suitable
    for creating Trelliscope displays.

    mars_rover:
        Data from the Mars rover Curiosity that contains
        timestamp and urls to images.
    gapminder:
        Yearly data of countries worldwide, containing data such as population
        and life expectancy.
    iris:
        Classic dataset of flowers and their petal/sepal dimensions.

    Args:
        dataset: One of [`mars_rover`, `gapminder`, `iris`].

    Returns:
        A pandas dataframe with example data.

    Raises:
        ValueError: If `dataset` is not one of available options.
    """
    if dataset == "mars_rover":
        with importlib_resources.path(
            "trelliscope.examples.external_data", "mars_rover.csv"
        ) as data_filepath:
            df = pd.read_csv(data_filepath)
    elif dataset == "iris":
        with importlib_resources.path(
            "trelliscope.examples.external_data", "iris.csv"
        ) as data_filepath:
            df = pd.read_csv(data_filepath)
    elif dataset == "gapminder":
        df = pd.read_csv(GAPMINDER_CSV_URL)
    else:
        raise ValueError(
            f"{dataset=} must be one of ['mars_rover', 'gapminder', 'iris']"
        )
    return df
