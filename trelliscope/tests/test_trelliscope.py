import pytest
import pandas as pd
from trelliscope.trelliscope import Trelliscope
from trelliscope.panels import Panel, ImagePanel, IFramePanel

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

# def test_standard_setup(iris_df: pd.DataFrame):
#     tr = Trelliscope(iris_df, "Iris")
    
#     # This will infer the panels if they have not been set
#     tr.write_display()

#     iris_df["img_panel"] = True;

#     # use panel in init
#     pnl = Panel("img_panel", aspect_ratio=1.5)
#     tr = Trelliscope(iris_df, "Iris", panel=pnl)
#     tr.write_display()

#     # set panel after init
#     tr = Trelliscope(iris_df, "Iris", panel=pnl)
#     tr.set_panel(Panel("img_panel", aspect_ratio=1.5))
#     tr.write_display()

#     # set derived class panel
#     tr = Trelliscope(iris_df, "Iris", panel=pnl)
#     tr.set_panel(ImagePanel("img_panel", aspect_ratio=1.5))
#     tr.write_display()

#     # set derived class panel
#     tr = Trelliscope(iris_df, "Iris", panel=pnl)
#     tr.set_panel(IFramePanel("img_panel", aspect_ratio=1.5, is_local=True))
#     tr.write_display()

#     # chain panel methods    
#     tr = (Trelliscope(iris_df, "Iris")
#           .set_panel(pnl = Panel("img_panel", aspect_ratio=1.5))
#           .write_display())

#     # infer panels explicitly (chained)
#     tr = (Trelliscope(iris_df, "Iris")
#         .infer_panels()
#         .write_display())

#     # infer panels implicitly
#     tr = Trelliscope(iris_df, "Iris").write_display()
