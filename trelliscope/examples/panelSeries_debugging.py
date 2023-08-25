import pandas as pd
# from trelliscope import panel_accessor
from trelliscope.panel_series import PanelDataFrame
from trelliscope.panel_series import PanelSeries
#from trelliscope.panel_series import panel_local

def get_fruit_data_frame():
    data = [["apple", 1, 3, "red", "https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg"],
            ["banana", 3, 2, "yellow", "https://upload.wikimedia.org/wikipedia/commons/4/44/Bananas_white_background_DS.jpg"],
            ["pineapple", 5, 6, "brown", "https://upload.wikimedia.org/wikipedia/commons/2/20/Ananas_01.JPG"]
            ]
    columns = ["name", "size", "weight", "color", "img"]
    df = pd.DataFrame(data, columns=columns)
    # df = PanelDataFrame(df)
    return df

def main():
    print("\nPanelSeries Debugging Work")

    df = get_fruit_data_frame()
    print(df.head())

    # s = PanelSeries(df["img"], "the source")
    s = df["img"]
    s._metadata = [pa]
    s.attrs["panel_test"] = "test"
    # s = panel_local(df["img"], "the source")
    print(s.attrs["panel_test"])
    print(type(s))
    df["panel_img"] = s
    # print(s.attrs["panel_info"])
    print(df["panel_img"].attrs)

    print(type(df["img"]))
    print(type(df["panel_img"]))
    print(s.attrs)
    print(df["panel_img"].attrs)
    # print(df["panel_img"].attrs["panel_info"])

    # print(df["img"].panel)
    # df["img"].panel.method_test()
    # print(df["img"].panel.variable_test)
    # df["img"].panel.variable_test = "B"
    # print(df["img"].panel.variable_test)
    # print(df["name"].panel.variable_test)
    # print(df["img"].panel.variable_test)

if __name__ == "__main__":
    main()