import types
import os
import shutil
import pandas as pd

def facet_panels(df: pd.DataFrame, facet_columns:list, plot_function:types.FunctionType, params:dict) -> pd.Series:
    result = df.groupby(facet_columns).apply(lambda mini_df: plot_function(mini_df, **params))
    return result

def write_panels(panel_df: pd.Series, output_dir:str, extension:str = "png"):
    # Create the output directory if necessary
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    
    count = 0
    for fig in panel_df:
        filename = os.path.join(output_dir, f"plot{count}.{extension}")
        print(f"Saving image {filename}")
        fig.write_image(filename)
        
        count += 1
