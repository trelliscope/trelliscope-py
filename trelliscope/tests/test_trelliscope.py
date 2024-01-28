import os
import shutil
import tempfile
import urllib.request

import pandas as pd
import pytest

from trelliscope import Trelliscope
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
    tr = Trelliscope(iris_df, "iris")

    # Trelliscopes need a name param
    with pytest.raises(TypeError, match=r"missing .* required .* argument"):
        tr = Trelliscope(iris_df)


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

        # Clean up


def test_write_javascript(mars_df: pd.DataFrame):
    with tempfile.TemporaryDirectory() as output_dir:
        tr = Trelliscope(mars_df, "mars_rover", path=output_dir)
        tr._create_output_dirs()
        tr._write_javascript_lib()

        expected_lib_dir = os.path.join(tr.get_output_path(), "lib")
        assert os.path.isdir(expected_lib_dir)


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


@pytest.mark.skip(
    "Need to find a new set of images to download, because nasa.gov is taking a long time."
)
def test_copy_images_to_build_directory(mars_df: pd.DataFrame):
    mars_df = mars_df[:3]  # reduce to two rows

    with tempfile.TemporaryDirectory() as output_dir:
        with tempfile.TemporaryDirectory() as temp_dir2:
            # download the images to a temp directory and update the data frame
            for i in range(len(mars_df)):
                original_file = mars_df["img_src"][i]
                file_name = os.path.basename(original_file)
                temp_dir_file = os.path.join(temp_dir2, file_name)

                with urllib.request.urlopen(original_file, timeout=1) as response, open(
                    temp_dir_file, "wb"
                ) as out_file:
                    shutil.copyfileobj(response, out_file)

                mars_df["img_src"][i] = temp_dir_file

            tr = Trelliscope(mars_df, "mars_rover", path=output_dir)
            tr = tr.add_panel(
                ImagePanel("img_src", FilePanelSource(True), should_copy_to_output=True)
            )

            # At first, the image should be in the temp dir that we put it in
            original_image = tr.data_frame["img_src"][0]
            assert temp_dir2 in original_image

            tr = tr.write_display()

            # Now the image should not be in the temp dir
            new_image = tr.data_frame["img_src"][0]
            new_image_full_path = os.path.join(tr.get_dataset_display_path(), new_image)
            assert temp_dir2 not in new_image_full_path

            # But the image should exist in the output dir
            assert output_dir in new_image_full_path
            assert os.path.exists(new_image_full_path)


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

    assert len(tr.state.sort) == 2

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

    assert len(tr.state.sort) == 2

    sort_keys = list(tr.state.sort.keys())

    ss1: SortState = tr.state.sort[sort_keys[0]]
    ss2: SortState = tr.state.sort[sort_keys[1]]

    assert ss1.varname == "img_src"
    assert ss2.varname == "img2"

    assert ss1.dir == SortState.DIR_ASCENDING
    assert ss2.dir == SortState.DIR_DESCENDING

    # Append
    tr = tr.set_default_sort(["img3"], add=True)

    assert len(tr.state.sort) == 3

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


@pytest.mark.skip("Need to better understand the rules of inferring states")
def test_infer_state(mars_df: pd.DataFrame):
    with tempfile.TemporaryDirectory() as output_dir:
        tr = Trelliscope(mars_df, "mars_rover", path=output_dir)
        tr._infer_state(tr.state)

    raise NotImplementedError()
    # TODO: Make sure to test the intersection of CategoryFilter levels and Factor meta levels.


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


@pytest.mark.skip("Test these when inputs are functioning")
def test_add_input(mars_df: pd.DataFrame):
    raise NotImplementedError


@pytest.mark.skip("Test these when inputs are functioning")
def test_add_inputs(mars_df: pd.DataFrame):
    raise NotImplementedError
