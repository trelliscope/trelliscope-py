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
import re
import glob
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

import logging
logging.basicConfig(level=logging.DEBUG)

from .metas import Meta, StringMeta, NumberMeta, HrefMeta, FactorMeta
from .state import DisplayState, LayoutState, LabelState
from .view import View
from .input import Input

class Trelliscope:
    """
    Main interface for creating and writing Trelliscopes.
    """

    DISPLAYS_DIR = "displays"
    CONFIG_FILE_NAME = "config"
    DISPLAY_LIST_FILE_NAME = "displayList"
    DISPLAY_INFO_FILE_NAME = "displayInfo"
    METADATA_FILE_NAME = "metaData"

    def __init__(self, dataFrame: pd.DataFrame, name: str, description: str = None, key_cols = None, tags = None,
            path = None, force_plot = False, panel_col = None, debug = False):
        """
        Instantiate a Trelliscope display object.

        Params:
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

        self.data_frame: pd.DateOffset = dataFrame
        self.name: str = name
        self.description: str = description
        self.tags: list = tags
        self.key_cols: list = key_cols
        self.path: str = path
        self.force_plot: bool = force_plot
        self.panel_col = panel_col
        self.debug = debug

        #TODO: Is there a reason this is not a true uuid?
        self.id = uuid.uuid4().hex[:8]

        if self.description is None:
            self.description = self.name

        if self.tags is None:
            self.tags = []

        if self.key_cols is None:
            # TODO: Infer this somehow or make sure it's set on the df...
            self.key_cols = ["name"]

        self.metas = {}
        self.columns_to_ignore = []
        self.state = DisplayState()
        
        self.views = {}
        self.inputs = {}
        self.panel_type = None
        self.panels_written = False

    def set_meta(self, meta: Meta):
        if not issubclass(meta, Meta):
            raise ValueError("Error: Meta definition must be a valid Meta class instance.")
        
        meta.check_with_data(self.data_frame)
        name = meta.varname

        if name in self.metas:
            logging.info(f"Replacing existing meta variable {name}")

        self.metas[name] = meta

    def set_metas(self, meta_list: list):
        for meta in meta_list:
            self.set_meta(meta)

    def add_meta(self, meta_name: str, meta: Meta):
        # TODO: Should we make a copy here??
        self.metas[meta_name] = meta

        return self

    def set_state(self, state: DisplayState):
        self.state = state

    # TODO: Verify this is acceptable as "add_view",
    # It was the method for set_view, but add seems more appropriate
    #def set_view(self, view: View):
    def add_view(self, view: View):
        name  = view.name

        if name in self.views:
            logging.info("Replacing existing view {name}")

        self.views[name] = view

    def set_input(self, input: Input):
        name = input.name

        if name in self.inputs:
            logging.info("Replacing existing input {input}")

        self.inputs[name] = input

    def _get_name_dir(self, to_lower: bool = True) -> str:
        return Trelliscope.__sanitize(self.name, to_lower)

    def get_output_path(self) -> str:
        return os.path.join(self.path, self._get_name_dir())

    def get_displays_path(self) -> str:
        output_path = self.get_output_path()
        return os.path.join(output_path, Trelliscope.DISPLAYS_DIR)
    
    def get_dataset_display_path(self) -> str:
        return os.path.join(self.get_displays_path(), self._get_name_dir(False))
    
    @staticmethod
    def __sanitize(text:str, to_lower=True) -> str:
        if to_lower:
            text = text.lower()
        
        text = text.replace(" ", "_")
        text = re.sub(r"[^\w]", "", text)

        return text
    
    def to_dict(self) -> dict:
        result = {}

        result["name"] = self.name
        result["description"] = self.description
        result["tags"] = self.tags
        result["key_cols"] = self.key_cols
        result["metas"] = [meta.to_dict() for meta in self.metas.values()]
        result["state"] = self.state.to_dict()
        result["views"] = [view.to_dict() for view in self.views.values()]
        result["inputs"] = [input.to_dict() for input in self.inputs.values()]
        result["panel_type"] = self.panel_type

        return result

    def to_json(self, pretty: bool = True) -> str:
        indent_value = None

        if pretty:
            indent_value = 2

        dict_to_serialize = self.to_dict()
        return json.dumps(self.to_dict(), indent=indent_value)
    
    def __repr__(self) -> str:
        output = []
        output.append("A trelliscope display")
        output.append(f"* Name: {self.name}")
        output.append(f"* Description: {self.description}")

        if len(self.tags) == 0:
            output.append(f"* Tags: None")
        else:
            output.append(f"* Tags: {self.tags}")

        output.append(f"* Key columns: {self.key_cols}")
        output.append(f"---")
        output.append(f"* Path: {self.path}")
        output.append(f"* Number of panels: {len(self.data_frame)}")
        
        written_str = "yes" if self.panels_written else "no"
        output.append(f"* Panels written: {written_str}")
        output.append(f"---")
        output.append(f"* Meta Info:")

        meta_info = self._get_meta_info_for_output()
        output.extend(meta_info)

        result = "\n".join(output)
        return result

    def _get_meta_info_for_output(self):
        """
        Returns a list of all the meta info that could be used for
        ToString type purposes.
        """
        output = []

        # TODO: Fill this in to iterate through the columns and metas
        # to display their information

        return output

    def write_display(self, force_write: bool = False, jsonp: bool = True):
        """
        Write the contents of this display.
        Params:
            force_write: bool - Should the panels be forced to be written even
                if they have already been written?
            jsonp: bool - If true, app files are written as "jsonp" format, otherwise
                "json" format. The "jsonp" format makes it possible to browse a
                trelliscope app without the need for a web server.
        """
        

        # TODO: Do we want to use the temp file context manager so our files are cleaned up after?
        # Or is the point to leave it around for a while?
        # https://docs.python.org/3/library/tempfile.html
        # if self._path is None:
        #     self.path = tempfile.TemporaryDirectory()
        # the context object is used like this:
        # with tempfile.TemporaryDirectory() as tmpdirname:

        output_dir = self.get_output_path()
        logging.info(f"Saving to {output_dir}")

        # TODO: Verify that we want to remove this rather than
        # just overwriting / appending...

        # Remove the targeted output dir if it already exists
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        # Create the output dir and the displays dir beneath it
        os.makedirs(output_dir)
        os.makedirs(self.get_displays_path())
        os.makedirs(self.get_dataset_display_path())

        config = self._check_app_config(output_dir, jsonp)

        config_using_jsonp = False
        if "data_type" in config.keys() and config["data_type"] == "jsonp":
            config_using_jsonp = True

        if config_using_jsonp != jsonp:
            jsonp = config_using_jsonp
            logging.info(f"Using jsonp={jsonp}")

        tr = self.__copy()

        # TODO: Determine how to check if the panel column is writable.
        # In R they check to make sure it doesn't inherit from img_panel or iframe_panel
        writable = True

        if ((not tr.panels_written) or force_write) and writable:
            tr = tr.write_panels()

        tr = tr.infer()
        
        tr._check_panels()

        tr._write_display_info(jsonp, config["id"])
        tr._write_meta_data(jsonp, config["id"])

        # TODO: Should this look in the path or the output path (ie. with the current name on it)
        # In R it was just the path, but from my example run, it seemed to have the dataset
        # name (ie. the output path)
        tr._update_display_list(self.get_output_path(), jsonp, config["id"])

        return tr

    def _check_panels(self):
        tr = self.__copy()

        return tr

    def _check_app_config(self, app_dir, jsonp) -> dict():
        """
        Gets the app config. If a config file exists in the `app_dir`
        it will be used. Otherwise, a new config will be created and
        the config information returned.
        Params:
            app_dir: str - The displays directory
            jsonp: bool - Should jsonp be used instead of json?
        """
        config_dict = {}

        prefix = Trelliscope.CONFIG_FILE_NAME
        jsonp_config_file = os.path.join(app_dir, f"{prefix}.jsonp")
        json_config_file = os.path.join(app_dir, f"{prefix}.json")

        # Look to see if there is an existing config file, and use it

        if os.path.exists(jsonp_config_file):
            config_dict = Trelliscope.__read_jsonp(jsonp_config_file)
        elif os.path.exists(json_config_file):
            config_dict = Trelliscope.__read_jsonp(json_config_file)
        else:
            # No config file found, generating new info
            config_dict["name"] = "Trelliscope App"
            config_dict["data_type"] = "jsonp" if jsonp else "json"
            # TODO: Verify that this is the correct id here
            # We might just want to get a random hash based on the current time
            config_dict["id"] = self.id

            # Write out a new config file
            function_name = f"__loadAppConfig__{config_dict['id']}"
            content = json.dumps(config_dict, indent=2)
            config_file = jsonp_config_file if jsonp else json_config_file
            Trelliscope.__write_json_file(config_file, jsonp, function_name, content)

        return config_dict

    @staticmethod
    def __get_jsonp_wrap_text_dict(jsonp: bool, function_name: str) -> dict():
        """
        Gets the starting and ending text to use for the config file.
        If it is jsonp, it will have a function name and ()'s. If it is
        not (ie, regular json), it will have empty strings.
        """
        text_dict = {}
        if jsonp:
            text_dict["start"] = f"{function_name}("
            text_dict["end"] = ")"
        else:
            text_dict["start"] = ""
            text_dict["end"] = ""

        return text_dict

    @staticmethod
    def __write_json_file(file_path: str, jsonp: bool, function_name: str, content: str):
        wrap_text_dict = Trelliscope.__get_jsonp_wrap_text_dict(jsonp, function_name)
        wrapped_content = wrap_text_dict["start"] + content + wrap_text_dict["end"]

        with open(file_path, "w") as output_file:
            output_file.write(wrapped_content)

    @staticmethod
    def __get_file_path(directory: str, filename_no_ext: str, jsonp: bool):
        file_ext = "jsonp" if jsonp else "json"
        filename = f"{filename_no_ext}.{file_ext}"

        file_path = os.path.join(directory, filename)

        return file_path

    @staticmethod
    def __read_jsonp(file: str) -> dict():
        """
        Reads the json content of the .json or .jsonp file. If the file is
        a .jsonp file, the function name and ()'s will be ignored.
        Params:
            file: str - The full path to the file.
        Returns:
            dict - The content of the .json or .jsonp file.
        """
        content = ""
        with open(file) as file_handle:
            content = file_handle.read()

        json_content = ""

        if file.endswith(".json"):
            json_content = content
        elif file.endswith(".jsonp"):
            open_paren_index = content.index("(")
            close_paren_index = content.rindex(")")
            json_content = content[open_paren_index + 1 : close_paren_index]
        else:
            raise ValueError(f"Unrecognized file extension for file {file}. Expected .json or .jsonp")

        result = json.loads(json_content)
        return result

    def infer(self):
        tr = self._infer_metas()

        tr.state = tr._infer_state(tr.state)

        for view in tr.views:
            view2:View = view._copy()
            state = view2.state

            view2.state = self._infer_state(state, view2.name)
            tr.add_view(view2)
            
        tr = tr._infer_panel_type()

        return tr

    def _infer_metas(self):
        tr = self.__copy()

        # get column names from the data frame
        column_names = tr.data_frame.columns

        # compare to metas that are already defined
        existing_meta_names = tr.metas.keys()

        # go through each column name that does not have a corresponding meta
        metas_to_infer = set(column_names) - set(existing_meta_names)

        logging.debug(f"Inferring Metas: {metas_to_infer}")

        metas_to_remove = []
        metas_inferred = []

        for meta_name in metas_to_infer:
            meta = tr._infer_meta_variable(tr.data_frame[meta_name], meta_name)

            if meta is None:
                # Could not infer this meta, add to remove list
                metas_to_remove.append(meta_name)
            else:
                metas_inferred.append(meta_name)

                # Add this inferred meta to the trelliscope
                tr.add_meta(meta_name, meta)

        # Add to the ignore list any that we could not infer
        tr.columns_to_ignore.extend(metas_to_remove)

        logging.debug(f"Successfully inferred metas: {metas_inferred}")

        tr = tr._finalize_meta_labels()

        return tr

    def _infer_meta_variable(self, meta_column: pd.Series, meta_name: str):
        meta = None

        # TODO: Add Date and DateTime to this list

        if meta_column.dtype == "category":
            meta = FactorMeta(meta_name)
        elif is_numeric_dtype(meta_column.dtype):
            meta = NumberMeta(meta_name)
        elif is_string_dtype(meta_column.dtype):
            # this is a string column

            # Check if all the entries start with http            
            if meta_column.apply(lambda x: x.startswith("http")).all():
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

        for meta in self.metas.values():
            if meta.label is None:
                meta.label = meta.varname

        return tr

    def _infer_state(self, state, view:str = None) -> DisplayState:
        view_str = ""

        if view is not None:
            view_str = f" for view '{view}'"

        state2:DisplayState = state._copy()

        layout = state2.layout

        if layout is None:
            logging.info(f"No layout definition supplied{view_str}. Using Default.")
            state2.layout = LayoutState(nrow=2, ncol=3)
        
        labels = state2.labels

        if labels is None:
            logging.info(f"No labels definition supplied{view_str}. Using Default.")
            state2.labels = LabelState(self.key_cols)

        return state2
                
    def _infer_panel_type(self):
        tr = self.__copy()

        # TODO: Implement this
    
        return tr


    def _write_display_info(self, jsonp, id):
        file = Trelliscope.__get_file_path(self.get_dataset_display_path(),
                                            Trelliscope.DISPLAY_INFO_FILE_NAME,
                                            jsonp)
    
        content = self.to_json(True)
        function_name = f"__loadDisplayInfo__{id}"

        Trelliscope.__write_json_file(file, jsonp, function_name, content)

    def _update_display_list(self, app_path:str, jsonp:bool, id:str):
        """
        Update the list of all displays in an app directory.
        Params:
            app_path: str - The path where all of the displays are stored
            jsonp: bool - If true, files are read and written as "jsonp" format,
                otherwise "json" format. The "jsonp" format makes it possible to browse a
                trelliscope app without the need for a web server.
            id: str - The id of the display. Can be found in `config.json[p]`.
        """
        displays_dir = os.path.join(app_path, Trelliscope.DISPLAYS_DIR)
        
        if not os.path.exists(displays_dir):
            raise ValueError(f"The directory {app_path} does not contain any displays.")
        
        ext = "jsonp" if jsonp else "json"
        filename = f"{Trelliscope.DISPLAY_INFO_FILE_NAME}.{ext}"

        pattern = os.path.join(app_path, Trelliscope.DISPLAYS_DIR, "*", filename)
        # print("Pattern: " + pattern)
        files = glob.glob(pattern)

        display_info_list = []

        for file in files:
            from_file = Trelliscope.__read_jsonp(file)
            keys_to_keep = ["name", "description", "tags"]
            display_info = {key: from_file[key] for key in keys_to_keep}
            display_info_list.append(display_info)

        display_list_file = Trelliscope.__get_file_path(self.get_displays_path(),
                                                        Trelliscope.DISPLAY_LIST_FILE_NAME,
                                                        jsonp)
        function_name = f"__loadDisplayList__{id}"
        content = json.dumps(display_info_list, indent=2)
        Trelliscope.__write_json_file(display_list_file, jsonp, function_name, content)

    def _get_metas_list(self) -> list:
        meta_list = [meta.to_dict() for meta in self.metas.values()]
        return meta_list

    def _write_meta_data(self, jsonp:bool, id:str):
        meta_data_file = Trelliscope.__get_file_path(self.get_dataset_display_path(),
                                           Trelliscope.METADATA_FILE_NAME,
                                           jsonp)
                
        if self.debug:
            # Pretty print the json if in debug mode
            meta_data_json = self.data_frame.to_json(orient="records", indent=2)
        else:
            meta_data_json = self.data_frame.to_json(orient="records")

        # Turn the escaped \/ into just /
        meta_data_json = meta_data_json.replace("\\/", "/")

        function_name = f"__loadMetaData__{id}"
        Trelliscope.__write_json_file(meta_data_file, jsonp, function_name, meta_data_json)

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

    # def add_view(self):
    #     return self.__copy()

    def add_inputs(self):
        return self.__copy()

    def __copy(self):
        # TODO: Should this do a deep copy? Should it make copies of metas?
        return copy.deepcopy(self)
