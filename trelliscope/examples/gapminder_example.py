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
    # TODO: Add some of the extra mutate columns here

    print(meta_df.head())

    # # grammar of wrangling
    # meta_dat <- gapminder|>
    # group_by(country, continent) |>
    # summarise(
    #     mean_lifeexp = mean(lifeExp),
    #     min_lifeexp = min(lifeExp),
    #     max_lifeexp = max(lifeExp),
    #     mean_gdp = mean(gdpPercap),
    #     first_year = min(year),
    #     latitude = first(latitude),
    #     longitude = first(longitude),
    #     .groups = "drop"
    # ) |>
    # ungroup() |>
    # mutate(
    #     first_date = as.Date(paste0(first_year, "-01-01")),
    #     first_datetime = as.POSIXct.Date(first_date),
    #     continent = as.factor(continent),
    #     wiki_link = paste0("https://en.wikipedia.org/wiki/", country)
    # )
    
    # Join metas with panels
    joined_df = meta_df.join(panel_df)
    joined_df = joined_df.reset_index()
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