import pytest
import os
import pandas as pd
from trelliscope.trelliscope import Trelliscope
from trelliscope.panels import Panel, ImagePanel, IFramePanel

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
    assert "panel_type" in dict

    assert dict["name"] == "iris"
    
def test_no_name(iris_df: pd.DataFrame):
    tr = Trelliscope(iris_df, "iris")

    # Trelliscopes need a name param
    with pytest.raises(TypeError, match=r"missing .* required .* argument"):
        tr = Trelliscope(iris_df)

def test_no_img_panel(iris_df: pd.DataFrame):
    # Trelliscopes need an image panel
    with pytest.raises(ValueError, match=r"that references a plot or image"):
        tr = Trelliscope(iris_df, "Iris")

    # TODO: SB: In the new approach, I think this could be inferred later
    # during the write process or something, so I think this should not raise
    # an error at this point.

def test_standard_setup(iris_df: pd.DataFrame):
    # this is test code that just sets all images to this test_image.png string
    # it is not a proper use of the images, but gives us something to use in testing.
    iris_df["img_panel"] = "test_image.png"

    tr = Trelliscope(iris_df, "Iris")
    tr.set_panel(ImagePanel("img_panel"))
    tr.write_display()

def test_write_javascript(mars_df: pd.DataFrame):
    tr = Trelliscope(mars_df, "mars_rover")
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
    tr.set_panel(ImagePanel("img_src"))
    
    tr2 = tr._get_thumbnail_url()
    first_value = mars_df["img_src"][0]

    assert tr2.thumbnail_url == first_value
    

@pytest.mark.skip("panel format not implemented yet.")
def test_get_thumbnail_url_with_format(mars_df: pd.DataFrame):
    """
    Tests the case where the thumbnail url comes from a panel_format,
    in other words panels created by the trelliscope lib
    """
    raise NotImplementedError()

    first_value = mars_df["img_src"][0]
    filename = os.path.join(Trelliscope.DISPLAYS_DIR, "mars_rover", Trelliscope.PANELS_DIR)

