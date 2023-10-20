from trelliscope import Trelliscope

import pandas as pd
import os

BASE_OUTPUT_DIR = "test-build-output"

def get_fruit_data_frame():
    data = [["apple", 1, 3, "red", "https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg"],
            ["banana", 3, 2, "yellow", "https://upload.wikimedia.org/wikipedia/commons/4/44/Bananas_white_background_DS.jpg"],
            ["pineapple", 5, 6, "brown", "https://upload.wikimedia.org/wikipedia/commons/2/20/Ananas_01.JPG"]
            ]
    columns = ["name", "size", "weight", "color", "img"]
    df = pd.DataFrame(data, columns=columns)

    return df

def main():
    print("Running Trelliscope Fruit Example...")
    output_dir = os.path.join(os.getcwd(), BASE_OUTPUT_DIR)

    df = get_fruit_data_frame()
    name = "Fruit"

    # Grammar of Dashboard
    # Note that the image column will be found and inferred to be the panel
    tr = (Trelliscope(df, name, path=output_dir, pretty_meta_data=True)
          .write_display()
          .view_trelliscope()
    )

if __name__ == "__main__":
    main()
