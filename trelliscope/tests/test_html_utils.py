import tempfile
from pathlib import Path

from trelliscope import html_utils


def test_get_index_html_content():
    version = "0.2.3"
    id = "abc123"

    with tempfile.TemporaryDirectory():
        html = html_utils._get_index_html_content(
            trelliscope_id=id, javascript_version=version
        )

        assert (
            f'<script src="https://unpkg.com/trelliscopejs-lib@{version}/dist/assets/index.js"></script>'
            in html
        )
        assert (
            f'<link href="https://unpkg.com/trelliscopejs-lib@{version}/dist/assets/index.css" rel="stylesheet" />'
            in html
        )

        assert f"<body onload=\"trelliscopeApp('{id}', 'config.jsonp')\">" in html
        assert f'<div id="{id}" class="trelliscope-spa">' in html


def test_write_index_html():
    version = "0.4.6"
    id = "def456"

    with tempfile.TemporaryDirectory() as output_dir:
        html_utils.write_index_html(
            output_dir, trelliscope_id=id, javascript_version=version
        )

        index_html_file = Path(output_dir) / "index.html"

        assert Path(index_html_file).is_file()

        with open(index_html_file) as input_file:
            html = input_file.read()

            assert (
                f'<script src="https://unpkg.com/trelliscopejs-lib@{version}/dist/assets/index.js"></script>'
                in html
            )
            assert (
                f'<link href="https://unpkg.com/trelliscopejs-lib@{version}/dist/assets/index.css" rel="stylesheet" />'
                in html
            )

            assert f"<body onload=\"trelliscopeApp('{id}', 'config.jsonp')\">" in html
            assert f'<div id="{id}" class="trelliscope-spa">' in html


def test_write_id_file():
    id = "def456"

    with tempfile.TemporaryDirectory() as output_dir:
        html_utils.write_id_file(output_dir, trelliscope_id=id)

        id_file = Path(output_dir) / "id"

        assert Path(id_file).is_file()

        with open(id_file) as input_file:
            id_from_file = input_file.read()

            assert id_from_file.strip() == id
