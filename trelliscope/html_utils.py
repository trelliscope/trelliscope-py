"""
Contains utility functions that facilitate the html, JavaScript,
and other widgets needed for Trelliscope viewing.
"""
import json
import os
import shutil
import uuid
from importlib import resources

JAVASCRIPT_SOURCE_PACKAGE = "trelliscope.resources.javascript"


def write_javascript_lib(output_path: str) -> None:
    """
    Writes the JavaScript lib code to the directory specified.

    Params:
        output_path:str - The path to the parent directory to
            write to, (not including "lib").
    """
    for file in resources.files(JAVASCRIPT_SOURCE_PACKAGE).iterdir():
        if file.is_dir():
            # base_name = os.path.basename(file)
            dir_name = file.name

            new_output = os.path.join(output_path, dir_name)

            # TODO: verify that this works if the package is zipped, etc.
            shutil.copytree(file, new_output)


def write_widget(
    output_path: str, trelliscope_id: str, config_info: str, is_spa: bool
) -> None:
    html_content = _get_index_html_content(
        output_path, trelliscope_id, config_info, is_spa
    )
    html_file = os.path.join(output_path, "index.html")

    with open(html_file, "w") as output_file:
        output_file.write(html_content)


def _get_index_html_content(
    output_path: str, trelliscope_id: str, config_info: str, is_spa: bool
) -> str:
    # TODO: Decide how to handle Javascript file version numbers to include
    HTML_WIDGET_FILE = "lib/htmlwidgets-1.6.2/htmlwidgets.js"
    CSS_FILE = "lib/trs-0.6.0/css/main.74ce0792.css"
    TRELLISCOPE_WIDGET_FILE = "lib/trs-0.6.0/js/main.173baec5.js"
    TRELLISCOPE_WIDGET_BINDING_FILE = "lib/trs-binding-0.1.3/trs.js"

    # TODO: What is this? Where does it come from?
    # It is something like "376b27d6688cc9ba8689"
    html_widget_id = uuid.uuid4().hex

    width = ""
    height = ""

    if is_spa:
        width = "100vw"
        height = "100vh"

    widget_params = {
        "x": {"id": trelliscope_id, "config_info": config_info, "spa": is_spa},
        "evals": [],
        "jsHooks": [],
    }

    widget_params_str = json.dumps(widget_params)

    # Note that because this is a format string and {}'s need to be escaped by doubling
    index_html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<style>body{{background-color:white;}}</style>
<script src="{HTML_WIDGET_FILE}"></script>
<link href="{CSS_FILE}" rel="stylesheet" />
<script src="{TRELLISCOPE_WIDGET_FILE}"></script>
<script src="{TRELLISCOPE_WIDGET_BINDING_FILE}"></script>

</head>
<body>
<div id="htmlwidget-{html_widget_id}" style="width:{width};height:{height};" class="trs html-widget "></div>
<script type="application/json" data-for="htmlwidget-{html_widget_id}">{widget_params_str}</script>
</body>
</html>
"""
    return index_html_content
