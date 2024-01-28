import types

import pandas as pd


def facet_panels(
    df: pd.DataFrame,
    panel_column_name: str,
    facet_columns: list,
    plot_function: types.FunctionType,
    params: dict,
) -> pd.DataFrame:
    result_df = df.groupby(facet_columns).apply(
        lambda mini_df: plot_function(mini_df, **params)
    )
    result_df = result_df.to_frame(name=panel_column_name)
    return result_df
