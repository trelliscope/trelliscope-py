import pytest
import pandas as pd
from trelliscope.trelliscope import Trelliscope
from trelliscope.panels import Panel, ImagePanel, IFramePanel

def test_panels_setup(iris_df: pd.DataFrame):
    # this is test code that just sets all images to this test_image.png string
    # it is not a proper use of the images, but gives us something to use in testing.
    iris_df["img_panel"] = "test_image.png"
    
    pnl = ImagePanel("img_panel", aspect_ratio=1.5, is_local=True)
    tr = Trelliscope(iris_df, "Iris", panel=pnl)

    tr.write_display()

def test_panels_setup_options(iris_df: pd.DataFrame):
    tr = Trelliscope(iris_df, "Iris")
    
    # This will infer the panels if they have not been set
    tr.write_display()

    # this is test code that just sets all images to this test_image.png string
    # it is not a proper use of the images, but gives us something to use in testing.
    iris_df["img_panel"] = "test_image.png"

    # use panel in init
    pnl = Panel("img_panel", aspect_ratio=1.5)
    tr = Trelliscope(iris_df, "Iris", panel=pnl)
    tr.write_display()

    # set panel after init
    tr = Trelliscope(iris_df, "Iris")
    tr.set_panel(Panel("img_panel", aspect_ratio=1.5))
    
    tr.write_display()

    # set derived class panel
    tr = Trelliscope(iris_df, "Iris")
    tr.set_panel(ImagePanel("img_panel", aspect_ratio=1.5))
    tr.write_display()

    # set derived class panel
    tr = Trelliscope(iris_df, "Iris")
    tr.set_panel(IFramePanel("img_panel", aspect_ratio=1.5, is_local=True))
    tr.write_display()

    # chain panel methods    
    tr = (Trelliscope(iris_df, "Iris")
          .set_panel(pnl = Panel("img_panel", aspect_ratio=1.5))
          .write_display())

    # infer panels explicitly (chained)
    tr = (Trelliscope(iris_df, "Iris")
        .infer_panels()
        .write_display())

    # infer panels implicitly
    tr = Trelliscope(iris_df, "Iris").write_display()
