import tempfile

import pandas as pd
import pytest

from trelliscope import Trelliscope
from trelliscope.panel_source import FilePanelSource
from trelliscope.panels import IFramePanel, ImagePanel, Panel, PanelOptions


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
            tr = (
                Trelliscope(iris_df, "Iris", path=temp_dir_name)
                #   .add_panel(pnl)
            )

            # tr.write_display()


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

        tr = Trelliscope(iris_df, "Iris", path=temp_dir_name).add_panel(pnl)

        tr.write_display()


@pytest.mark.skip("Still considering various options for this")
def test_panels_setup_options(iris_df: pd.DataFrame):
    with tempfile.TemporaryDirectory() as temp_dir_name:
        tr = Trelliscope(iris_df, "Iris", path=temp_dir_name)

        # This will infer the panels if they have not been set
        tr.write_display()

        # this is test code that just sets all images to this test_image.png string
        # it is not a proper use of the images, but gives us something to use in testing.
        iris_df["img_panel"] = "test_image.png"

        # use panel in init
        pnl = Panel("img_panel", aspect_ratio=1.5)
        tr = Trelliscope(iris_df, "Iris", panel=pnl, path=temp_dir_name)
        tr.write_display()

        # set panel after init
        tr = Trelliscope(iris_df, "Iris", path=temp_dir_name)
        tr.set_panel(Panel("img_panel", aspect_ratio=1.5))

        tr.write_display()

        # set derived class panel
        tr = Trelliscope(iris_df, "Iris", path=temp_dir_name)
        tr.set_panel(ImagePanel("img_panel", aspect_ratio=1.5))
        tr.write_display()

        # set derived class panel
        tr = Trelliscope(iris_df, "Iris", path=temp_dir_name)
        tr.set_panel(IFramePanel("img_panel", aspect_ratio=1.5, is_local=True))
        tr.write_display()

        # chain panel methods
        tr = (
            Trelliscope(iris_df, "Iris", path=temp_dir_name)
            .set_panel(Panel("img_panel", aspect_ratio=1.5))
            .write_display()
        )

        # infer panels explicitly (chained)
        # tr = (Trelliscope(iris_df, "Iris", path=temp_dir_name)
        #     .infer_panels()
        #     .write_display())

        # infer panels implicitly
        tr = Trelliscope(iris_df, "Iris", path=temp_dir_name).write_display()


def test_panel_options_init():
    # default params
    panel_options = PanelOptions()
    assert panel_options.width == 600
    assert panel_options.height == 400
    assert panel_options.aspect == pytest.approx(1.5, 0.01)
    assert panel_options.format is None
    assert panel_options.force == False
    assert panel_options.prerender == True
    assert panel_options.type is None

    # specified params (except aspect ratio)
    panel_options = PanelOptions(
        width=500,
        height=500,
        format="png",
        force=True,
        prerender=False,
        type=Panel._PANEL_TYPE_IMAGE,
    )
    assert panel_options.width == 500
    assert panel_options.height == 500
    assert panel_options.aspect == pytest.approx(1.0, 0.01)
    assert panel_options.format == "png"
    assert panel_options.force == True
    assert panel_options.prerender == False
    assert panel_options.type == Panel._PANEL_TYPE_IMAGE

    # specified params (including aspect ratio)
    panel_options = PanelOptions(
        width=500,
        height=500,
        format="png",
        force=True,
        prerender=False,
        type=Panel._PANEL_TYPE_IMAGE,
        aspect=2.0,
    )
    assert panel_options.width == 500
    assert panel_options.height == 500
    assert panel_options.aspect == pytest.approx(2.0, 0.01)
    assert panel_options.format == "png"
    assert panel_options.force == True
    assert panel_options.prerender == False
    assert panel_options.type == Panel._PANEL_TYPE_IMAGE

    with pytest.raises(ValueError):
        panel_options = PanelOptions(format="doc")


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

    # po1 = tr.panel_options["Sepal.Length"]
    # po2 = tr.panel_options["Sepal.Width"]

    po1 = tr._get_panel_options("Sepal.Length")
    po2 = tr._get_panel_options("Sepal.Width")
    po3 = tr._get_panel_options("Unknown panel")

    assert po3 is None

    assert po1.width == 600
    assert po1.height == 400
    assert po1.aspect == pytest.approx(1.5, 0.01)
    assert po1.format is None
    assert po1.force == False
    assert po1.prerender == True
    assert po1.type is None

    assert po2.width == 500
    assert po2.height == 500
    assert po2.aspect == pytest.approx(1.0, 0.01)
    assert po2.format == "png"
    assert po2.force == True
    assert po2.prerender == False
    assert po2.type == Panel._PANEL_TYPE_IMAGE


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
