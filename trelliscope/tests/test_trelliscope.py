import json
import os
import tempfile
import urllib.request

import pandas as pd
import pytest

from trelliscope import Trelliscope
from trelliscope.metas import NumberMeta
from trelliscope.panel_source import FilePanelSource
from trelliscope.panels import ImagePanel, Panel
from trelliscope.state import SortState


def test_mars_df(mars_df: pd.DataFrame):
    assert len(mars_df) > 0
    assert len(mars_df.columns) > 0


def test_init(iris_tr: Trelliscope):
    assert iris_tr.name == "iris"


def test_to_dict(iris_tr: Trelliscope):
    dict = iris_tr.to_dict()

    assert "name" in dict
    assert "description" in dict
    assert "tags" in dict
    assert "key_cols" in dict
    assert "metas" in dict
    assert "state" in dict
    assert "views" in dict
    assert "inputs" in dict
    assert "thumbnailurl" in dict

    assert dict["name"] == "iris"


def test_no_name(iris_df_no_duplicates: pd.DataFrame):
    iris_df = iris_df_no_duplicates
    Trelliscope(iris_df, "iris")

    # Trelliscopes need a name param
    with pytest.raises(TypeError, match=r"missing .* required .* argument"):
        Trelliscope(iris_df)


# def test_no_img_panel(iris_df: pd.DataFrame):
#     # Trelliscopes need an image panel
#     with pytest.raises(ValueError, match=r"that references a plot or image"):
#         tr = Trelliscope(iris_df, "Iris")

#     # TODO: SB: In the new approach, I think this could be inferred later
#     # during the write process or something, so I think this should not raise
#     # an error at this point.


def test_standard_setup(iris_df_no_duplicates: pd.DataFrame):
    iris_df = iris_df_no_duplicates

    with tempfile.TemporaryDirectory() as output_dir:
        # this is test code that just sets all images to this test_image.png string
        # it is not a proper use of the images, but gives us something to use in testing.
        iris_df["img_panel"] = "test_image.png"

        tr = Trelliscope(iris_df, "Iris", path=output_dir)
        tr = tr.add_panel(
            ImagePanel(
                "img_panel", source=FilePanelSource(True), should_copy_to_output=False
            )
        )
        tr.write_display()

        id_file = os.path.join(tr.get_output_path(), "id")

        with open(id_file) as input_file:
            id_from_file = input_file.read()

            assert id_from_file.strip() == tr.id


def test_standard_setup_explicit_javascript_version(
    iris_df_no_duplicates: pd.DataFrame,
):
    version = "1.2.3.4"

    iris_df = iris_df_no_duplicates

    with tempfile.TemporaryDirectory() as output_dir:
        # this is test code that just sets all images to this test_image.png string
        # it is not a proper use of the images, but gives us something to use in testing.
        iris_df["img_panel"] = "test_image.png"

        tr = Trelliscope(iris_df, "Iris", path=output_dir, javascript_version=version)
        tr = tr.add_panel(
            ImagePanel(
                "img_panel", source=FilePanelSource(True), should_copy_to_output=False
            )
        )
        tr.write_display()

        # verify that the index.html file has the correct JavaScript version in it
        index_html_file = os.path.join(tr.get_output_path(), "index.html")

        with open(index_html_file) as input_file:
            html = input_file.read()

            assert (
                f'<script src="https://unpkg.com/trelliscopejs-lib@{version}/dist/assets/index.js"></script>'
                in html
            )
            assert (
                f'<link href="https://unpkg.com/trelliscopejs-lib@{version}/dist/assets/index.css" rel="stylesheet" />'
                in html
            )

            assert (
                f"<body onload=\"trelliscopeApp('{tr.id}', 'config.jsonp')\">" in html
            )
            assert f'<div id="{tr.id}" class="trelliscope-spa">' in html


def test_standard_setup_default_javascript_version(iris_df_no_duplicates: pd.DataFrame):
    iris_df = iris_df_no_duplicates

    with tempfile.TemporaryDirectory() as output_dir:
        # this is test code that just sets all images to this test_image.png string
        # it is not a proper use of the images, but gives us something to use in testing.
        iris_df["img_panel"] = "test_image.png"

        tr = Trelliscope(iris_df, "Iris", path=output_dir)
        tr = tr.add_panel(
            ImagePanel(
                "img_panel", source=FilePanelSource(True), should_copy_to_output=False
            )
        )
        tr.write_display()

        # verify that the index.html file has the correct JavaScript version in it
        expected_version = "0.7.5"
        index_html_file = os.path.join(tr.get_output_path(), "index.html")

        with open(index_html_file) as input_file:
            html = input_file.read()

            assert (
                f'<script src="https://unpkg.com/trelliscopejs-lib@{expected_version}/dist/assets/index.js"></script>'
                in html
            )
            assert (
                f'<link href="https://unpkg.com/trelliscopejs-lib@{expected_version}/dist/assets/index.css" rel="stylesheet" />'
                in html
            )

            assert (
                f"<body onload=\"trelliscopeApp('{tr.id}', 'config.jsonp')\">" in html
            )
            assert f'<div id="{tr.id}" class="trelliscope-spa">' in html


def test_get_thumbnail_url(mars_df: pd.DataFrame):
    """
    Tests the case where the thumbnail url is simply the first row
    of the panel column.
    """
    tr = Trelliscope(mars_df, "mars_rover")
    tr = tr.add_panel(
        ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False)
    )

    tr2 = tr._infer_thumbnail_url()
    first_value = mars_df["img_src"][0]

    assert tr2.thumbnail_url == first_value


def test_get_panel_columns(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    tr = Trelliscope(mars_df, "mars_rover")
    tr = tr.add_panel(
        ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False)
    )
    tr = tr.add_panel(
        ImagePanel("img2", source=FilePanelSource(False), should_copy_to_output=False)
    )

    panels = tr._get_panel_columns()

    assert set(panels) == {"img_src", "img2"}


def test_get_panel_output_path(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    with tempfile.TemporaryDirectory() as output_dir:
        tr = Trelliscope(mars_df, "mars_rover", path=output_dir)
        tr = tr.add_panel(
            ImagePanel(
                "img_src", source=FilePanelSource(True), should_copy_to_output=False
            )
        )
        tr = tr.add_panel(
            ImagePanel(
                "img2", source=FilePanelSource(False), should_copy_to_output=False
            )
        )

        expected_abs_path = os.path.join(
            output_dir, "mars_rover", "displays", "mars_rover", "panels", "img_src"
        )
        actual_abs_path = tr._get_panel_output_path("img_src", True)
        assert os.path.normpath(expected_abs_path) == os.path.normpath(actual_abs_path)

        expected_rel_path = os.path.join("panels", "img_src")
        actual_rel_path = tr._get_panel_output_path("img_src", False)
        assert os.path.normpath(expected_rel_path) == os.path.normpath(actual_rel_path)


def test_add_panel(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    tr = Trelliscope(mars_df, "mars_rover")

    panel1 = ImagePanel(
        "img_src", source=FilePanelSource(True), should_copy_to_output=False
    )
    tr2 = tr.add_panel(panel1)
    panel2 = ImagePanel(
        "img2", source=FilePanelSource(False), should_copy_to_output=False
    )
    tr3 = tr2.add_panel(panel2)

    assert not tr._has_panel("img_src")
    assert not tr._has_panel("img2")

    assert tr2._has_panel("img_src")
    assert not tr2._has_panel("img2")

    assert tr3._has_panel("img_src")
    assert tr3._has_panel("img2")


def test_get_panel_from_col_name(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    tr = Trelliscope(mars_df, "mars_rover")

    panel1 = ImagePanel(
        "img_src", source=FilePanelSource(True), should_copy_to_output=False
    )
    tr = tr.add_panel(panel1)
    panel2 = ImagePanel(
        "img2", source=FilePanelSource(False), should_copy_to_output=False
    )
    tr = tr.add_panel(panel2)

    assert tr._has_panel("img_src")
    assert tr._has_panel("img2")
    assert not tr._has_panel("camera")

    # Note: We cannot check that the instances are the same, because the copy results
    # in different objects
    # assert panel1 == tr._get_panel("img_src")
    assert panel1.varname == tr._get_panel("img_src").varname
    assert panel2.varname == tr._get_panel("img2").varname

    with pytest.raises(ValueError, match="There is no panel"):
        tr._get_panel("camera")


def test_infer_primary_panel(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    tr = Trelliscope(mars_df, "mars_rover")
    tr = tr.add_panel(
        ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False)
    )
    tr = tr.add_panel(
        ImagePanel("img2", source=FilePanelSource(False), should_copy_to_output=False)
    )

    assert tr.primary_panel is None

    tr._infer_primary_panel()

    # It would be nice to know that infer will get the "first" one,
    # but because they are stored in a dictionary, order is not
    # guaranteed. All we know is that it will be one of them.
    assert tr.primary_panel in ("img_src", "img2")


def test_copy_images_to_build_directory():
    """Local image files should be copied into the output directory on write_display()."""
    import base64

    # Minimal valid 1×1 white PNG — no external download needed
    TINY_PNG = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
        b"+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )

    with tempfile.TemporaryDirectory() as output_dir:
        with tempfile.TemporaryDirectory() as img_dir:
            rows = []
            for i in range(3):
                img_path = os.path.join(img_dir, f"row_{i}.png")
                with open(img_path, "wb") as f:
                    f.write(TINY_PNG)
                rows.append({"id": str(i), "value": float(i), "img_panel": img_path})
            df = pd.DataFrame(rows)

            tr = Trelliscope(df, "test", path=output_dir)
            tr = tr.add_panel(
                ImagePanel(
                    "img_panel", FilePanelSource(True), should_copy_to_output=True
                )
            )

            # Before write: paths point into img_dir
            assert img_dir in tr.data_frame["img_panel"].iloc[0]

            tr = tr.write_display()

            # After write: paths must no longer point into the original img_dir
            new_img = tr.data_frame["img_panel"].iloc[0]
            full_path = os.path.join(tr.get_dataset_display_path(), new_img)
            assert img_dir not in full_path

            # And the copied file must actually exist in the output directory
            assert os.path.exists(full_path)


def test_set_default_sort(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    tr = Trelliscope(mars_df, "mars_rover")
    tr = tr.add_panel(
        ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False)
    )
    tr = tr.add_panel(
        ImagePanel("img2", source=FilePanelSource(False), should_copy_to_output=False)
    )

    tr = tr.set_default_sort(["img2", "img3"])
    expected_n_sort = 2
    assert len(tr.state.sort) == expected_n_sort

    sort_keys = list(tr.state.sort.keys())

    ss1: SortState = tr.state.sort[sort_keys[0]]
    ss2: SortState = tr.state.sort[sort_keys[1]]

    assert ss1.varname == "img2"
    assert ss2.varname == "img3"

    assert ss1.dir == SortState.DIR_ASCENDING
    assert ss2.dir == SortState.DIR_ASCENDING

    assert ss1.metatype is None

    # Overwrite
    tr = tr.set_default_sort(["img_src", "img2"], ["asc", "desc"])

    expected_n_sort = 2
    assert len(tr.state.sort) == expected_n_sort

    sort_keys = list(tr.state.sort.keys())

    ss1: SortState = tr.state.sort[sort_keys[0]]
    ss2: SortState = tr.state.sort[sort_keys[1]]

    assert ss1.varname == "img_src"
    assert ss2.varname == "img2"

    assert ss1.dir == SortState.DIR_ASCENDING
    assert ss2.dir == SortState.DIR_DESCENDING

    # Append
    tr = tr.set_default_sort(["img3"], add=True)
    expected_n_sort = 3
    assert len(tr.state.sort) == expected_n_sort

    sort_keys = list(tr.state.sort.keys())

    ss1: SortState = tr.state.sort[sort_keys[0]]
    ss2: SortState = tr.state.sort[sort_keys[1]]
    ss3: SortState = tr.state.sort[sort_keys[2]]

    assert ss1.varname == "img_src"
    assert ss2.varname == "img2"
    assert ss3.varname == "img3"

    assert ss1.dir == SortState.DIR_ASCENDING
    assert ss2.dir == SortState.DIR_DESCENDING
    assert ss3.dir == SortState.DIR_ASCENDING

    # Try wrong number of directions
    with pytest.raises(ValueError, match=r"'varnames' must have same length as 'dirs'"):
        tr.set_default_sort(["a", "b", "c"], ["asc", "desc"])


def test_infer_state(iris_df_no_duplicates):
    import pandas as pd

    from trelliscope.state import CategoryFilterState, DisplayState, LayoutState

    df = iris_df_no_duplicates.copy()
    df["Species"] = pd.Categorical(df["Species"])
    df["img"] = "test.png"
    pnl = ImagePanel("img", source=FilePanelSource(False), should_copy_to_output=False)
    tr = Trelliscope(df, "test").add_panel(pnl).infer()

    # Empty state → default LayoutState(ncol=3) and LabelState(key_cols)
    inferred = tr._infer_state(DisplayState())
    assert inferred.layout is not None
    assert inferred.layout.ncol == 3
    assert inferred.labels is not None
    for key in tr.key_cols:
        assert key in inferred.labels.varnames

    # Existing layout is preserved, not overwritten
    state_with_layout = DisplayState()
    state_with_layout.set(LayoutState(ncol=5))
    inferred2 = tr._infer_state(state_with_layout)
    assert inferred2.layout.ncol == 5

    # CategoryFilterState values are intersected with FactorMeta levels
    state_with_filter = DisplayState()
    cf = CategoryFilterState("Species", values=["setosa", "no_such_species"])
    state_with_filter.set(cf)
    inferred3 = tr._infer_state(state_with_filter)
    assert "setosa" in inferred3.filter["Species"].values
    assert "no_such_species" not in inferred3.filter["Species"].values


def test_set_primary_panel(mars_df: pd.DataFrame):
    with tempfile.TemporaryDirectory() as output_dir:
        tr = Trelliscope(mars_df, "mars_rover", path=output_dir)
        tr = tr.add_panel(ImagePanel("img_src", FilePanelSource(False)))

        with pytest.raises(ValueError, match="Error: Primary panel should be a panel."):
            tr = tr.set_primary_panel("camera")

        tr = tr.set_primary_panel("img_src")
        assert tr.primary_panel == "img_src"


def test_infer_panels(mars_df: pd.DataFrame):
    with tempfile.TemporaryDirectory() as output_dir:
        tr = Trelliscope(mars_df, "mars_rover", path=output_dir)
        tr = tr.infer_panels()

        assert len(tr.panels) == 1

        panel: Panel = tr.panels["img_src"]
        assert panel.varname == "img_src"

        assert tr.primary_panel == "img_src"


def test_add_input(iris_tr):
    from trelliscope.input import TextInput

    inp = TextInput("notes", label="Notes", width=60, height=4)
    tr = iris_tr.add_input(inp)

    assert "notes" in tr.inputs
    assert tr.inputs["notes"].label == "Notes"


def test_add_inputs(iris_tr):
    from trelliscope.input import NumberInput, RadioInput, TextInput

    inputs = [
        TextInput("comments", label="Comments"),
        RadioInput("quality", label="Quality", options=["good", "bad"]),
        NumberInput("score", label="Score", min=0, max=10),
    ]
    tr = iris_tr.add_inputs(inputs, email="test@example.com", vars=["Species"])

    assert len(tr.inputs) == 3
    assert tr.input_email == "test@example.com"
    assert tr.input_vars == ["Species"]


def test_add_inputs_serialized(iris_tr):
    from trelliscope.input import RadioInput, TextInput

    inputs = [
        TextInput("notes"),
        RadioInput("flag", options=["yes", "no"]),
    ]
    tr = iris_tr.add_inputs(inputs, email="user@test.com", vars=["Species"])
    d = tr.to_dict()

    # The shape the viewer reads, matching the R package's Inputs class.
    assert set(d["inputs"]) == {"inputs", "storageInterface", "feedbackInterface"}
    assert {i["type"] for i in d["inputs"]["inputs"]} == {"text", "radio"}
    assert d["inputs"]["storageInterface"] == {"type": "localStorage"}
    assert d["inputs"]["feedbackInterface"] == {
        "feedbackEmail": "user@test.com",
        "includeMetaVars": ["Species"],
    }


def test_no_inputs_serialized_as_null(iris_tr):
    assert iris_tr.to_dict()["inputs"] is None


def test_set_var_labels(iris_tr):
    tr = iris_tr.set_var_labels(
        Species="Species Name", **{"Sepal.Length": "Sepal Length (cm)"}
    )

    assert tr.var_labels["Species"] == "Species Name"
    assert tr.var_labels["Sepal.Length"] == "Sepal Length (cm)"


def test_set_var_labels_applied_to_existing_meta(iris_df_no_duplicates):
    from trelliscope.metas import StringMeta

    tr = Trelliscope(iris_df_no_duplicates, name="iris")
    tr = tr.set_meta(StringMeta("Species"))
    tr = tr.set_var_labels(Species="Species Name")

    assert tr.metas["Species"].label == "Species Name"


def test_set_var_labels_applied_during_infer(iris_df_no_duplicates):
    tr = Trelliscope(iris_df_no_duplicates, name="iris")
    tr = tr.set_var_labels(**{"Sepal.Length": "Sepal Length (cm)"})
    tr = tr._infer_metas()

    assert tr.metas["Sepal.Length"].label == "Sepal Length (cm)"


def test_set_var_labels_invalid_type(iris_tr):
    with pytest.raises(ValueError, match="string"):
        iris_tr.set_var_labels(Species=123)


# ---------------------------------------------------------------------------
# Phase 2: set_default_layout (sidebar + visible_filters)
# ---------------------------------------------------------------------------


def test_set_default_layout_sidebar(iris_df_no_duplicates):
    tr = Trelliscope(iris_df_no_duplicates, name="iris")
    tr = tr.set_default_layout(ncol=2, sidebar=False)
    assert tr.state.layout.sidebar is False
    assert tr.state.layout.ncol == 2


def test_set_default_layout_visible_filters(iris_df_no_duplicates):
    tr = Trelliscope(iris_df_no_duplicates, name="iris")
    tr = tr.set_default_layout(ncol=3, visible_filters=["Species", "Sepal.Length"])
    assert tr.state.layout.visible_filters == ["Species", "Sepal.Length"]


def test_set_default_layout_visible_filters_unknown_col(iris_df_no_duplicates):
    tr = Trelliscope(iris_df_no_duplicates, name="iris")
    with pytest.raises(ValueError, match="references columns not in the data"):
        tr.set_default_layout(visible_filters=["no_such_col"])


def test_set_default_layout_serialized(iris_df_no_duplicates):
    tr = Trelliscope(iris_df_no_duplicates, name="iris")
    tr = tr.set_default_layout(ncol=4, sidebar=False, visible_filters=["Species"])
    d = tr.state.layout.to_dict()
    assert d["sidebar"] is False
    assert d["visible_filters"] == ["Species"]
    assert d["ncol"] == 4


# ---------------------------------------------------------------------------
# Phase 2: set_info_html and set_show_info_on_load
# ---------------------------------------------------------------------------


def test_set_info_html(iris_tr):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write("<h1>Hello Trelliscope</h1>")
        html_path = f.name

    try:
        tr = iris_tr.set_info_html(html_path)
        assert tr.info_html == "<h1>Hello Trelliscope</h1>"
        assert tr.to_dict()["hasInfo"] is True
    finally:
        os.unlink(html_path)


def test_set_info_html_missing_file(iris_tr):
    with pytest.raises(ValueError, match="not found"):
        iris_tr.set_info_html("/nonexistent/path/info.html")


def test_set_info_html_does_not_mutate_original(iris_tr):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write("<p>test</p>")
        html_path = f.name

    try:
        tr2 = iris_tr.set_info_html(html_path)
        assert iris_tr.info_html is None
        assert tr2.info_html is not None
    finally:
        os.unlink(html_path)


def test_set_show_info_on_load(iris_tr):
    tr = iris_tr.set_show_info_on_load(True)
    assert tr.show_info_on_load is True
    assert tr.to_dict()["infoOnLoad"] is True


def test_set_show_info_on_load_default_false(iris_tr):
    assert iris_tr.show_info_on_load is False
    assert iris_tr.to_dict()["infoOnLoad"] is False


def test_set_show_info_on_load_invalid_type(iris_tr):
    with pytest.raises(TypeError, match="must be a boolean"):
        iris_tr.set_show_info_on_load("yes")


def test_has_info_false_by_default(iris_tr):
    assert iris_tr.to_dict()["hasInfo"] is False


# ---------------------------------------------------------------------------
# serve()
# ---------------------------------------------------------------------------


def test_serve_raises_before_write(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["img"] = "test.png"
    pnl = ImagePanel("img", source=FilePanelSource(False), should_copy_to_output=False)
    tr = Trelliscope(df, "test").add_panel(pnl)
    with pytest.raises(ValueError, match="write_display"):
        tr.serve(port=19876)


def test_serve_returns_self(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["img"] = "test.png"
    pnl = ImagePanel("img", source=FilePanelSource(False), should_copy_to_output=False)
    with tempfile.TemporaryDirectory() as output_dir:
        tr = Trelliscope(df, "test", path=output_dir).add_panel(pnl).write_display()
        result = tr.serve(port=19877)
        assert result is tr


def test_serve_responds_to_http(iris_df_no_duplicates):
    """The background server should return HTTP 200 for index.html."""
    import time

    df = iris_df_no_duplicates.copy()
    df["img"] = "test.png"
    pnl = ImagePanel("img", source=FilePanelSource(False), should_copy_to_output=False)
    with tempfile.TemporaryDirectory() as output_dir:
        tr = Trelliscope(df, "test", path=output_dir).add_panel(pnl).write_display()
        tr.serve(port=19878)
        time.sleep(0.3)  # let the daemon thread bind its socket
        response = urllib.request.urlopen(
            "http://localhost:19878/index.html", timeout=3
        )
        assert response.getcode() == 200


def test_save_figure_calls_write_image(tmp_path):
    """_save_figure delegates to fig.write_image for Plotly figures."""
    from unittest.mock import MagicMock

    captured = {}

    def fake_write_image(path):
        captured["path"] = path
        open(path, "wb").close()

    mock_fig = MagicMock()
    mock_fig.write_image.side_effect = fake_write_image

    out = tmp_path / "out.png"
    Trelliscope._save_figure(mock_fig, str(out))

    assert captured["path"] == str(out)
    assert mock_fig.write_image.call_count == 1


def test_write_display_in_jupyter_event_loop(iris_df_no_duplicates, tmp_path):
    """write_display() works when called from inside a running event loop (Jupyter)."""
    import asyncio
    from unittest.mock import MagicMock

    df = iris_df_no_duplicates.copy()

    def make_mock_fig():
        fig = MagicMock()
        fig.write_image.side_effect = lambda path: open(path, "wb").close()
        return fig

    df["panel"] = [make_mock_fig() for _ in range(len(df))]

    async def run():
        from trelliscope.panel_source import FilePanelSource
        from trelliscope.panels import FigurePanel

        pnl = FigurePanel("panel", source=FilePanelSource(False))
        tr = Trelliscope(df, "test", path=str(tmp_path)).add_panel(pnl).write_display()
        return tr

    tr = asyncio.run(run())
    assert tr is not None


def test_write_display_with_missing_category_value(iris_df_no_duplicates: pd.DataFrame):
    df = iris_df_no_duplicates.copy()
    df["img_panel"] = "test_image.png"
    df["size"] = pd.Categorical(
        ["small", None] * (len(df) // 2) + ["small"] * (len(df) % 2)
    )

    with tempfile.TemporaryDirectory() as output_dir:
        tr = (
            Trelliscope(df, "Iris", path=output_dir)
            .add_panel(
                ImagePanel(
                    "img_panel",
                    source=FilePanelSource(True),
                    should_copy_to_output=False,
                )
            )
            .write_display()
        )

        meta_data_file = os.path.join(tr.get_dataset_display_path(), "metaData.js")
        with open(meta_data_file) as f:
            text = f.read()
        rows = json.loads(text[text.index("=") + 1 :])

        # Level codes start at 1; the viewer reads 0 as a missing value.
        assert {row["size"] for row in rows} == {0, 1}


def test_set_metas(iris_df_no_duplicates: pd.DataFrame):
    tr = Trelliscope(iris_df_no_duplicates, "iris")
    metas = [NumberMeta("Sepal.Length", digits=1), NumberMeta("Sepal.Width", digits=2)]

    tr2 = tr.set_metas(metas)

    # set_meta deep-copies the display, so compare values, not identities.
    assert {k: m.digits for k, m in tr2.metas.items()} == {
        m.varname: m.digits for m in metas
    }
    assert tr.metas == {}
