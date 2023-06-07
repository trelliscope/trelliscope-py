from trelliscope.trelliscope import Trelliscope
import pandas as pd
import os
from trelliscope.facets import facet_panels
import plotly.express as px
from io import BytesIO
import pkgutil

BASE_OUTPUT_DIR = "test-build-output"

DATA_DIR = "./trelliscope/tests/external_data"
IRIS_DF_FILENAME = "iris.data"

def main():
    output_dir = os.path.join(os.getcwd(), BASE_OUTPUT_DIR)
    iris_path = os.path.join(DATA_DIR, IRIS_DF_FILENAME)

    # Load dataset
    df:pd.DataFrame = pd.read_pickle(iris_path)
    df = df.drop_duplicates()
    name = "Iris"

    # Grammar of Graphics
    # This particular example isn't very great, because it just
    # plots a single dot in the middle of the plot for each row,
    # but it does render...
    all_columns = df.columns.to_list()
    panel_df = facet_panels(df, all_columns, px.scatter, {"x": "Sepal.Width", "y": "Sepal.Length"})

    # Grammar of Dashboard
    tr = (Trelliscope(panel_df, name, path=output_dir, pretty_meta_data=True)
          .write_display()
          .view_trelliscope()
    )

if __name__ == "__main__":
    main()
