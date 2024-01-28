import os
import tempfile
import urllib.request
import zipfile

import pandas as pd
import plotly.express as px

from trelliscope import Trelliscope
from trelliscope.facets import facet_panels
from trelliscope.state import NumberRangeFilterState

# set up some constants for the example
use_small_dataset = False
use_single_panel_approach = False

GAPMINDER_CSV_URL = "https://raw.githubusercontent.com/trelliscope/trelliscope-py/main/trelliscope/examples/external_data/gapminder.csv"

EXTERNAL_DATA_DIR = "external_data"
GAPMINDER_CSV_FILENAME = "gapminder.csv"


def main():
    # Use a URL for the external file
    gapminder_file = GAPMINDER_CSV_URL

    # If desired: Alternatively, use a the file locally, assuming the working directly is in the `examples` folder
    # gapminder_file = os.path.join(EXTERNAL_DATA_DIR, GAPMINDER_CSV_FILENAME)

    gapminder = pd.read_csv(gapminder_file)

    if use_small_dataset:
        df = gapminder[:200]
    else:
        df = gapminder

    # Grammar of Graphics
    # Use facet_panels to create a Plotly Express graphic for each small data frame
    panel_df = facet_panels(
        df,
        "lifeExp_time",
        ["country", "continent", "iso_alpha2"],
        px.scatter,
        {"x": "year", "y": "lifeExp"},
    )

    print(panel_df.columns)
    print(panel_df.head())

    # Grammar of Wrangling
    meta_df = df.groupby(["country", "continent", "iso_alpha2"]).agg(
        mean_lifeExp=("lifeExp", "mean"),
        min_lifeExp=("lifeExp", "min"),
        max_lifeExp=("lifeExp", "max"),
        mean_gdp=("gdpPercap", "mean"),
        first_year=("year", "min"),
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
    )

    meta_df = meta_df.reset_index()
    meta_df["first_date"] = pd.to_datetime(meta_df["first_year"], format="%Y")
    meta_df["wiki"] = meta_df["country"].apply(
        lambda x: f"https://en.wikipedia.org/wiki/{x}"
    )
    meta_df["country"] = meta_df["country"].astype("category")
    meta_df["continent"] = meta_df["continent"].astype("category")

    if use_single_panel_approach:
        # This shows an example that uses only single panels
        meta_df = meta_df.set_index(["country", "continent"])
    else:
        # This shows an example that uses multiple panels

        # Download and extract flag images to a temporary directory
        (zip_file, _) = urllib.request.urlretrieve(
            "https://github.com/trelliscope/trelliscope/files/12265140/flags.zip"
        )
        local_flags_path = os.path.join(tempfile.mkdtemp(), "temp_flag_images")

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(local_flags_path)

        # The flag column will hold references to the local files
        meta_df["flag"] = meta_df["iso_alpha2"].apply(
            lambda x: os.path.join(local_flags_path, f"{x}.png")
        )

        # The `flag_base_url` column will hold references to the remote URLs
        flag_base_url = (
            "https://raw.githubusercontent.com/hafen/countryflags/master/png/512/"
        )
        meta_df["flag_url"] = meta_df["iso_alpha2"].apply(
            lambda x: f"{flag_base_url}{x}.png"
        )

        print(meta_df[["country", "flag", "flag_url"]].head())

        meta_df = meta_df.set_index(["country", "continent", "iso_alpha2"])

    # Join metas with panels
    joined_df = meta_df.join(panel_df)
    print(joined_df.head())

    ########################
    # Grammar of Dashboard
    ########################

    # Simple example (using defaults)
    # tr = (Trelliscope(joined_df, name="gapminder")
    #       .write_display()
    #       .view_trelliscope()
    # )

    # Setting various parameters explicitly
    tr = (
        Trelliscope(joined_df, name="gapminder")
        .set_default_labels(["country", "continent"])
        .set_default_layout(3)
        .set_default_sort(
            ["continent", "mean_lifeExp"], sort_directions=["asc", "desc"]
        )
        .set_default_filters([NumberRangeFilterState("mean_lifeExp", 30, 60)])
        #       .set_panel_options()
        .write_display()
        .view_trelliscope()
    )


if __name__ == "__main__":
    main()
