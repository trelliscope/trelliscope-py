"""Contains utility functions that facilitate writing the html and support files for viewing."""
from pathlib import Path

DEFAULT_JAVASCRIPT_VERSION = "0.7.5"


def write_index_html(
    output_path: str, trelliscope_id: str, javascript_version: str = None
) -> None:
    """Writes the main index.html file for the Trelliscope to the output directory.

    Args:
        output_path: The absolute path to the directory that will contain
            the file.
        trelliscope_id: The ID of the Trelliscope object.
        javascript_version: The version of the Trelliscope JavaScript library
            to include from the CDN. If none is provided, the value will be
            read from the main config file.
    """
    if javascript_version is None:
        javascript_version = DEFAULT_JAVASCRIPT_VERSION

    html_content = _get_index_html_content(trelliscope_id, javascript_version)
    html_file = Path(output_path) / "index.html"

    with open(html_file, "w") as output_file:
        output_file.write(html_content)


def _get_index_html_content(trelliscope_id: str, javascript_version: str) -> str:
    """Gets the contents of the base index.html page.

    Args:
        trelliscope_id: The ID of the Trelliscope object.
        javascript_version: The version of the Trelliscope
            JavaScript library to include from the CDN.

    Returns:
        A string containing the html to write.
    """
    # Note that because this is a format string any literal {}'s need to be escaped by doubling
    index_html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<script src="https://unpkg.com/trelliscopejs-lib@{javascript_version}/dist/assets/index.js"></script>
<link href="https://unpkg.com/trelliscopejs-lib@{javascript_version}/dist/assets/index.css" rel="stylesheet" />

</head>
<body onload="trelliscopeApp('{trelliscope_id}', 'config.jsonp')">
  <div id="{trelliscope_id}" class="trelliscope-spa">
</body>
</html>
"""
    return index_html_content


def write_id_file(output_path: str, trelliscope_id: str) -> None:
    """Writes the id file that belongs in the main output directory.

    Args:
        output_path: The absolute path to the directory that will contain
            the file.
        trelliscope_id: The ID of the Trelliscope object.
    """
    id_file = Path(output_path) / "id"

    with open(id_file, "w") as output_file:
        output_file.write(trelliscope_id)
