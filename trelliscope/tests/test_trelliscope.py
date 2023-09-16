import pytest
import os
import tempfile
import pandas as pd
from trelliscope.trelliscope import Trelliscope
from trelliscope.panels import Panel, ImagePanel, IFramePanel
from trelliscope.panel_source import FilePanelSource
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
        tr.add_panel(ImagePanel("img_panel", source=FilePanelSource(True), should_copy_to_output=False))
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
    tr.add_panel(ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False))
    
    tr2 = tr._infer_thumbnail_url()
    first_value = mars_df["img_src"][0]

    assert tr2.thumbnail_url == first_value

def test_get_panel_columns(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    tr = Trelliscope(mars_df, "mars_rover")
    tr.add_panel(ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False))
    tr.add_panel(ImagePanel("img2", source=FilePanelSource(False), should_copy_to_output=False))

    panels = tr._get_panel_columns()

    assert set(panels) == {"img_src", "img2"}

def test_get_panel_output_path(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]


    with tempfile.TemporaryDirectory() as output_dir:        
        tr = Trelliscope(mars_df, "mars_rover", path=output_dir)
        tr.add_panel(ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False))
        tr.add_panel(ImagePanel("img2", source=FilePanelSource(False), should_copy_to_output=False))

        expected_abs_path = os.path.join(output_dir,
                                         "mars_rover",
                                         "displays",
                                         "mars_rover",
                                         "panels",
                                         "img_src")
        actual_abs_path = tr._get_panel_output_path("img_src", True)
        assert os.path.normpath(expected_abs_path) == os.path.normpath(actual_abs_path)

        expected_rel_path = os.path.join("panels", "img_src")
        actual_rel_path = tr._get_panel_output_path("img_src", False)
        assert os.path.normpath(expected_rel_path) == os.path.normpath(actual_rel_path)


def test_get_panel_from_col_name(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    tr = Trelliscope(mars_df, "mars_rover")

    panel1 = ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False)
    tr.add_panel(panel1)
    panel2 = ImagePanel("img2", source=FilePanelSource(False), should_copy_to_output=False)
    tr.add_panel(panel2)

    assert panel1 == tr._get_panel("img_src")
    assert panel2 == tr._get_panel("img2")


def test_infer_primary_panel(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    tr = Trelliscope(mars_df, "mars_rover")
    tr.add_panel(ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False))
    tr.add_panel(ImagePanel("img2", source=FilePanelSource(False), should_copy_to_output=False))

    assert tr.primary_panel is None

    tr._infer_primary_panel()

    # It would be nice to know that infer will get the "first" one,
    # but because they are stored in a dictionary, order is not
    # guaranteed. All we know is that it will be one of them.
    assert tr.primary_panel in ("img_src", "img2")

def test_copy_images_to_build_directory():
    raise NotImplementedError()

def test_set_default_sort(mars_df: pd.DataFrame):
    mars_df["img2"] = mars_df["img_src"]
    mars_df["img3"] = mars_df["img_src"]

    tr = Trelliscope(mars_df, "mars_rover")
    tr.add_panel(ImagePanel("img_src", source=FilePanelSource(True), should_copy_to_output=False))
    tr.add_panel(ImagePanel("img2", source=FilePanelSource(False), should_copy_to_output=False))

    tr = tr.set_default_sort(["img2", "img3"])

    assert(len(tr.state.sort) == 2)
    
    sort_keys = list(tr.state.sort.keys())

    ss1:SortState = tr.state.sort[sort_keys[0]]
    ss2:SortState = tr.state.sort[sort_keys[1]]

    assert ss1.varname == "img2"
    assert ss2.varname == "img3"

    assert ss1.dir == SortState.DIR_ASCENDING
    assert ss2.dir == SortState.DIR_ASCENDING

    assert ss1.metatype is None

    # Overwrite
    tr = tr.set_default_sort(["img_src", "img2"], ["asc", "desc"])

    assert(len(tr.state.sort) == 2)
    
    sort_keys = list(tr.state.sort.keys())

    ss1:SortState = tr.state.sort[sort_keys[0]]
    ss2:SortState = tr.state.sort[sort_keys[1]]

    assert ss1.varname == "img_src"
    assert ss2.varname == "img2"

    assert ss1.dir == SortState.DIR_ASCENDING
    assert ss2.dir == SortState.DIR_DESCENDING

    # Append
    tr = tr.set_default_sort(["img3"], add=True)

    assert(len(tr.state.sort) == 3)
    
    sort_keys = list(tr.state.sort.keys())

    ss1:SortState = tr.state.sort[sort_keys[0]]
    ss2:SortState = tr.state.sort[sort_keys[1]]
    ss3:SortState = tr.state.sort[sort_keys[2]]

    assert ss1.varname == "img_src"
    assert ss2.varname == "img2"
    assert ss3.varname == "img3"

    assert ss1.dir == SortState.DIR_ASCENDING
    assert ss2.dir == SortState.DIR_DESCENDING
    assert ss3.dir == SortState.DIR_ASCENDING

    # Try wrong number of directions
    with pytest.raises(ValueError, match=r"'varnames' must have same length as 'dirs'"):
        tr.set_default_sort(["a", "b", "c"], ["asc", "desc"])

def test_infer_state():
    # TODO: Make sure to test the intersection of CategoryFilter levels and Factor meta levels.
    raise NotImplementedError()

def test_set_primary_panel():
    # Test setting one that is not a valid panel to ensure
    # the exception is raised

    raise NotImplementedError()