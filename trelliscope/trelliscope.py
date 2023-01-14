# TODO: Decide how to handle type hints for return type of Trelliscope
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
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

import logging
logging.basicConfig(level=logging.DEBUG)

from .metas import Meta, StringMeta, NumberMeta, HrefMeta
from .state import DisplayState
from .view import View
from .input import Input

class Trelliscope:
    """
    Main interface for creating and writing Trelliscopes.
    """

    DISPLAYS_DIR = "displays"
    CONFIG_FILE_NAME = "config.jsonp"
    DISPLAY_LIST_FILE_NAME = "displayList.jsonp"
    DISPLAY_INFO_FILE_NAME = "displayInfo.jsonp"
    METADATA_FILE_NAME = "metaData.jsonp"

    def __init__(self, dataFrame: pd.DataFrame, name: str, description: str = None, key_cols = None, tags = None,
            path = None, force_plot = False, panel_col = None, debug = False):
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

        # TODO: Add lots of checks here to ensure the data types match etc

        self._data_frame: pd.DateOffset = dataFrame
        self._name: str = name
        self._description: str = description
        self._tags: list = tags
        self._key_cols: list = key_cols
        self._path: str = path
        self._force_plot: bool = force_plot
        self._panel_col = panel_col
        self._debug = debug

        #TODO: Is there a reason this is not a true uuid?
        self._id = uuid.uuid4().hex[:8]

        if self._description is None:
            self._description = self._name

        if self._tags is None:
            self._tags = []

        if self._key_cols is None:
            # TODO: Infer this somehow or make sure it's set on the df...
            self._key_cols = ["name"]

        self._metas = {}
        self._columns_to_ignore = []
        self._state = DisplayState()
        
        self._views = {}
        self._inputs = {}
        self._type_type = None

    def set_meta(self, meta: Meta):
        if not issubclass(meta, Meta):
            raise ValueError("Error: Meta definition must be a valid Meta class instance.")
        
        meta.check_with_data(self._data_frame)
        name = meta.varname

        if name in self._metas:
            logging.info(f"Replacing existing meta variable {name}")

        self._metas[name] = meta

    def set_metas(self, meta_list: list):
        for meta in meta_list:
            self.set_meta(meta)

    def add_meta(self, meta_name: str, meta: Meta):
        # TODO: Should we make a copy here??
        self._metas[meta_name] = meta

        return self

    def set_state(self, state: DisplayState):
        self.state = state

    def set_view(self, view: View):
        name  = view.name

        if name in self._views:
            logging.info("Replacing existing view {name}")

        self._views[name] = view

    def set_input(self, input: Input):
        name = input.name

        if name in self._inputs:
            logging.info("Replacing existing input {input}")

        self._inputs[name] = input

    def get_output_path(self) -> str:
        #TODO: See how to handle names with multiple words, etc.
        #TODO: Do we care about other special characters here?
        name_dir = self._name.lower().replace(" ", "_")

        return os.path.join(self._path, name_dir)

    def get_displays_path(self) -> str:
        output_path = self.get_output_path()
        return os.path.join(output_path, Trelliscope.DISPLAYS_DIR)
    
    # TODO: fill this in. In R, they first build a list and then to_json it here
    # def to_json(self, pretty: bool = True):

    # TODO: fill thi in with a detailed listing of everything in the trelliscope
    # def __repr__(self) -> str:
        

    def write_display(self):
        # TODO: Do we want to use the temp file context manager so our files are cleaned up after?
        # Or is the point to leave it around for a while?
        # https://docs.python.org/3/library/tempfile.html
        # if self._path is None:
        #     self.path = tempfile.TemporaryDirectory()
        # the context object is used like this:
        # with tempfile.TemporaryDirectory() as tmpdirname:

        output_dir = self.get_output_path()
        print(f"Saving to {output_dir}")

        # Remove the targeted output dir if it already exists
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        displays_dir = self.get_displays_path()
        
        os.makedirs(output_dir)
        os.makedirs(displays_dir)

        tr = self.infer()

        tr._write_config_file(output_dir)
        tr._write_displays(displays_dir)

        return tr

    def infer(self):
        tr = self._infer_metas()

        ## TODO: Fill out the state/view inferring methods

        # tr._state = self._state.infer_state(tr._data_frame, tr._key_cols, )

        # for view in tr._views:
        #     view._state = view._state.infer_state(tr._data_frame, tr._key_cols)

        return tr

    def _infer_metas(self):
        tr = self.__copy()

        # get column names from the data frame
        column_names = tr._data_frame.columns

        # compare to metas that are already defined
        existing_meta_names = tr._metas.keys()

        # go through each column name that does not have a corresponding meta
        metas_to_infer = set(column_names) - set(existing_meta_names)

        logging.debug(f"Inferring Metas: {metas_to_infer}")

        metas_to_remove = []
        metas_inferred = []

        for meta_name in metas_to_infer:
            meta = tr._infer_meta_variable(tr._data_frame[meta_name], meta_name)

            if meta is None:
                # Could not infer this meta, add to remove list
                metas_to_remove.append(meta_name)
            else:
                metas_inferred.append(meta_name)

                # Add this inferred meta to the trelliscope
                tr.add_meta(meta_name, meta)

        # Add to the ignore list any that we could not infer
        tr._columns_to_ignore.extend(metas_to_remove)

        logging.debug(f"Successfully inferred metas: {metas_inferred}")

        tr = tr._finalize_meta_labels()

        return tr

    def _infer_meta_variable(self, meta_column: pd.Series, meta_name: str):
        meta = None

        # TODO: Finish this list when all meta types are implemented

        if meta_column.dtype == "category":
            raise NotImplementedError("category type is not implemented")
        elif is_numeric_dtype(meta_column.dtype):
            meta = NumberMeta(meta_name)
        elif is_string_dtype(meta_column.dtype):
            # this is a string column
            
            # TODO: Improve this way of inferring href
            # For now, check if the first value starts with http
            if str(meta_column[0]).startswith("http"):
                # This appears to be an href column
                meta = HrefMeta(meta_name)
            else:
                # This appears to be a regular string column
                meta = StringMeta(meta_name)

        return meta
        
    def _finalize_meta_labels(self):
        # This is how this is inferred in the R code...
        # Finalize labels if NULL with the following priority:
        # 1. use from disp$meta_labels if defined
        # 2. use from attr(disp$df[[varname]], "label") if defined
        # 3. set it to varname

        # TODO: See if there is a Pandas equivalent to a column label
        # that is separate from the column name. It appears this R
        # functionality is not present in Pandas

        # TODO: if tr.__copy() doesn't make copies of metas, this needs
        # to make copies of the metas here before changing the label
        tr = self.__copy()

        for meta in self._metas.values():
            if meta.label is None:
                meta.label = meta.varname

        return tr

    def infer_state():
        pass

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
        meta_list = [meta.to_dict() for meta in self._metas.values()]
        return meta_list

    def _write_meta_data(self, output_dir: str):
        # TODO: This will need to be refactored if there is more than
        # one display info to print out. This assumes the member variables
        # define all the information, rather than passing in unique params
        file_path = os.path.join(output_dir, Trelliscope.METADATA_FILE_NAME)

        if self._debug:
            # Pretty print the json if in debug mode
            meta_data_json = self._data_frame.to_json(orient="records", indent=2)
        else:
            meta_data_json = self._data_frame.to_json(orient="records")

        # Turn the escaped \/ into just /
        meta_data_json = meta_data_json.replace("\\/", "/")

        output_content = f"__loadMetaData__{self._id}({meta_data_json})"

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
        # TODO: Should this do a deep copy? Should it make copies of metas?
        return copy.deepcopy(self)
