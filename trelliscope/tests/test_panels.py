import tempfile
import pytest
import pandas as pd
from trelliscope.trelliscope import Trelliscope
from trelliscope.panels import Panel, ImagePanel, IFramePanel

def test_panels_setup(iris_df: pd.DataFrame):
    
    with tempfile.TemporaryDirectory() as temp_dir_name:
        # this is test code that just sets all images to this test_image.png string
        # it is not a proper use of the images, but gives us something to use in testing.
        iris_df["img_panel"] = "test_image.png"
        
        pnl = ImagePanel("img_panel", aspect_ratio=1.5, is_local=True)
        tr = Trelliscope(iris_df, "Iris", panel=pnl, path=temp_dir_name)

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
        tr = (Trelliscope(iris_df, "Iris", path=temp_dir_name)
            .set_panel(Panel("img_panel", aspect_ratio=1.5))
            .write_display())

        # infer panels explicitly (chained)
        # tr = (Trelliscope(iris_df, "Iris", path=temp_dir_name)
        #     .infer_panels()
        #     .write_display())

        # infer panels implicitly
        tr = Trelliscope(iris_df, "Iris", path=temp_dir_name).write_display()
