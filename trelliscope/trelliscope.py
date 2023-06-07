# TODO: Decide how to handle type hints for return type of Trelliscope
# This enables type hints for the return type to be Trelliscope
# from __future__ import annotations
# This is now the proper way to do type hints for the return type of the
# enclosing class, but it requires Python 3.11
# from typing import Self


import tempfile
import copy
import os
import uuid
import json
import shutil
import re
import glob
import pandas as pd
from pandas.api.types import is_numeric_dtype
import webbrowser

import logging
logging.basicConfig(level=logging.DEBUG)

from .metas import Meta, StringMeta, NumberMeta, HrefMeta, FactorMeta
from .state import DisplayState, LayoutState, LabelState
from .view import View
from .input import Input
from .panels import Panel, ImagePanel, IFramePanel, FigurePanel
from .panel_source import PanelSource, FilePanelSource
from . import utils
from . import html_utils

class Trelliscope:
    """
    Main interface for creating and writing Trelliscopes.
    """

    DISPLAYS_DIR = "displays"
    CONFIG_FILE_NAME = "config"
    PANELS_DIR = "panels"
    DISPLAY_LIST_FILE_NAME = "displayList"
    DISPLAY_INFO_FILE_NAME = "displayInfo"
    METADATA_FILE_NAME = "metaData"
    PANEL_OUTPUT_DIR = "panels"
    PANEL_OUTPUT_FILENAME = "facet_plot"

    def __init__(self, dataFrame: pd.DataFrame, name: str, description: str = None, key_cols = None, tags = None,
            path: str = None, force_plot: bool = False, panel_col: str = None, panel: Panel = None, pretty_meta_data: bool = False,
            keysig:str = None, server:str = None):
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
        self.pretty_meta_data = pretty_meta_data
        self.keysig: str = keysig
        self.server: str = server
        self.thumbnail_url: str = None
        self.panel_source: PanelSource = FilePanelSource()
        
        self.facet_cols: list = None

        self.panel: Panel = panel

        if panel is not None and panel_col is not None:
            # They have supplied both a panel and a panel column name
            # They really should have only given one or the other
            # Let's see if they match (and then we can ignore the panel
            # column), of if they don't (in which case we have two panels
            # to work with)

            # TODO: Fill this in
            pass
        elif panel_col is not None:
            # This is the case where they have specified a panel column
            # but not an actual panel, so we can create the panel for them
            self.panel = Panel.create_panel(self.data_frame, panel_col)
        else: # panel column is None
            # TODO: Decide if we should infer right here. This is how it
            # is done in the R as_trelliscope function

            # For now, leave this empty so it can be defined explicitly or
            # inferred later
            pass
            
        # SB 3/25/23: This should not be needed anymore with the new panel approach
        # self.panel_col = panel_col
        #self.panel_col = Trelliscope.__check_and_get_panel_col(dataFrame)

        #TODO: Is there a reason this is not a true uuid?
        self.id = uuid.uuid4().hex[:8]

        if self.description is None:
            self.description = self.name

        if self.tags is None:
            self.tags = []

        if self.key_cols is None:
            self.key_cols = self._get_key_cols()

        self.metas = {}
        self.columns_to_ignore = []
        self.state = DisplayState()
        
        self.views = {}
        self.inputs = {}

        self.panel_type = None
        self.panels_written = False
        self.panel_aspect = None
        self.panel_format = None

    def set_panel(self, panel: Panel):
        """
        Sets the panel.
        Params:
            panel: Panel - The new panel.
        """
        # TODO: Should we make a copy here??
        if not isinstance(panel, Panel):
            raise ValueError("Error: Panel must be a valid Panel class instance.")
        
        self.panel = panel

        return self

    def set_meta(self, meta: Meta):
        """
        Adds the provided meta to the stored dictionary with a key of the meta's
        `varname`. If this key was already present it will be replaced.
        Params:
            meta: Meta - The Meta object to add.
        """
        if not isinstance(meta, Meta):
            raise ValueError("Error: Meta definition must be a valid Meta class instance.")
        
        meta.check_with_data(self.data_frame)
        name = meta.varname

        if name in self.metas:
            logging.info(f"Replacing existing meta variable {name}")

        self.metas[name] = meta

        return self

    def set_metas(self, meta_list: list):
        """
        Helper method to add a list of metas at once.
        Params:
            meta_list: list(Meta) - The list of meta objects to add.
        """
        for meta in meta_list:
            self.set_meta(meta)

        return self

    def add_meta(self, meta_name: str, meta: Meta):
        """
        Adds the provided meta to the dictionary of stored metas. It will be
        added with a key of `meta_name`, replacing a meta of that key if it 
        already existed.
        Params:
            meta_name: str - The key for the meta (typically the varname).
            meta: Meta - The new meta to add.
        """
        # TODO: This seems redundant with set_meta. Do we need both?
        # TODO: Should we make a copy here??
        self.metas[meta_name] = meta

        return self

    def set_state(self, state: DisplayState):
        """
        Sets the state to the provided one.
        Params:
            state: DisplayState - The new state to add.
        """
        self.state = state

        return self

    # TODO: Verify this is acceptable as "add_view",
    # It was the method for set_view, but add seems more appropriate
    #def set_view(self, view: View):
    def add_view(self, view: View):
        """
        Adds the provided view to the stored dictionary. The key will be the view's name,
        and it will replace a view of that name if it already existed.
        Params:
            view: View - The view to add.
        """
        name  = view.name

        if name in self.views:
            logging.info("Replacing existing view {name}")

        self.views[name] = view

        return self

    def set_input(self, input: Input):
        """
        Adds the provided input to the stored dictionary. The key will be the input's name,
        and it will replace an input of that name if it already existed.
        Params:
            input: Input - The input to add.
        """
        # TODO: Should this be `add_input` instead?
        name = input.name

        if name in self.inputs:
            logging.info("Replacing existing input {input}")

        self.inputs[name] = input

        return self

    def _get_name_dir(self, to_lower: bool = True) -> str:
        """
        Returns the dataset name in directory form (sanitized).
        """
        return utils.sanitize(self.name, to_lower)

    def get_output_path(self) -> str:
        """
        Returns the output path where the Trelliscope is saved.
        """
        return os.path.join(self.path, self._get_name_dir())

    def get_displays_path(self) -> str:
        """
        Returns the path of the `displays` directory, which is a child
        of the main output path.
        """
        output_path = self.get_output_path()
        return os.path.join(output_path, Trelliscope.DISPLAYS_DIR)
    
    def get_dataset_display_path(self) -> str:
        """
        Returns the path of the display directory for this particular dataset, which
        is a child of the main `displays` directory.
        """
        return os.path.join(self.get_displays_path(), self._get_name_dir(False))
    
    def get_panel_output_path(self) -> str:
        """
        Returns the directory where the panels will be saved, which is a child
        of the display path for this particular dataset.
        """
        displays_path = self.get_displays_path()
        return os.path.join(displays_path, Trelliscope.PANEL_OUTPUT_DIR)
        
    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of this Trelliscope object.
        """
        result = {}

        result["name"] = self.name
        result["description"] = self.description
        result["tags"] = self.tags
        result["key_cols"] = self.key_cols
        result["keysig"] = self.keysig
        result["metas"] = [meta.to_dict() for meta in self.metas.values()]
        result["state"] = self.state.to_dict()
        result["views"] = [view.to_dict() for view in self.views.values()]

        if self.inputs.values is None or len(self.inputs.values()) == 0:
            result["inputs"] = None
        else:
            result["inputs"] = [input.to_dict() for input in self.inputs.values()]
        result["paneltype"] = self.panel_type
        result["panelformat"] = self.panel_format

        if self.panel is None:
            result["panelaspect"] = None
        else:
            result["panelaspect"] = self.panel.aspect_ratio
        
        # TODO: This needs to come from the right place
        result["panelsource"] = self.panel_source.to_dict()
        result["thumbnailurl"] = self.thumbnail_url

        return result

    def to_json(self, pretty: bool = True) -> str:
        """
        Returns a json string of the information stored in this object.
        Params:
            pretty: bool - Should the json be pretty printed / indented?
        """
        indent_value = None

        if pretty:
            indent_value = 2

        dict_to_serialize = self.to_dict()
        return json.dumps(self.to_dict(), indent=indent_value)
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the Trelliscope object.
        """
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
    
    def _create_output_dirs(self):
        """
        Creates the output directories needed for this Trelliscope. If an output
        path has not been specified, it will create them in a temporary directory.
        """

        # TODO: Do we want to use the temp file context manager so our files are cleaned up after?
        # Or is the point to leave it around for a while?
        # The mkdtemp means that it will stick around and we have to clean it up
        # tempfile.mkdtemp()
        # The TemporaryDirectory() approach uses a context object and cleans it up for us
        # https://docs.python.org/3/library/tempfile.html
        # if self._path is None:
        #     self.path = tempfile.TemporaryDirectory()
        # the context object is used like this:
        # with tempfile.TemporaryDirectory() as tmpdirname:

        if self.path is None:
            self.path = tempfile.mkdtemp()

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
        tr = self.__copy()

        tr._create_output_dirs()

        config = tr._check_app_config(tr.get_output_path(), jsonp)

        config_using_jsonp = False
        if "datatype" in config.keys() and config["datatype"] == "jsonp":
            config_using_jsonp = True

        if config_using_jsonp != jsonp:
            jsonp = config_using_jsonp
            logging.info(f"Using jsonp={jsonp}")


        # Infer panels if needed
        panels = tr.__check_and_get_panel_col()
        
        if len(panels) == 0:
            # No panels were found. Try to infer them.
            tr = tr._infer_panels()
            tr = tr._infer_panel_type()

        # TODO: Determine how to check if the panel column is writable.
        # In R they check to make sure it doesn't inherit from img_panel or iframe_panel
        is_writeable = tr.panel.is_writeable

        if ((not tr.panels_written) or force_write) and is_writeable:
            tr = tr.write_panels()

        tr = tr.infer()

        tr = tr._check_panels()
        tr = tr._infer_thumbnail_url()

        tr._write_display_info(jsonp, config["id"])
        tr._write_meta_data(jsonp, config["id"])

        # TODO: Should this look in the path or the output path (ie. with the current name on it)
        # In R it was just the path, but from my example run, it seemed to have the dataset
        # name (ie. the output path)
        tr._update_display_list(tr.get_output_path(), jsonp, config["id"])

        tr._write_javascript_lib()
        tr._write_widget()

        logging.info(f"Trelliscope written to `{tr.get_output_path()}`")

        return tr

    def _check_panels(self):
        """
        Checks the files in the panels directory, then compares them against the
        key columns in the dataframe. If there are key columns that do not have
        corresponding files, it will throw an error specifying the extra key columns
        that were discovered.
        
        Throws:
            ValueError
        """
        tr = self.__copy()

        panel_path = os.path.join(tr.get_displays_path(), "panels")

        # TODO: Fill this in

        return tr
    
    def _infer_thumbnail_url(self):
        """
        Sets the self.thumbnail_url variable to the appropriate thumbnail url.
        """
        # SB: In R this was called `get_thumbnail_url()` but it's not a getter

        # Is it necessary to make a copy in this case? In R it was not
        # tr = self.__copy()

        format = None
        # TODO: add check of panel format here.
        # format = tr.panel_format

        if self.panel is None:
            raise ValueError("A panel must be defined to be able to get the thumbnail url")
        
        # TODO: Clean this up using polymorphism and better checks...
        if isinstance(self.panel, ImagePanel):
            key = self.data_frame[self.panel.varname][0]

            thumbnail_url = ""
            if format is not None:
                name = self._get_name_dir()
                filename = f"{key}.{format}"
                thumbnail_url = os.path.join(Trelliscope.DISPLAYS_DIR, name, Trelliscope.PANELS_DIR, filename)
            else:
                thumbnail_url = key

            self.thumbnail_url = thumbnail_url
        else:
            self.thumbnail_url = None

        return self
    
    def _get_key_cols(self):
        """
        Infers the columns that uniquely identify a row.

        Checks for key columns in this order:
        1. self.facet_cols
        2. self.key_cols
        3. grouped columns on self.data_frame
        4. all columns
        
        This method does not SET the attribute, but rather just returns the columns.
        """

        key_cols = None

        if self.facet_cols is not None:
            key_cols = self.facet_cols
        elif self.key_cols is not None:
            key_cols = self.key_cols
        elif utils.is_dataframe_grouped(self.data_frame):
            key_cols = utils.get_dataframe_grouped_columns(self.data_frame)

            # ungroup the columns now, so they can be used as metas, etc.
            self.data_frame = self.data_frame.reset_index()
        else:
            key_cols = utils.get_uniquely_identifying_cols(self.data_frame)

            if len(key_cols) == 0:
                raise ValueError("Could not find columns of the data that uniquely define each row.")

        if self.facet_cols is None:
            logging.info(f"Using {key_cols} to uniquely identify each row of the data.")

        return key_cols

    def _get_existing_config_filename(self) -> str:
        """
        Gets the filename of the config file (.json or .jsonp) found on the filesystem.
        If no config file is found, it returns `None`
        """
        output_dir = self.get_output_path()

        prefix = Trelliscope.CONFIG_FILE_NAME
        jsonp_config_file = os.path.join(output_dir, f"{prefix}.jsonp")
        json_config_file = os.path.join(output_dir, f"{prefix}.json")

        # Look to see if there is an existing config file, and use it
        filename = None

        if os.path.exists(jsonp_config_file):
            filename = jsonp_config_file
        elif os.path.exists(json_config_file):
            filename = json_config_file

        return filename

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
            config_dict = utils.read_jsonp(jsonp_config_file)
        elif os.path.exists(json_config_file):
            config_dict = utils.read_jsonp(json_config_file)
        else:
            # No config file found, generating new info
            config_dict["name"] = "Trelliscope App"
            config_dict["datatype"] = "jsonp" if jsonp else "json"
            # TODO: Verify that this is the correct id here
            # We might just want to get a random hash based on the current time
            config_dict["id"] = self.id

            # Write out a new config file
            function_name = f"__loadAppConfig__{config_dict['id']}"
            content = json.dumps(config_dict, indent=2)
            config_file = jsonp_config_file if jsonp else json_config_file
            utils.write_json_file(config_file, jsonp, function_name, content)

        return config_dict

    def infer(self):
        """
        Infers:
            - Metas
            - State
            - Views
        """
        tr = self.__copy()

        tr = tr._infer_metas()

        tr.state = tr._infer_state(tr.state)

        for view in tr.views:
            view2:View = view._copy()
            state = view2.state

            view2.state = self._infer_state(state, view2.name)
            tr.add_view(view2)
        
        return tr

    def _infer_metas(self):
        tr = self.__copy()

        # get column names from the data frame
        column_names = tr.data_frame.columns

        # compare to metas that are already defined
        existing_meta_names = tr.metas.keys()

        # go through each column name that does not have a corresponding meta
        metas_to_infer = set(column_names) - set(existing_meta_names)

        # SB: Should we exclude any panel columns here? It seems like we should...

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
        elif utils.is_string_column(meta_column):
            # Check if all the entries start with http
            if utils.is_all_remote(meta_column):
                # This appears to be an href column
                meta = HrefMeta(meta_name)
            else:
                # This appears to be a regular string column
                meta = StringMeta(meta_name)
        # else:
        #     # This is not a column we can work with. For example, it could be a figure
        #     # do NOT add it to the list
        #     pass


        return meta
        
    def _finalize_meta_labels(self):
        """
        Fill in the labels for any metas that do not have a label. It will
        use the varname by default.
        """
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
        """
        Find the Panel column, then use that to set the
        .panel_type attribute, and also rename the column
        to be __PANEL_KEY__ as appropriate.
        """

        # TODO: Refer back to the panels approach. In the PanelSeries
        # approach, the as_trelliscope method first checks for any
        # columns that implement PanelSeries, and if they don't exist
        # one is inferred if possible.
        # Then, after creating a Trelliscope Display object, a separate
        # call to inferPanelType is made to essentially find the
        # PanelSeries columns that have been created.

        # tr = self.__copy()

        if self.panel is None:
            raise ValueError("A panel must be in place.")
        
        # TODO: In R, there are lots of checks here,
        # for _server_, nested_panels, image_panel, and iframe_panel
        # Perhaps a polymorphic approach could be used instead?
        if isinstance(self.panel, ImagePanel):
            self.panel_type = "img"
            self.panel_aspect = self.panel.aspect_ratio
            self.panels_written = False
            self.data_frame = self.data_frame.rename(columns={self.panel.varname: "__PANEL_KEY__"})
            
            # In R, they set the panel attribute directly, but currently
            # panel is a panel object
            #tr.panel = "__PANEL_KEY__"
            self.panel.varname = "__PANEL_KEY__"
        elif isinstance(self.panel, FigurePanel):
            self.panel_type = "img"
            self.panel_aspect = self.panel.aspect_ratio
            # TODO: check what we should put here...
            # tr.panels_written = False
            # tr.data_frame = tr.data_frame.rename(columns={tr.panel.varname: "__PANEL_KEY__"})

        return self
        # return tr

    def _infer_panels(self):
        # tr = self.__copy()
        # In R, this logic is found in the as_trelliscope function
        
        panel_cols = self.__check_and_get_panel_col()

        if len(panel_cols) == 0:
            # No panels were found
            # Check for a `Figure` col
            figure_columns = utils.find_figure_columns(self.data_frame)
            
            if len(figure_columns) > 1:
                # TODO: Decide how to handle this case... Use the first? Make the user specify?
                logging.warning(f"Warning, found multiple image columns `{image_columns}`, so none were used as a panel.")

            if len(figure_columns) == 1:
                # Found exactly one figure column
                panel_col = figure_columns[0]
                self.panel = FigurePanel(panel_col)
            else:
                # Did not find a single Figure panel, check for image panel

                # Check for an image col
                image_columns = utils.find_image_columns(self.data_frame)
                
                if len(image_columns) > 1:
                    # TODO: Decide how to handle this case... Use the first? Make the user specify?
                    logging.warning(f"Warning, found multiple image columns `{image_columns}`, so none were used as a panel.")
                elif len(image_columns) == 1:
                    # Found exactly one image column
                    panel_col = image_columns[0]

                    panel_col_series = self.data_frame[panel_col]
                    is_remote = utils.is_all_remote(panel_col_series)
                    
                    # The logic in this function is about being remote
                    # but the image column is defined in terms of being
                    # local, which is the opposite
                    is_local = not is_remote

                    # In R, this creates a new ImagePanelSeries and overwrites
                    # the Series in the dataframe with the new derived type.
                    # We may come back and try that here, but for now, we will
                    # create an ImagePanel that refers back to the varname in
                    # the table instead.
                    # tr[panel_col] = ImagePanelSeries(panel_col_series, is_local=is_local)
                    self.panel = ImagePanel(panel_col, is_local=is_local)
                    logging.info(f"Using {panel_col} col as an image panel.")

        return self
        # return tr

    def __check_and_get_panel_col(self):
        """
        Look for panels that have previously been defined.

        Returns:
            A list of the col names that are defined as panels.
            If none are found, an empty list is returned.
        """
        panels = []

        # TODO: If we use the PanelSeries approach, look for
        # all columns that inherit from PanelSeries.

        # Not using the PanelSeries approach, we can simply check
        # if the panel attribute is empty
        if self.panel is not None:
            panels.append(self.panel.varname)

        return panels
        
    def _write_display_info(self, jsonp : bool, id : str):
        """
        Creates the displayInfo json file.
        """
        file = utils.get_file_path(self.get_dataset_display_path(),
                                            Trelliscope.DISPLAY_INFO_FILE_NAME,
                                            jsonp)
    
        content = self.to_json(True)
        function_name = f"__loadDisplayInfo__{id}"

        utils.write_json_file(file, jsonp, function_name, content)

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
        files = glob.glob(pattern)

        display_info_list = []

        for file in files:
            from_file = utils.read_jsonp(file)
            keys_to_keep = ["name", "description", "tags", "keysig", "thumbnailurl"]
            display_info = {key: from_file[key] for key in keys_to_keep}
            display_info_list.append(display_info)

        display_list_file = utils.get_file_path(self.get_displays_path(),
                                                        Trelliscope.DISPLAY_LIST_FILE_NAME,
                                                        jsonp)
        function_name = f"__loadDisplayList__{id}"
        content = json.dumps(display_info_list, indent=2)
        utils.write_json_file(display_list_file, jsonp, function_name, content)

    def _get_metas_list(self) -> list:
        meta_list = [meta.to_dict() for meta in self.metas.values()]
        return meta_list

    def _write_meta_data(self, jsonp:bool, id:str):
        meta_data_file = utils.get_file_path(self.get_dataset_display_path(),
                                           Trelliscope.METADATA_FILE_NAME,
                                           jsonp)
                
        # TODO: Verify that we only want the meta columns here
        meta_columns = [meta for meta in self.metas]
        meta_df = self.data_frame[meta_columns]

        if self.pretty_meta_data:
            # Pretty print the json if in debug mode
            meta_data_json = meta_df.to_json(orient="records", indent=2)
        else:
            meta_data_json = meta_df.to_json(orient="records")

        # Turn the escaped \/ into just /
        meta_data_json = meta_data_json.replace("\\/", "/")

        function_name = f"__loadMetaData__{id}"
        utils.write_json_file(meta_data_file, jsonp, function_name, meta_data_json)

    def _write_javascript_lib(self):
        """
        Writes the JavaScript libraries to the output directory
        """
        output_path = self.get_output_path()
        html_utils.write_javascript_lib(output_path)

    def _write_widget(self):
        output_path = self.get_output_path()
        config_path =  self._get_existing_config_filename()
        config_file = os.path.basename(config_path)

        id = self.id
        is_spa = True

        html_utils.write_widget(output_path, id, config_file, is_spa)

    @staticmethod
    def __write_figure(row, fig_column:str, output_dir:str, extension:str, key_cols:list):
        fig = row[fig_column]

        filename_prefix = ""
        if len(key_cols) > 0:
            key_col_values = [str(row[key_col]) for key_col in key_cols]
            filename_prefix = "_".join(key_col_values)
        else:
            filename_prefix = row.name

        filename_prefix = utils.sanitize(filename_prefix)

        filename = os.path.join(output_dir, f"{filename_prefix}.{extension}")
        logging.debug(f"Saving image {filename}")
        fig.write_image(filename)

        return filename

    def write_panels(self):
        tr = self.__copy()

        #if not isinstance(self.panel, FigurePanel):
        if not tr.panel.is_writeable:
            raise ValueError("Error: Attempting to write a panel that is not writable")

        panel_keys = tr._get_panel_paths_from_keys
        panel_col = tr.panel.varname
        extension = tr.panel.get_extension()

        output_dir = tr.get_panel_output_path()

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        # TODO: check if the panel is an html widget, and if so, create it here (see R)
        
        # TODO: Follow the logic in the R version to match filenames, etc.
        tr.data_frame["__PANEL_KEY__"] = tr.data_frame.apply(lambda row: Trelliscope.__write_figure(row, panel_col, output_dir, extension, self.key_cols), axis=1)

        # TODO: Handle creating hash and key sig to avoid having to re-write panels
        # that have already been generated here.
        # One of the things that needs to happen here is to set the keysig to a hash of the columns

        tr.panels_written = True

        return tr

    def _get_panel_paths_from_keys(self):
        path = "_".join(self.key_cols)
        path = utils.sanitize(path)

        # TODO: Make sure the sanitized key columns still uniquely identify the row
        # TODO: Do we need to sanitize (and change) the actual panel columns here?

        return path

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

    def view_trelliscope(self):
        # TODO: Verify that a trelliscope has been written first

        index_file = os.path.join(self.get_output_path(), "index.html") 
        full_path = "file://" + os.path.realpath(index_file)
        NEW_TAB = 2
        webbrowser.open(full_path, NEW_TAB)
        
        return self

    def __copy(self):
        # TODO: Should this do a deep copy? Should it make copies of metas?
        return copy.deepcopy(self)
