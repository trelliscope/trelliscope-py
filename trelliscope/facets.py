import types
import os
import shutil
import pandas as pd

FACET_PLOT_COLUMN = "facet_plot"

def facet_panels(df: pd.DataFrame, panel_column_name:str, facet_columns:list, plot_function:types.FunctionType, params:dict) -> pd.DataFrame:
    result_df = df.groupby(facet_columns).apply(lambda mini_df: plot_function(mini_df, **params))
    result_df = result_df.to_frame(name = panel_column_name)
    return result_df

def write_panels(panel_df: pd.DataFrame, output_dir:str, extension:str = "png"):
    # Create the output directory if necessary
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    
    count = 0
    # for fig in panel_df:
    for index, row in panel_df.iterrows():
        fig = row[FACET_PLOT_COLUMN]
        filename = os.path.join(output_dir, f"{FACET_PLOT_COLUMN}{count}.{extension}")
        print(f"Saving image {filename}")
        fig.write_image(filename)

        count += 1
