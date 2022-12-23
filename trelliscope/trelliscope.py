#TODO: Decide how to handle type hints for return type of Trelliscope
# This enables type hints for the return type to be Trelliscope
# from __future__ import annotations
# This is now the proper way to do type hints for the return type of the
# enclosing class, but it requires Python 3.11
# from typing import Self


#import tempfile
import copy
import os
import uuid
import json
import shutil
import pandas as pd


class Trelliscope:
    """
    A Trelliscope Display Object.
    """

    DISPLAYS_DIR = "displays"
    CONFIG_FILE_NAME = "config.jsonp"
    DISPLAY_LIST_FILE_NAME = "displayList.jsonp"
    DISPLAY_INFO_FILE_NAME = "displayInfo.jsonp"
    METADATA_FILE_NAME = "metaData.jsonp"

    def __init__(self, dataFrame: pd.DataFrame, name: str, description: str = None, key_cols = None, tags = None,
            path = None, force_plot = False):
        """
        Instantiate a Trelliscope display object.

        Args:
            dataFrame: A data frame that contains the metadata of the display as well as
                a column that indicates the panels to be displayed.
            name: Name of the trelliscope display.
            description: Description of the trelliscope display. If none is provided, the
                name will be used as the description.
            key_cols: Variable names in the data frame that uniquely define a row of the
                data. If not supplied, an attempt will be made to infer them.
            tags: Optional vector of tag names to identify the display in the case that
                there are many to search through.
            path: Directory in which to place the trelliscope display when it is written
                using [`write_display()`].
            force_plot: Should the panels be forced to be plotted, even if they have
                already been plotted and have not changed since the previous plotting?
        """

        self._data_frame = dataFrame
        self._name: str = name
        self._description = description
        self._key_cols = key_cols
        self._tags = tags
        self._path = path
        self._force_plot = force_plot
        #TODO: Is there a reason this is not a true uuid?
        self._id = uuid.uuid4().hex[:8]

        if self._description is None:
            self._description = self._name

        if self._tags is None:
            self._tags = []

        if self._key_cols is None:
            # TODO: Infer this somehow...
            self._key_cols = ["name"]

    def write_display(self):
        # TODO: Do we want to use the temp file context manager so our files are cleaned up after?
        # Or is the point to leave it around for a while?
        # https://docs.python.org/3/library/tempfile.html
        # if self._path is None:
        #     self.path = tempfile.TemporaryDirectory()
        # the context object is used like this:
        # with tempfile.TemporaryDirectory() as tmpdirname:

        #TODO: See how to handle names with multiple words, etc.
        #TODO: Do we care about other special characters here?
        name_dir = self._name.lower().replace(" ", "_")

        output_dir = os.path.join(self._path, name_dir)
        print(f"Saving to {output_dir}")

        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        displays_dir = os.path.join(output_dir, Trelliscope.DISPLAYS_DIR)

        # appfiles_dir = os.path.join(output_dir, Trelliscope.APPFILES_DIR)
        # display_group_dir = os.path.join(displays_dir, self._display_group)
        # display_name_dir = os.path.join(display_group_dir, self._dataset_name)

        os.makedirs(output_dir)
        os.makedirs(displays_dir)

        self._write_config_file(output_dir)
        self._write_displays(displays_dir)

        return self.__copy()

    def _write_config_file(self, output_dir):
        file_path = os.path.join(output_dir, Trelliscope.CONFIG_FILE_NAME)

        config_dict = {"name": "Trelliscope App",
                        "data_type": "jsonp",
                        "id" : self._id}
        config_json = json.dumps(config_dict, indent=2)

        output_content = f"__loadAppConfig__{self._id}({config_json})"

        with open(file_path, "w") as output_file:
            output_file.write(output_content)
            
    def _write_displays(self, displays_dir: str):
        file_path = os.path.join(displays_dir, Trelliscope.DISPLAY_LIST_FILE_NAME)

        display_list = []

        #TODO: This is a list instead of a dictionary... is it possible to have more
        # than just this one item in the list??
        # If so the following should be in a loop
        display_info_dict = {"name": self._name,
                            "description": self._description,
                            "tags": self._tags}
        display_list.append(display_info_dict)

        self._write_single_display(self._name, displays_dir)

        # TODO: End loop

        # Now, write out the display list file
        display_list_json = json.dumps(display_list, indent=2)
        output_content = f"__loadDisplayList__{self._id}({display_list_json})"

        with open(file_path, "w") as output_file:
            output_file.write(output_content)

    def _write_single_display(self, name: str, displays_dir: str):
        single_display_dir = os.path.join(displays_dir, name)
        os.makedirs(single_display_dir)

        self._write_display_info(single_display_dir)
        self._write_meta_data(single_display_dir)

    def _write_display_info(self, output_dir: str):
        # TODO: This will need to be refactored if there are more than
        # one display info to print out. This assumes the member variables
        # define all the information, rather than passing in unique params
        file_path = os.path.join(output_dir, Trelliscope.DISPLAY_INFO_FILE_NAME)

        metas_list = self._get_metas_list()

        # TODO: Fill in all the state variables based on actual settings

        display_info_dict = {
            "name": self._name,
            "description": self._description,
            "tags": self._tags,
            "key_cols": self._key_cols,
            "metas": metas_list,
            "state": {
                "layout": {
                "page": 1,
                "arrange": "rows",
                "ncol": 3,
                "nrow": 2,
                "type": "layout"
                },
                "labels": {
                "varnames": ["name"],
                "type": "labels"
                },
                "sort": [],
                "filter": []
            },
            "views": [],
            "inputs": [],
            "panel_type": "img"
        }

        display_info_json = json.dumps(display_info_dict, indent=2)
        output_content = f"__loadDisplayInfo__{self._id}({display_info_json})"

        with open(file_path, "w") as output_file:
            output_file.write(output_content)

    def _get_metas_list(self) -> list:
        metas =  []

        for col_name in self._data_frame.columns:
            meta_info = self._get_meta_info_for_column(col_name)
            metas.append(meta_info)

        return metas

    def _get_meta_info_for_column(self, col_name):
        meta = {}

        col = self._data_frame[col_name]
        meta["varname"] = col_name
        meta["label"] = col_name # TODO: find where this can be different
        meta["sortable"] = True # Default to True
        meta["filterable"] = True # Default to True
        meta["tags"] = [] # TODO: Fill this in...

        if col.dtype == "object":
            # this is a string column
            # TODO: check for other types of "object" columns
            
            # TODO: Improve this check to infer href
            if str(col[0]).startswith("http"):
                # This appears to be an href column
                meta["type"] = "href"
                meta["sortable"] = False
                meta["filterable"] = False
            else:
                # This appears to be a regular string column
                meta["type"] = "string"

        elif col.dtype == "category":
            raise NotImplementedError("category type is not implemented")
        elif col.dtype == "float64":
            raise NotImplementedError("float64 type is not implemented")
        elif col.dtype == "int64":
            meta["type"] = "number"
            meta["locale"] = True # TODO: What is this?
            meta["digits"] = None # TODO: What is this?

        return meta

    def _write_meta_data(self, output_dir: str):
        # TODO: This will need to be refactored if there are more than
        # one display info to print out. This assumes the member variables
        # define all the information, rather than passing in unique params
        file_path = os.path.join(output_dir, Trelliscope.METADATA_FILE_NAME)

        output_content = ""

        with open(file_path, "w") as output_file:
            output_file.write(output_content)


    def write_panels(self):
        return self.__copy()

    def add_meta_defs(self):
        return self.__copy()

    def add_meta_labels(self):
        return self.__copy()
    
    def set_labels(self):
        return self.__copy()

    def set_layout(self):
        return self.__copy()

    def set_sort(self):
        return self.__copy()

    def set_filters(self):
        return self.__copy()

    def add_view(self):
        return self.__copy()

    def add_inputs(self):
        return self.__copy()

    def __copy(self):
        return copy.deepcopy(self)
