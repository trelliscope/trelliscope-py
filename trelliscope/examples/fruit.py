from trelliscope.trelliscope import Trelliscope
import pandas as pd
import os
import json

BASE_OUTPUT_DIR = "test-build-output"

def get_data_frame():
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

    df = get_data_frame()
    name = "Fruit"

    # TODO: Use an img_panel function from the Trelliscope library
    df["panel"] = df["img"]

    tr = Trelliscope(df, name, path=output_dir, debug=True).write_display()
    # tr.set_default_label("name")

    # tr.write_trelliscope(output_dir)

    # # print(df.to_json(orient="records"))

if __name__ == "__main__":
    main()
