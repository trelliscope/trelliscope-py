# Trelliscope
This repository contains an experimental Python port of the trelliscope R package. It is currently under heavy development.

## Quick Start

Install from source (see [Getting Started for Development](development.md)), then try the minimal example below.

### Plotly figures

```python
import pandas as pd
import plotly.express as px
from trelliscope import Trelliscope

# One summary row per iris species, plus a per-species scatter plot
iris = px.data.iris()

rows = []
for species, group in iris.groupby("species"):
    fig = px.scatter(
        group, x="sepal_width", y="sepal_length",
        title=f"Species: {species}",
    )
    rows.append({
        "species": species,
        "n": len(group),
        "mean_sepal_length": group["sepal_length"].mean(),
        "panel": fig,
    })

df = pd.DataFrame(rows)

(
    Trelliscope(df, name="Iris Species", path="./iris_display")
    .set_var_labels(
        species="Species",
        n="Count",
        mean_sepal_length="Mean Sepal Length (cm)",
    )
    .set_default_layout(ncol=3)
    .write_display()
    .view_trelliscope()
)
```

### Lazy panels (generate figures at write time)

Use `LazyPanel` when you want to generate each figure from a row of the summary
data frame rather than pre-computing all figures up front.  The function
receives a `pd.Series` (one row) and must return a Plotly or matplotlib figure.

```python
import pandas as pd
import plotly.express as px
from trelliscope import LazyPanel, Trelliscope

iris = px.data.iris()
summary = (
    iris.groupby("species")
    .agg(n=("sepal_length", "count"), mean_sl=("sepal_length", "mean"))
    .reset_index()
)

# Keep the raw data accessible in the closure
def make_panel(row):
    species_data = iris[iris["species"] == row["species"]]
    return px.scatter(species_data, x="sepal_width", y="sepal_length",
                      title=row["species"])

(
    Trelliscope(summary, name="Iris Lazy", path="./iris_lazy")
    .add_panel(LazyPanel("panel", fn=make_panel))
    .write_display()
)
```

### matplotlib figures

`Trelliscope` also accepts `matplotlib.figure.Figure` objects in panel columns
(or returned from a `LazyPanel` function).

```python
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px  # for the iris dataset only
from trelliscope import Trelliscope

iris = px.data.iris()

rows = []
for species, group in iris.groupby("species"):
    fig, ax = plt.subplots()
    ax.scatter(group["sepal_width"], group["sepal_length"])
    ax.set_title(species)
    rows.append({"species": species, "panel": fig})
    plt.close(fig)

df = pd.DataFrame(rows)
Trelliscope(df, name="Iris matplotlib", path="./iris_mpl").write_display()
```

## More Examples

For a fuller walkthrough see the
[Python Trelliscope Introduction](trelliscope/examples/introduction.ipynb)
Jupyter notebook.

## Getting Started For Development
If you are interested in working on development of the Trelliscope library itself, see: [Getting Started for Development](development.md)
