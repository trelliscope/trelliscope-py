import pytest
from trelliscope.trelliscope import Trelliscope

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
    
