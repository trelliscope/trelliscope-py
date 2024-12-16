"""Create dataframes with figure facets from dataframes containing input data.

Each facet is a figure belonging to a group of data.
"""

from typing import Any, Callable

import pandas as pd
import plotly.graph_objects as go


def facet_panels(
    df: pd.DataFrame,
    panel_column_name: str,
    facet_columns: list,
    plot_function: Callable[[pd.DataFrame, ...], go.Figure],
    params: dict[str, Any],
) -> pd.DataFrame:
    """Create figure facets from a dataframe by applying a plot function.

    Args:
        df: Dataframe input containing data for plotting and grouping.
        panel_column_name: The names of the output column containing the figure objects.
        facet_columns: Columns to group data by, creating a figure for each group.
        plot_function: Plotting function to apply to each group, taking a pd.DataFrame as the first argument.
        params: Additional keyword argument passed to the ``plot_function``.

    Returns:
        A dataframe with 1 column with the name of ``panel_column_name`` containing figure objects,
        The dataframe will have a multi-level index, with the level names given by ``facet_columns``.

    Examples:
        .. code-block:: python

            from trelliscope.facets import facet_panels

            import plotly.graph_objs as go
            import pandas as pd

            df = pd.DataFrame(
                [
                    ("Belgium","Europe",1977,9821800),
                    ("Belgium","Europe",1982,9856303),
                    ("Belgium","Europe",1987,9870200),
                    ("Belgium","Europe",1992,10045622),
                    ("Belgium","Europe",1997,10199787),
                    ("Belgium","Europe",2002,10311970),
                    ("Belgium","Europe",2007,10392226),
                    ("Singapore","Asia",1977,2325300),
                    ("Singapore","Asia",1982,2651869),
                    ("Singapore","Asia",1987,2794552),
                    ("Singapore","Asia",1992,3235865),
                    ("Singapore","Asia",1997,3802309),
                    ("Singapore","Asia",2002,4197776)
                ],
                columns=["Country", "Continent", "Year", "Population"]
            )

            def plot_population(df: pd.DataFrame, **kwargs) -> go.Figure:
                return go.Figure(go.Scatter(x=df["Year"], y=df["Population"]))

            df_facets = facet_panels(
                df=df,
                panel_column_name="panel",
                facet_columns=["Country", "Continent"],
                plot_function=plot_population,
                params={"layout": {"title": "Population over time"}}
            )
    """
    result_df = df.groupby(facet_columns).apply(
        lambda mini_df: plot_function(mini_df, **params)
    )
    result_df = result_df.to_frame(name=panel_column_name)
    return result_df
