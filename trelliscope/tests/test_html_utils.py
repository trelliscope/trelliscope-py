import os
import re
import tempfile

import pandas as pd

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
        assert any(("htmlwidgets-" in file) for file in files)
        assert any(("trs-" in file) for file in files)
        assert any(("trs-binding-" in file) for file in files)

        for file in files:
            if "trelliscope_widget-binding" in file:
                widget_binding_dir = os.path.join(expected_lib_dir, file)

                widget_files = os.listdir(widget_binding_dir)
                assert "trelliscope_widget.js" in widget_files


def test_get_index_html_content():
    with tempfile.TemporaryDirectory() as output_dir:
        html = html_utils._get_index_html_content(
            output_dir, "abc123", "config.jsonp", True
        )

        assert '<script src="lib/htmlwidgets' in html
        assert '<script src="lib/trs-binding' in html
        assert '<div id="htmlwidget-' in html
        assert re.search(r'"id":\s*"abc123"', html)
        assert re.search(r'"config_info":\s*"config.jsonp"', html)


def test_write_widget():
    with tempfile.TemporaryDirectory() as output_dir:
        html_utils.write_widget(output_dir, "abc123", "config.jsonp", True)

        index_html_file = os.path.join(output_dir, "index.html")

        assert os.path.isfile(index_html_file)

        with open(index_html_file) as input_file:
            html = input_file.read()

            assert '<script src="lib/htmlwidgets' in html
            assert '<script src="lib/trs-binding' in html
            assert '<div id="htmlwidget-' in html
            assert re.search(r'"id":\s*"abc123"', html)
            assert re.search(r'"config_info":\s*"config.jsonp"', html)
