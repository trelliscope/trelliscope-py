import pytest
import os
import pandas as pd
import tempfile
from trelliscope import html_utils

def test_write_javascript(mars_df: pd.DataFrame):
    with tempfile.TemporaryDirectory() as output_dir:
        html_utils.write_javascript_lib(output_dir)

        expected_lib_dir = os.path.join(output_dir, "lib")
        assert os.path.isdir(expected_lib_dir)

        files = os.listdir(expected_lib_dir)

        # Check if at least one item in the directory contains the
        # substring with part of the expected lib name (we don't want to)
        # test for a certain version number
        assert any(("htmlwidgets" in file) for file in files)
        assert any(("trelliscope_widget" in file) for file in files)
        assert any(("trelliscope_widget-binding" in file) for file in files)

        for file in files:
            if "trelliscope_widget-binding" in file:
                widget_binding_dir = os.path.join(expected_lib_dir, file)
                
                widget_files = os.listdir(widget_binding_dir)
                assert "trelliscope_widget.js" in widget_files
