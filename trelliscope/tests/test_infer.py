import pandas as pd
import pytest

from trelliscope import Trelliscope
from trelliscope.metas import (
    FactorMeta,
    HrefMeta,
    NumberMeta,
    PanelMeta,
    StringMeta,
)
from trelliscope.panel_source import FilePanelSource
from trelliscope.panels import ImagePanel, Panel

# ---------------------------------------------------------------------------
# Key-column inference
# ---------------------------------------------------------------------------


def test_infer_key_cols_single_string(iris_df_no_duplicates):
    """A column of unique strings should be inferred as the key column."""
    df = iris_df_no_duplicates.copy()
    df.insert(0, "id", [f"row_{i}" for i in range(len(df))])
    tr = Trelliscope(df, "test")
    assert "id" in tr.key_cols


def test_infer_key_cols_multiple_columns(iris_df):
    """When no single column is unique, multiple columns should be combined."""
    # iris_df has duplicates; Species + Sepal.Length combination may uniquely identify rows
    tr = Trelliscope(iris_df.drop_duplicates(), "test")
    # key_cols should be non-empty
    assert len(tr.key_cols) > 0


def test_infer_key_cols_raises_when_no_unique_combo(iris_df):
    """Should raise if no column combination uniquely identifies rows."""
    # Duplicate rows make key-col inference fail
    df = pd.DataFrame({"a": [1, 1], "b": [2, 2]})
    with pytest.raises(ValueError, match="Could not find columns"):
        Trelliscope(df, "test")


# ---------------------------------------------------------------------------
# Meta type inference
# ---------------------------------------------------------------------------


def test_infer_number_meta(iris_df_no_duplicates):
    tr = Trelliscope(iris_df_no_duplicates, "test")
    tr = tr.infer()
    assert "Sepal.Length" in tr.metas
    assert isinstance(tr.metas["Sepal.Length"], NumberMeta)


def test_infer_string_meta(iris_df_no_duplicates):
    tr = Trelliscope(iris_df_no_duplicates, "test")
    tr = tr.infer()
    # Species is a string (object dtype, first value is str)
    assert "Species" in tr.metas
    assert isinstance(tr.metas["Species"], StringMeta)


def test_infer_factor_meta(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["Species"] = pd.Categorical(df["Species"])
    tr = Trelliscope(df, "test")
    tr = tr.infer()
    assert "Species" in tr.metas
    assert isinstance(tr.metas["Species"], FactorMeta)


def test_infer_href_meta(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["url"] = [f"https://example.com/{i}" for i in range(len(df))]
    tr = Trelliscope(df, "test")
    tr = tr.infer()
    assert "url" in tr.metas
    assert isinstance(tr.metas["url"], HrefMeta)


def test_infer_skips_non_meta_columns(iris_df_no_duplicates):
    """Object columns that are not strings, figures, or callables should be ignored."""
    df = iris_df_no_duplicates.copy()
    df["mixed"] = [{"key": i} for i in range(len(df))]
    tr = Trelliscope(df, "test")
    tr = tr.infer()
    assert "mixed" not in tr.metas
    assert "mixed" in tr.columns_to_ignore


# ---------------------------------------------------------------------------
# Panel column exclusion from metas
# ---------------------------------------------------------------------------


def test_panel_column_becomes_panel_meta(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["img_panel"] = "test_image.png"
    pnl = ImagePanel(
        "img_panel", source=FilePanelSource(is_local=False), should_copy_to_output=False
    )
    tr = Trelliscope(df, "test").add_panel(pnl)
    tr = tr.infer()
    assert "img_panel" in tr.metas
    assert isinstance(tr.metas["img_panel"], PanelMeta)


def test_panel_column_not_inferred_as_string_meta(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["img_panel"] = "test_image.png"
    pnl = ImagePanel(
        "img_panel", source=FilePanelSource(is_local=False), should_copy_to_output=False
    )
    tr = Trelliscope(df, "test").add_panel(pnl)
    tr = tr.infer()
    assert isinstance(tr.metas["img_panel"], PanelMeta)
    assert not isinstance(tr.metas["img_panel"], StringMeta)


# ---------------------------------------------------------------------------
# Figure backup column exclusion from metas
# ---------------------------------------------------------------------------


def test_figure_backup_column_excluded_from_metas(iris_df_no_duplicates):
    """The __FIGURE backup column should never appear in metas."""
    df = iris_df_no_duplicates.copy()
    df["img_panel"] = "test_image.png"
    pnl = ImagePanel(
        "img_panel", source=FilePanelSource(is_local=False), should_copy_to_output=False
    )
    tr = Trelliscope(df, "test").add_panel(pnl)
    tr = tr.infer()
    backup_col = "img_panel" + Panel._FIGURE_SUFFIX
    assert backup_col not in tr.metas


# ---------------------------------------------------------------------------
# Panel inference from image columns
# ---------------------------------------------------------------------------


def test_infer_panels_from_image_column(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["img_panel"] = "test_image.png"
    pnl = ImagePanel(
        "img_panel", source=FilePanelSource(is_local=False), should_copy_to_output=False
    )
    tr = Trelliscope(df, "test").add_panel(pnl)
    tr = tr.infer_panels()
    assert "img_panel" in tr._get_panel_columns()
    assert isinstance(tr._get_panel("img_panel"), ImagePanel)


# ---------------------------------------------------------------------------
# LazyPanel inference from callable column
# ---------------------------------------------------------------------------


def test_infer_panels_detects_callable_column(iris_df_no_duplicates):
    """A column of callables should be auto-detected as a LazyPanel."""
    from trelliscope.panels import LazyPanel as LP

    df = iris_df_no_duplicates.copy()
    df["lazy"] = [lambda row: None for _ in range(len(df))]
    tr = Trelliscope(df, "test")
    tr = tr.infer_panels()
    assert "lazy" in tr._get_panel_columns()
    assert isinstance(tr._get_panel("lazy"), LP)


def test_lazy_panel_explicit_add(iris_df_no_duplicates):
    """LazyPanel added explicitly should appear in panel columns."""
    from trelliscope.panels import LazyPanel as LP

    df = iris_df_no_duplicates.copy()
    fn = lambda row: None  # noqa: E731
    lp = LP("lazy_panel", fn=fn)
    tr = Trelliscope(df, "test").add_panel(lp)
    assert "lazy_panel" in tr._get_panel_columns()


def test_lazy_panel_invalid_fn():
    from trelliscope.panels import LazyPanel as LP

    with pytest.raises(ValueError, match="callable"):
        LP("panel", fn="not_a_function")


# ---------------------------------------------------------------------------
# Label inference fallback
# ---------------------------------------------------------------------------


def test_infer_labels_fall_back_to_varname(iris_df_no_duplicates):
    """When no var_labels are set, the label should default to the varname."""
    tr = Trelliscope(iris_df_no_duplicates, "test")
    tr = tr.infer()
    assert tr.metas["Sepal.Length"].label == "Sepal.Length"


def test_infer_labels_uses_set_var_labels(iris_df_no_duplicates):
    """set_var_labels() should propagate to inferred metas."""
    tr = (
        Trelliscope(iris_df_no_duplicates, "test")
        .set_var_labels(**{"Sepal.Length": "Sepal Length (cm)"})
        .infer()
    )
    assert tr.metas["Sepal.Length"].label == "Sepal Length (cm)"


# ---------------------------------------------------------------------------
# Default state inference
# ---------------------------------------------------------------------------


def test_infer_default_layout_state(iris_df_no_duplicates):
    """When no layout is set, infer() should supply a default LayoutState."""
    df = iris_df_no_duplicates.copy()
    df["img_panel"] = "test_image.png"
    pnl = ImagePanel(
        "img_panel", source=FilePanelSource(is_local=False), should_copy_to_output=False
    )
    tr = Trelliscope(df, "test").add_panel(pnl)
    tr = tr.infer()
    assert tr.state.layout is not None
    assert tr.state.layout.ncol == 3


def test_infer_default_label_state(iris_df_no_duplicates):
    """When no labels are set, infer() should supply labels defaulting to key_cols."""
    df = iris_df_no_duplicates.copy()
    df["img_panel"] = "test_image.png"
    pnl = ImagePanel(
        "img_panel", source=FilePanelSource(is_local=False), should_copy_to_output=False
    )
    tr = Trelliscope(df, "test").add_panel(pnl)
    tr = tr.infer()
    assert tr.state.labels is not None
    for key in tr.key_cols:
        assert key in tr.state.labels.varnames
