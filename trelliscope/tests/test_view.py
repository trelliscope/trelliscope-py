import json

from trelliscope import Trelliscope
from trelliscope.panel_source import FilePanelSource
from trelliscope.panels import ImagePanel
from trelliscope.state import CategoryFilterState, LabelState, LayoutState, SortState
from trelliscope.view import View

# Note, when using json results, we are converting the json to dictionaries
# and comparing those to ignore any differences in order or whitespace


def test_create_view_with_no_state():
    view = View("test view")

    # Look at just the state
    state = view.state
    actual_json = state.to_json()
    expected_json = '{"layout":null,"labels":null,"sort":[],"filter":[]}'
    assert json.loads(actual_json) == json.loads(expected_json)

    # look at the whole view
    actual_json = view.to_json(pretty=False)
    expected_json = '{"name":"test view","state":{"layout":null,"labels":null,"sort":[],"filter":[]}}'
    assert json.loads(actual_json) == json.loads(expected_json)


def test_create_view_with_state_parameters():
    view = View(
        "test view",
        label_state=LabelState(["manufacturer", "class"]),
        sort_state=SortState("manufacturer"),
    )

    actual_json = view.to_json(pretty=False)
    expected_json = '{"name":"test view","state":{"layout":null,"labels":{"varnames":["manufacturer","class"],"type":"labels"},"sort":[{"metatype":null,"dir":"asc","varname":"manufacturer","type":"sort"}],"filter":[]}}'
    assert json.loads(actual_json) == json.loads(expected_json)


def test_view_with_layout_state():
    v = View("v", layout_state=LayoutState(ncol=4))
    assert v.state.layout.ncol == 4


def test_view_with_filter_states_list():
    v = View(
        "v",
        filter_states=[
            CategoryFilterState("a", values=["x"]),
            CategoryFilterState("b", values=["y"]),
        ],
    )
    assert "a" in v.state.filter
    assert "b" in v.state.filter


def test_view_with_sort_states_list():
    v = View("v", sort_states=[SortState("a"), SortState("b")])
    assert "a" in v.state.sort
    assert "b" in v.state.sort


def test_view_to_json_pretty_vs_compact():
    v = View("v", layout_state=LayoutState(ncol=2))
    assert "\n" in v.to_json(pretty=True)
    assert "\n" not in v.to_json(pretty=False)


def test_view_copy_is_independent():
    v = View("original", layout_state=LayoutState(ncol=2))
    v2 = v._copy()
    v2.name = "copy"
    v2.state.layout.ncol = 99
    assert v.name == "original"
    assert v.state.layout.ncol == 2


def test_trelliscope_add_view(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["img"] = "test.png"
    pnl = ImagePanel("img", source=FilePanelSource(False), should_copy_to_output=False)
    tr = (
        Trelliscope(df, "test")
        .add_panel(pnl)
        .add_view(View("sorted_view", sort_state=SortState("Sepal.Length")))
    )
    assert "sorted_view" in tr.views


def test_trelliscope_add_view_replaces_existing(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["img"] = "test.png"
    pnl = ImagePanel("img", source=FilePanelSource(False), should_copy_to_output=False)
    tr = (
        Trelliscope(df, "test")
        .add_panel(pnl)
        .add_view(View("v", layout_state=LayoutState(ncol=1)))
        .add_view(View("v", layout_state=LayoutState(ncol=5)))
    )
    assert tr.views["v"].state.layout.ncol == 5


def test_trelliscope_add_view_immutable(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["img"] = "test.png"
    pnl = ImagePanel("img", source=FilePanelSource(False), should_copy_to_output=False)
    tr = Trelliscope(df, "test").add_panel(pnl)
    tr2 = tr.add_view(View("myview"))
    assert "myview" not in tr.views
    assert "myview" in tr2.views
