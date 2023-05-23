import os
import shutil
import pandas as pd
from gapminder import gapminder
import plotly.express as px
from trelliscope.facets import facet_panels, write_panels
from trelliscope.trelliscope import Trelliscope
from trelliscope.panels import FigurePanel

BASE_OUTPUT_DIR = "test-build-output"

def main():
    image_dir = "test-build-image-output"
    output_dir = os.path.join(os.getcwd(), image_dir)

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

    df = gapminder
    df = df[:200]
    print(df.columns)

    # Grammar of graphics
    panel_df = facet_panels(df, ["country", "continent"], px.scatter, {"x": "year", "y": "lifeExp"})
    #write_panels(panel_df, output_dir)

    # Grammar of wrangling
    meta_df = df.groupby(["country", "continent"]).agg(
        mean_lifeExp = ("lifeExp", "mean"),
        min_lifeExp = ("lifeExp", "min"),
        max_lifeExp = ("lifeExp", "max"),
        mean_gdp = ("gdpPercap", "mean"),
        first_year = ("year", "min"),
        # latitude = ("latitude", "first"),
        # longitude = ("longitude", "first")
    )

    meta_df = meta_df.reset_index()
    meta_df["first_date"] = pd.to_datetime(meta_df["first_year"], format='%Y')
    # meta_df["continent"] = meta_df["continent"].astype("category")
    meta_df["wiki"] = meta_df["country"].apply(lambda x: f"https://en.wikipedia.org/wiki/{x}")
    meta_df = meta_df.set_index(["country", "continent"])

    print(meta_df.head())

    
    # Join metas with panels
    joined_df = meta_df.join(panel_df)
    # joined_df = joined_df.reset_index()
    print(joined_df.head())

    output_dir = os.path.join(os.getcwd(), BASE_OUTPUT_DIR)

    # Grammar of Dashboard
    tr = (Trelliscope(joined_df, name="gapminder", path=output_dir, pretty_meta_data=True)
          .set_panel(FigurePanel("facet_plot"))
          .write_display()
    )

    # # grammar of dashboard
    # trell <- joined_dat |>
    # as_trelliscope_df(name = "gapminder") |>
    # write_panels() |>
    # write_trelliscope()
    # view_trelliscope()

if __name__ == "__main__":
    main()