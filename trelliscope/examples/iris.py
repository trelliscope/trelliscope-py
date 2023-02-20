from trelliscope.trelliscope import Trelliscope
import pandas as pd
import os
from io import BytesIO
import pkgutil

BASE_OUTPUT_DIR = "test-build-output"

DATA_DIR = "./trelliscope/tests/external_data"
IRIS_DF_FILENAME = "iris.data"

def get_iris_df() -> pd.DataFrame:
    """
    Loads the iris dataset from a file in the test-data directory.
    """
    iris_path = os.path.join(DATA_DIR, IRIS_DF_FILENAME)
    df = pd.read_pickle(iris_path)

    return df

def main():
    print("Running Trelliscope Iris Example...")
    output_dir = os.path.join(os.getcwd(), BASE_OUTPUT_DIR)

    df = get_iris_df()
    name = "Iris"

    tr = Trelliscope(df, name, path=output_dir, debug=True).write_display()

if __name__ == "__main__":
    main()
