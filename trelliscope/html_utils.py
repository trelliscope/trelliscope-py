"""
Contains utility functions that facilitate the html, JavaScript,
and other widgets needed for Trelliscope viewing.
"""
import os
import shutil
from importlib import resources

JAVASCRIPT_SOURCE_PACKAGE = "trelliscope.resources.javascript"

def write_javascript_lib(output_path:str) -> None:
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

