"""
Compares the JSON this package writes with a display written by the R package,
the format the viewer was built around. The reference files are made by
external_data/r_reference/make_reference.R; this test writes the same display.
"""

import os

import pandas as pd
import pytest

from trelliscope import Trelliscope, utils
from trelliscope.input import NumberInput, RadioInput, TextInput
from trelliscope.panel_source import FilePanelSource
from trelliscope.panels import ImagePanel

REFERENCE_DIR = os.path.join(os.path.dirname(__file__), "external_data", "r_reference")

# Keys the R package writes that this package does not write yet. They are
# outside the input, info, theme and state formats this test covers.
NOT_YET_WRITTEN = {"order"}


def assert_matches_reference(reference, actual, path="displayInfo"):
    """Every key in the reference must be in actual with the same value."""
    if isinstance(reference, dict):
        assert isinstance(actual, dict), f"{path}: expected an object"
        for key, value in reference.items():
            assert key in actual, f"{path}.{key} is missing"
            assert_matches_reference(value, actual[key], f"{path}.{key}")
    elif isinstance(reference, list):
        assert isinstance(actual, list), f"{path}: expected a list"
        assert len(actual) == len(reference), f"{path}: length differs"
        for i, (ref_item, item) in enumerate(zip(reference, actual)):
            assert_matches_reference(ref_item, item, f"{path}[{i}]")
    else:
        assert actual == reference, f"{path}: {actual!r} != {reference!r}"


@pytest.fixture(scope="module")
def written(tmp_path_factory):
    out = tmp_path_factory.mktemp("display")
    info = out / "info.html"
    info.write_text("<h1>Reference info</h1>")

    df = pd.DataFrame(
        {
            "species": ["setosa", "versicolor", "virginica"],
            "n": [50, 50, 50],
            "panel": [f"https://example.com/{c}.png" for c in "abc"],
        }
    )
    tr = (
        Trelliscope(df, "ref", path=str(out), key_cols=["species"])
        .add_panel(
            ImagePanel("panel", FilePanelSource(False), should_copy_to_output=False)
        )
        .set_default_layout(ncol=2, sidebar=True, visible_filters=["species", "n"])
        .set_info_html(str(info))
        .set_theme(primary="#c80000")
        .add_inputs(
            [
                TextInput("notes", label="Notes"),
                RadioInput("flag", options=["yes", "no"]),
                NumberInput("score", min=0, max=10),
            ],
            email="someone@example.com",
            vars=["species"],
        )
        .write_display()
    )
    config = utils.read_jsonp(os.path.join(tr.get_output_path(), "config.jsonp"))
    display_info = utils.read_jsonp(
        os.path.join(tr.get_dataset_display_path(), "displayInfo.jsonp")
    )
    return config, display_info


def read_reference(name):
    return utils.read_jsonp(os.path.join(REFERENCE_DIR, name))


def test_app_config_theme_matches_r(written):
    config, _ = written
    assert config["theme"] == read_reference("config.jsonp")["theme"]


def test_display_info_matches_r(written):
    _, display_info = written
    reference = read_reference("displayInfo.jsonp")

    # Metas are compared by name and type only: each package fills in
    # different optional fields (maxnchar, digits) and orders them differently.
    reference_metas = {m["varname"]: m["type"] for m in reference.pop("metas")}
    metas = {m["varname"]: m["type"] for m in display_info["metas"]}
    assert metas == reference_metas

    for key in NOT_YET_WRITTEN:
        reference.pop(key)
    assert_matches_reference(reference, display_info)
