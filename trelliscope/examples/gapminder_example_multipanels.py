import os
import shutil
import urllib.request
import zipfile
import pandas as pd
import plotly.express as px
from trelliscope.facets import facet_panels
from trelliscope.trelliscope import Trelliscope
from trelliscope.state import NumberRangeFilterState

BASE_OUTPUT_DIR = "test-build-output"
DOWNLOAD_FLAGS = True

def main():
    image_dir = "test-build-image-output"
    output_dir = os.path.join(os.getcwd(), image_dir)

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

    # TODO: Prepare this example to run in other environments
    gapminder = pd.read_csv("./trelliscope/examples/external_data/gapminder.csv")

    df = gapminder

    # Take a subset of the data to make testing faster
    df = df[:200]
    print(df.columns)

    # Grammar of graphics
    panel_df = facet_panels(df, "lifeExp_time", ["country", "continent", "iso_alpha2"], px.scatter, {"x": "year", "y": "lifeExp"})

    print(panel_df.columns)

    # Grammar of wrangling
    meta_df = df.groupby(["country", "continent", "iso_alpha2"]).agg(
        mean_lifeExp = ("lifeExp", "mean"),
        min_lifeExp = ("lifeExp", "min"),
        max_lifeExp = ("lifeExp", "max"),
        mean_gdp = ("gdpPercap", "mean"),
        first_year = ("year", "min"),
        latitude = ("latitude", "first"),
        longitude = ("longitude", "first")
    )

    meta_df = meta_df.reset_index()
    meta_df["first_date"] = pd.to_datetime(meta_df["first_year"], format='%Y')
    meta_df["wiki"] = meta_df["country"].apply(lambda x: f"https://en.wikipedia.org/wiki/{x}")
    meta_df["country"] = meta_df["country"].astype("category")
    meta_df["continent"] = meta_df["continent"].astype("category")


    if DOWNLOAD_FLAGS:
        print("Downloading flag images...")
        (zip_file, _) = urllib.request.urlretrieve("https://github.com/trelliscope/trelliscope/files/12265140/flags.zip")
        local_flags_path = os.path.join(BASE_OUTPUT_DIR, "temp_flag_images")

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(local_flags_path)

        meta_df["flag"] = meta_df["iso_alpha2"].apply(lambda x: os.path.join(local_flags_path, f"{x}.png"))
        print(meta_df["flag"].head())

    flag_base_url = "https://raw.githubusercontent.com/hafen/countryflags/master/png/512/"
    meta_df["flag_url"] = meta_df["iso_alpha2"].apply(lambda x: f"{flag_base_url}{x}.png")

    meta_df = meta_df.set_index(["country", "continent", "iso_alpha2"])

    # Join metas with panels
    joined_df = meta_df.join(panel_df)
    print(joined_df.head())

    output_dir = os.path.join(os.getcwd(), BASE_OUTPUT_DIR)

    ########################
    # Grammar of Dashboard
    ########################

    # Simple example (using defaults)
    # tr = (Trelliscope(joined_df, name="gapminder", path=output_dir, pretty_meta_data=True)
    #       .write_display()
    #       .view_trelliscope()
    # )

    # Setting various parameters explicitly
    tr = (Trelliscope(joined_df, name="gapminder", path=output_dir, pretty_meta_data=True)
          .set_default_labels(["country", "continent"])
          .set_default_layout(3)
          .set_default_sort(["continent", "mean_lifeExp"], sort_directions=["asc", "desc"])
          .set_default_filters([NumberRangeFilterState("mean_lifeExp", 30, 60)])
          .write_display()
          .view_trelliscope()
    )

if __name__ == "__main__":
    main()