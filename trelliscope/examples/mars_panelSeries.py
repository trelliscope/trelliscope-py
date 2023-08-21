from trelliscope.trelliscope import Trelliscope
from trelliscope.panel_series import ImagePanelSeries
import pandas as pd
import os
from io import BytesIO
import pkgutil

BASE_OUTPUT_DIR = "test-build-output"

DATA_DIR = "./trelliscope/tests/external_data"
MARS_ROVER_DF_FILENAME = "mars_rover.csv"

def get_mars_rover_df() -> pd.DataFrame:
    """
    Loads the Mars Rover dataset from a file in the test-data directory.
    """
    df_path = os.path.join(DATA_DIR, MARS_ROVER_DF_FILENAME)
    df = pd.read_csv(df_path)

    return df

def main():
    print("Running Trelliscope Mars Rover Example...")
    output_dir = os.path.join(os.getcwd(), BASE_OUTPUT_DIR)

    df = get_mars_rover_df()

    df["img_src"] = ImagePanelSeries(df["img_src"])

    name = "mars rover"

    # Grammar of Dashboard
    # Note that the image column will be found and inferred to be the panel
    tr = (Trelliscope(df, name, path=output_dir, pretty_meta_data=True)
          .write_display()
          .view_trelliscope()
    )

    print(f"Trelliscope saved to: {tr.get_output_path()}")
    
if __name__ == "__main__":
    main()
