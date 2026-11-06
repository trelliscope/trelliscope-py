import tempfile

import pandas as pd
import pytest

from trelliscope import Trelliscope
from trelliscope.panel_source import FilePanelSource
from trelliscope.panels import ImagePanel, Panel, PanelOptions


def test_panels_setup_no_uniquely_identifying_columns(iris_df: pd.DataFrame):
    with tempfile.TemporaryDirectory() as temp_dir_name:
        # this is test code that just sets all images to this test_image.png string
        # it is not a proper use of the images, but gives us something to use in testing.
        iris_df["img_panel"] = "test_image.png"

        # SB: We previously passed a panel here, because it used to be required
        # to instantiate the object, but now it is not really needed any longer to
        # produce the error.
        # pnl = ImagePanel("img_panel", source=FilePanelSource(True), aspect_ratio=1.5)

        with pytest.raises(ValueError, match="Could not find columns"):
            (Trelliscope(iris_df, "Iris", path=temp_dir_name))


def test_panels_setup(iris_df_no_duplicates: pd.DataFrame):
    iris_df = iris_df_no_duplicates

    with tempfile.TemporaryDirectory() as temp_dir_name:
        # this is test code that just sets all images to this test_image.png string
        # it is not a proper use of the images, but gives us something to use in testing.
        iris_df["img_panel"] = "test_image.png"

        pnl = ImagePanel(
            "img_panel",
            source=FilePanelSource(is_local=False),
            aspect_ratio=1.5,
            should_copy_to_output=False,
        )

        (
            Trelliscope(iris_df, "Iris", path=temp_dir_name)
            .add_panel(pnl)
            .write_display()
        )


def test_panels_setup_options(iris_df_no_duplicates: pd.DataFrame):
    df = iris_df_no_duplicates.copy()
    df["img_panel"] = "test_image.png"
    pnl = ImagePanel(
        "img_panel",
        source=FilePanelSource(is_local=False),
        should_copy_to_output=False,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        # add_panel then write_display (basic chain)
        tr = Trelliscope(df, "Iris", path=temp_dir).add_panel(pnl).write_display()
        assert "img_panel" in tr._get_panel_columns()

        # add_panel with a fresh Trelliscope (non-chained)
        tr2 = Trelliscope(df, "Iris", path=temp_dir)
        tr2 = tr2.add_panel(pnl)
        tr2 = tr2.write_display()
        assert "img_panel" in tr2._get_panel_columns()

        # infer_panels finds the already-added panel (no duplication)
        tr3 = Trelliscope(df, "Iris", path=temp_dir).add_panel(pnl).infer_panels()
        assert tr3._get_panel_columns().count("img_panel") == 1

        # PanelOptions are stored and retrievable
        width = 800
        opts = PanelOptions(width=width, height=600)
        tr4 = (
            Trelliscope(df, "Iris", path=temp_dir)
            .set_panel_options({"img_panel": opts})
            .add_panel(pnl)
        )
        assert tr4._get_panel_options("img_panel").width == width
        assert tr4._get_panel_options("unknown") is None


def test_panel_options_init_default():
    # default params
    expected_width = 600
    expected_height = 400

    panel_options = PanelOptions()
    assert panel_options.width == expected_width
    assert panel_options.height == expected_height
    assert panel_options.aspect == pytest.approx(1.5, 0.01)
    assert panel_options.format is None
    assert panel_options.force is False
    assert panel_options.prerender is True
    assert panel_options.type is None


def test_panel_options_init_no_aspect_ratio():
    # specified params (except aspect ratio)
    expected_width = 500
    expected_height = 500
    expected_format = "png"
    expected_force = True
    expected_prerender = False
    expected_type = Panel._PANEL_TYPE_IMAGE

    panel_options = PanelOptions(
        width=expected_width,
        height=expected_height,
        format=expected_format,
        force=expected_force,
        prerender=expected_prerender,
        type=expected_type,
    )
    assert panel_options.width == expected_width
    assert panel_options.height == expected_height
    assert panel_options.aspect == pytest.approx(1.0, 0.01)
    assert panel_options.format == expected_format
    assert panel_options.force is expected_force
    assert panel_options.prerender is expected_prerender
    assert panel_options.type == expected_type


def test_panel_options_init_with_aspect_ratio():
    expected_width = 500
    expected_height = 500
    expected_format = "png"
    expected_force = True
    expected_prerender = False
    expected_type = Panel._PANEL_TYPE_IMAGE
    aspect_ratio = 2.0

    panel_options = PanelOptions(
        width=expected_width,
        height=expected_height,
        format=expected_format,
        force=expected_force,
        prerender=expected_prerender,
        type=expected_type,
        aspect=aspect_ratio,
    )
    assert panel_options.width == expected_width
    assert panel_options.height == expected_height
    assert panel_options.aspect == pytest.approx(2.0, 0.01)
    assert panel_options.format == expected_format
    assert panel_options.force is expected_force
    assert panel_options.prerender is expected_prerender
    assert panel_options.type == expected_type


def test_panel_options_init_invalid_format():
    with pytest.raises(ValueError):
        PanelOptions(format="doc")


def test_set_panel_options_dict(iris_df_no_duplicates: pd.DataFrame):
    """
    Just ensure that the dictionary is set at this point.
    """
    panel_options1 = PanelOptions()
    panel_options2 = PanelOptions(
        width=500,
        height=500,
        format="png",
        force=True,
        prerender=False,
        type=Panel._PANEL_TYPE_IMAGE,
    )

    options_dict = {"Sepal.Length": panel_options1, "Sepal.Width": panel_options2}

    tr = Trelliscope(iris_df_no_duplicates, "Iris")
    tr = tr.set_panel_options(options_dict)

    po1 = tr._get_panel_options("Sepal.Length")
    po2 = tr._get_panel_options("Sepal.Width")
    po3 = tr._get_panel_options("Unknown panel")

    assert po3 is None
    assert po1 is panel_options1
    assert po2 is panel_options2


def test_set_panel_options(mars_df: pd.DataFrame):
    with tempfile.TemporaryDirectory() as output_dir:
        panel_options = PanelOptions(
            width=500,
            height=500,
            format="png",
            force=True,
            prerender=True,
            type=Panel._PANEL_TYPE_IMAGE,
        )
        options_dict = {"img_src": panel_options}

        tr = Trelliscope(mars_df, "mars_rover", path=output_dir)
        tr = tr.set_panel_options(options_dict)
        tr = tr.infer_panels()

        panel = tr._get_panel("img_src")
        assert panel.aspect_ratio == pytest.approx(1.0, 0.01)
