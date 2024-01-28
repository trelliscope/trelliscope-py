import pandas as pd

from trelliscope import Trelliscope

EXTERNAL_DATA_DIR = "external_data"
MARS_ROVER_CSV_FILENAME = "mars_rover.csv"

MARS_ROVER_CSV_URL = "https://raw.githubusercontent.com/trelliscope/trelliscope-py/main/trelliscope/examples/external_data/mars_rover.csv"


def main():
    # Use a URL for the external file
    mars_file = MARS_ROVER_CSV_URL

    # If desired: Alternatively, use a the file locally, assuming the working directly is in the `examples` folder
    # mars_file = os.path.join(EXTERNAL_DATA_DIR, MARS_ROVER_CSV_FILENAME)

    mars_df = pd.read_csv(mars_file)

    # Note that the image column will be found and inferred to be the panel
    tr = Trelliscope(mars_df, name="Mars Rover").write_display().view_trelliscope()

    print(f"Trelliscope saved to: {tr.get_output_path()}")


if __name__ == "__main__":
    main()
