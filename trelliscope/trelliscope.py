import copy
import glob
import json
import logging
import os
import shutil
import tempfile
import uuid
import webbrowser

import pandas as pd

logging.basicConfig(level=logging.INFO)

from . import html_utils, utils
from .input import Input
from .metas import FactorMeta, HrefMeta, Meta, NumberMeta, PanelMeta, StringMeta
from .panels import FigurePanel, ImagePanel, Panel, PanelOptions
from .progress_bar import ProgressBar
from .state import (
    CategoryFilterState,
    DisplayState,
    FilterState,
    LabelState,
    LayoutState,
    SortState,
)
from .view import View


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

    def __init__(
        self,
        dataFrame: pd.DataFrame,
        name: str,
        description: str = None,
        key_cols=None,
        tags=None,
        path: str = None,
        force_plot: bool = False,
        primary_panel: str = None,
        pretty_meta_data: bool = False,
        keysig: str = None,
        server: str = None,
    ):
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

        self.data_frame: pd.DataFrame = dataFrame
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

        self.facet_cols: list = None

        self.panel_options = {}  # stores PanelOptions objects used to pre-specify panel data
        self.panels = {}  # stores the actual Panel objects

        self.primary_panel = primary_panel

        if self.primary_panel is None:
            # If there are panels defined already, this will select one to be the primary panel
            self._infer_primary_panel()

        # In R, the id is only 8 digits, but it should not hurt to use a proper uuid
        # self.id = uuid.uuid4().hex[:8] # This would only use 8 digits as in the R version
        self.id = uuid.uuid4().hex[:8]  # This uses a proper uuid

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

    def _infer_primary_panel(self) -> None:
        """
        Infers the primary panel. If there is only one, it will be used.
        If more than one is found, the first one encountered will be used.

        Note: Because the panels are stored in a dictionary, there is no
        guarantee that the one chosen will be the first one created.

        If no panels are found, the `primary_panel` attribute will be left
        unchanged.

        Side Effects: sets the self.primary_panel variable.
        """
        panel_columns = self._get_panel_columns()

        if len(panel_columns) > 0:
            self.primary_panel = panel_columns[0]

    def _get_panel(self, panel_col: str) -> Panel:
        """
        Returns a `Panel` object corresponding to this panel column name.

        If no panel exists for this column a `ValueError` will be raised.
        """
        if panel_col not in self.panels:
            raise ValueError(f"There is no panel associated with column {panel_col}")

        return self.panels[panel_col]

    def _has_panel(self, panel_col: str) -> bool:
        """
        Returns true if a panel object exists with this name.
        """
        return panel_col in self.panels

    def add_panel(self, panel: Panel):
        """
        Adds the panel to the Trelliscope object.

        A new Trelliscope object is returned. The original one is not modified.
        """
        tr = self.__copy()

        if not isinstance(panel, Panel):
            raise ValueError("Panel must be of Panel class type (or a sub class)")

        tr.panels[panel.varname] = panel

        return tr

    def set_meta(self, meta: Meta):
        """
        Adds the provided meta to the stored dictionary with a key of the meta's
        `varname`. If this key was already present it will be replaced.
        Params:
            meta: Meta - The Meta object to add.

        Returns a copy of the Trelliscope object with the meta added. The original
        Trelliscope object is not modified.
        """
        tr = self.__copy()

        if not isinstance(meta, Meta):
            raise ValueError(
                "Error: Meta definition must be a valid Meta class instance."
            )

        meta.check_with_data(tr.data_frame)
        name = meta.varname

        if name in tr.metas:
            logging.info(f"Replacing existing meta variable {name}")

        tr.metas[name] = meta

        return tr

    def set_metas(self, meta_list: list):
        """
        Helper method to add a list of metas at once.
        Params:
            meta_list: list(Meta) - The list of meta objects to add.

        Returns a copy of the Trelliscope object with the metas added. The original
        Trelliscope object is not modified.
        """
        tr = self._copy()

        for meta in meta_list:
            tr = tr.set_meta(meta)

        return tr

    def set_state(self, state: DisplayState):
        """
        Sets the state to the provided one.
        Params:
            state: DisplayState - The new state to add.

        Returns a copy of the Trelliscope object with the state added. The original
        Trelliscope object is not modified.
        """
        tr = self.__copy()

        tr.state = state

        return tr

    def add_view(self, view: View):
        """
        Adds the provided view to the stored dictionary. The key will be the view's name,
        and it will replace a view of that name if it already existed.
        Params:
            view: View - The view to add.

        Returns a copy of the Trelliscope object with the view added. The original
        Trelliscope object is not modified.
        """
        tr = self.__copy()

        name = view.name

        if name in tr.views:
            logging.info("Replacing existing view {name}")

        tr.views[name] = view

        return tr

    def add_input(self, input: Input):
        """
        Adds the provided input to the stored dictionary. The key will be the input's name,
        and it will replace an input of that name if it already existed.
        Params:
            input: Input - The input to add.

        Returns a copy of the Trelliscope object. The original
        Trelliscope object is not modified.
        """
        tr = self.__copy()

        name = input.name

        if name in tr.inputs:
            logging.info("Replacing existing input {input}")

        tr.inputs[name] = input

        return tr

    def add_inputs(self, inputs: list):
        """
        Convenience method to add muliple inputs.

        Returns a copy of the Trelliscope object. The original is not modified.
        """
        tr = self.__copy()

        for input_obj in inputs:
            tr = tr.add_input(input_obj)

        return tr

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

    def _get_panel_output_path(self, panel_col: str, is_absolute: bool) -> str:
        """
        Returns the directory where the panels for this dataset are saved, which is
        a child of the display path for this particular dataset.

        Params:
            panel_col:str - The name of the panel column.
            is_absolute:bool - Should an absolute path be returned? If not, a relative
                path will be returned instead.
        """
        panel_dir = utils.sanitize(panel_col, to_lower=True)
        combined_path = os.path.join(Trelliscope.PANEL_OUTPUT_DIR, panel_dir)

        if is_absolute:
            combined_path = os.path.join(self.get_dataset_display_path(), combined_path)

        return combined_path

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

        result["thumbnailurl"] = self.thumbnail_url
        result["primarypanel"] = self.primary_panel

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

        return json.dumps(self.to_dict(), indent=indent_value)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Trelliscope object.
        """
        # TODO: See if there are additional items we want to add.

        output = []
        output.append("A trelliscope display")
        output.append(f"* Name: {self.name}")
        output.append(f"* Description: {self.description}")

        if len(self.tags) == 0:
            output.append("* Tags: None")
        else:
            output.append(f"* Tags: {self.tags}")

        output.append(f"* Key columns: {self.key_cols}")
        output.append("---")
        output.append(f"* Path: {self.path}")
        output.append(f"* Number of panels: {len(self.panels)}")

        # written_str = "yes" if self.panels_written else "no"
        # output.append(f"* Panels written: {written_str}")
        output.append("---")
        output.append("* Meta Info:")

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

        Side effects:
        * Directories created on the filesystem
        * self.path variable will be updated to the temp directory if it was None.
        """
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
        Write the contents of this display. In the process, all necessary
        Trelliscope parameters will be inferred if they are not present.

        Params:
            force_write: bool - Should the panels be forced to be written even
                if they have already been written?
            jsonp: bool - If true, app files are written as "jsonp" format, otherwise
                "json" format. The "jsonp" format makes it possible to browse a
                trelliscope app without the need for a web server.

        Returns a copy of the Trelliscope object. The original is not modified.
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
        tr = tr.infer_panels()
        panels = tr._get_panel_columns()

        if len(panels) == 0:
            raise ValueError("No panels were found or inferred.")

        # Look through each panel and write the images if needed
        for panel_col in panels:
            panel = tr._get_panel(panel_col)

            if (panel.is_writeable or panel.should_copy) and (
                not panel.panels_written or force_write
            ):
                tr = tr.write_or_copy_panels(panel_col)

        tr = tr.infer()

        tr = tr._check_panels()
        tr = tr._infer_thumbnail_url()

        tr._write_display_info(jsonp, config["id"])
        tr._write_meta_data(config["id"])

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

        Modifies the current Trelliscope object.
        """
        # Is it necessary to make a copy in this case? In R it was not
        # tr = self.__copy()

        format = None
        # TODO: add check of panel format here.
        # format = tr.panel_format

        if self.primary_panel is None:
            self._infer_primary_panel()

        primary_panel_col = self.primary_panel

        if primary_panel_col is None:
            raise ValueError(
                "A primary panel must be defined to be able to get the thumbnail url"
            )

        primary_panel = self._get_panel(primary_panel_col)

        # TODO: Clean this up using polymorphism and better checks...
        if isinstance(primary_panel, (FigurePanel, ImagePanel)):
            thumbnail_url = self.data_frame[primary_panel_col][0]

            # key = self.data_frame[self.panel.varname][0]

            # thumbnail_url = ""
            # if format is not None:
            #     name = self._get_name_dir()
            #     filename = f"{key}.{format}"
            #     thumbnail_url = os.path.join(Trelliscope.DISPLAYS_DIR, name, Trelliscope.PANELS_DIR, filename)
            # else:
            #     thumbnail_url = key

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
                raise ValueError(
                    "Could not find columns of the data that uniquely define each row."
                )

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

        Returns a copy of the Trelliscope object. The original is not modified.
        """
        tr = self.__copy()

        tr = tr._infer_metas()

        tr.state = tr._infer_state(tr.state)

        for view in tr.views:
            view2: View = view._copy()
            state = view2.state

            view2.state = self._infer_state(state, view2.name)
            tr = tr.add_view(view2)

        return tr

    def _infer_metas(self):
        """
        Infers metas from the data frame columns.

        Returns a copy of the Trelliscope object. The original is not modified.
        """

        tr = self.__copy()

        # get column names from the data frame
        column_names = tr.data_frame.columns

        # compare to metas that are already defined
        existing_meta_names = tr.metas.keys()

        # go through each column name that does not have a corresponding meta
        metas_to_infer = set(column_names) - set(existing_meta_names)

        # TODO: SB: Should we exclude any panel columns here? It seems like we should...

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
                tr = tr.set_meta(meta)

        # Add to the ignore list any that we could not infer
        tr.columns_to_ignore.extend(metas_to_remove)

        logging.debug(f"Successfully inferred metas: {metas_inferred}")

        tr = tr._finalize_meta_labels()

        return tr

    def _infer_meta_variable(self, meta_column: pd.Series, meta_name: str) -> Meta:
        """
        Infers an individual meta variable from the provided column. If an appropriate
        Meta is not found for this column `None` is returned.

        Params:
            meta_column: pd.Series - The Pandas column to infer from.
            meta_name: str - The name of the column.

        Returns:
            Meta object associated with this column.

        This does not add the meta to the Trelliscope object, but simply returns it.
        """
        meta = None

        # TODO: Add Date and DateTime to this list
        panel_cols = self._get_panel_columns()
        panel_figure_cols = self._get_panel_figure_columns()

        if meta_name in panel_cols:
            panel = self._get_panel(meta_name)
            meta = PanelMeta(panel)
        elif meta_name in panel_figure_cols:
            # These are the original figure columns held for backup.
            # They are not desired in the output, so they are skipped here.
            pass
        elif meta_column.dtype == "category":
            meta = FactorMeta(meta_name)
        elif utils.is_numeric_dtype(meta_column.dtype):
            meta = NumberMeta(meta_name)
        elif utils.is_string_column(meta_column):
            # Check if all the entries start with http
            if utils.is_all_remote(meta_column):
                # This appears to be an href column
                meta = HrefMeta(meta_name)
            else:
                # This appears to be a regular string column
                meta = StringMeta(meta_name)
        else:
            # This is not a column we can work with. For example, it could be a figure
            # do NOT add it to the list
            pass

        return meta

    def _finalize_meta_labels(self):
        """
        Fill in the labels for any metas that do not have a label. It will
        use the varname by default.

        Returns a copy of the Trelliscope object. The original is not modified.
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

    def _infer_state(self, state, view: str = None) -> DisplayState:
        """
        Infers and returns a new display state based on this state. Creates LayoutState,
        LabelState, and updates the filter map.

        A new DisplayState object is returned. The original is not modified.
        """
        view_str = ""

        if view is not None:
            view_str = f" for view '{view}'"

        state2: DisplayState = state._copy()

        layout = state2.layout

        if layout is None:
            logging.info(f"No layout definition supplied{view_str}. Using Default.")
            state2.layout = LayoutState(ncol=3)

        labels = state2.labels

        if labels is None:
            logging.info(f"No labels definition supplied{view_str}. Using Default.")
            state2.labels = LabelState(self.key_cols)

        # Add in metatype for sorts and filters
        filter_map = state2.filter

        for filter_name in filter_map.keys():
            filter_map[filter_name].metatype = self.metas[filter_name].type

        sort_map = state2.sort
        for sort_name in sort_map.keys():
            sort_map[sort_name].metatype = self.metas[sort_name].type

        # if there is a default filter that is a factor, we need to translate
        for filter_name in filter_map.keys():
            filter: FilterState = filter_map[filter_name]
            meta: Meta = self.metas[filter_name]

            if (
                isinstance(filter, CategoryFilterState) and isinstance(meta, FactorMeta)
                # and filter.filtertype == FilterState.FILTERTYPE_CATEGORY
                # and meta.type == Meta.TYPE_FACTOR
            ):
                if filter.values is not None and len(filter.values) > 0:
                    filter.values = list(set(meta.levels).intersection(filter.values))

        return state2

    # def _infer_panel_type(self):
    #     """
    #     Find the Panel column, then use that to set the
    #     .panel_type attribute.
    #     """

    #     # TODO: Refer back to the panels approach. In the PanelSeries
    #     # approach, the as_trelliscope method first checks for any
    #     # columns that implement PanelSeries, and if they don't exist
    #     # one is inferred if possible.
    #     # Then, after creating a Trelliscope Display object, a separate
    #     # call to inferPanelType is made to essentially find the
    #     # PanelSeries columns that have been created.

    #     # tr = self.__copy()

    #     if self.panel is None:
    #         raise ValueError("A panel must be in place.")

    #     # TODO: In R, there are lots of checks here,
    #     # for _server_, nested_panels, image_panel, and iframe_panel
    #     # Perhaps a polymorphic approach could be used instead?
    #     if isinstance(self.panel, ImagePanel):
    #         self.panel_type = "img"
    #         self.panel_aspect = self.panel.aspect_ratio
    #         self.panels_written = False
    #         # self.data_frame = self.data_frame.rename(columns={self.panel.varname: "__PANEL_KEY__"})

    #         # In R, they set the panel attribute directly, but currently
    #         # panel is a panel object
    #         #tr.panel = "__PANEL_KEY__"
    #         # self.panel.varname = "__PANEL_KEY__"
    #     elif isinstance(self.panel, FigurePanel):
    #         self.panel_type = "img"
    #         self.panel_aspect = self.panel.aspect_ratio
    #         # TODO: check what we should put here...
    #         # tr.panels_written = False
    #         # tr.data_frame = tr.data_frame.rename(columns={tr.panel.varname: "__PANEL_KEY__"})

    #     return self
    #     # return tr

    def infer_panels(self):
        """
        If no panels are already present, this method will look through each column to try to infer
        panel columns. If it finds columns that can be inferred, it will create the appropriate
        panel class and add it to the Trelliscope object.

        Returns a copy of the Trelliscope object. The original is not modified.
        """

        tr = self.__copy()
        # Note: In R, this logic is found in the as_trelliscope function

        panel_cols = tr._get_panel_columns()

        if len(panel_cols) == 0:
            # No panels exist yet

            # Check for a `Figure` col
            figure_columns = utils.find_figure_columns(tr.data_frame)

            for column in figure_columns:
                # If there is a predefined panel options object for this column, use it
                panel_options = tr._get_panel_options(column)

                # Create the panel
                panel = Panel.create_panel(
                    df=tr.data_frame,
                    panel_column=column,
                    panel_options=panel_options,
                    is_known_figure_col=True,
                )
                tr = tr.add_panel(panel)

            # Check for image panels
            image_columns = utils.find_image_columns(tr.data_frame)
            for column in image_columns:
                # If there is a predefined panel options object for this column, use it
                panel_options = tr._get_panel_options(column)

                # Create the panel
                panel = Panel.create_panel(
                    df=tr.data_frame,
                    panel_column=column,
                    panel_options=panel_options,
                    is_known_image_col=True,
                )
                tr = tr.add_panel(panel)

        # If the primary panel is None, try to re-infer it, because there may be one now
        if tr.primary_panel is None:
            tr._infer_primary_panel()

        return tr

    def _copy_images_to_build_directory(
        self,
        column_name: str,
        output_dir_for_writing: str,
        output_dir_for_dataframe: str,
    ) -> None:
        """
        Copies the images found in the provided column into the build output directory so they will
        be self contained in the output. Two directories are provided, one for the destination of the copy
        command (likely an absolute path) and one to be the directory left in the data frame (likely
        a relative path).
        """
        self.data_frame[column_name] = self.data_frame.apply(
            lambda row: Trelliscope.__copy_image_and_update_reference(
                row=row,
                image_column=column_name,
                output_dir_for_writing=output_dir_for_writing,
                output_dir_for_dataframe=output_dir_for_dataframe,
            ),
            axis=1,
        )

    @staticmethod
    def __copy_image_and_update_reference(
        row,
        image_column: str,
        output_dir_for_writing: str,
        output_dir_for_dataframe: str,
    ) -> str:
        """
        Copies an image to a new directory and updates the reference in the dataframe. This function is
        designed to be passed to a DataFrame.apply() call to copy each image
        Params:
            row - The DataFrame row
            image_column:str - The name of the column containing the image
            output_dir_for_writing:str - Used for writing the image. It is most likely an
                absolute path.
            output_dir_for_dataframe:str - Used for the result in the dataframe. It is most likely a
                relative path.
        """
        # Get the original file (including path) from the dataframe
        original_image_file = row[image_column]

        # Split the filename off of the directory
        (_, filename) = os.path.split(original_image_file)

        # Create the two paths
        filename_for_writing = os.path.join(output_dir_for_writing, filename)
        filename_for_dataframe = os.path.join(output_dir_for_dataframe, filename)

        # Copy the file
        shutil.copyfile(original_image_file, filename_for_writing)

        # Return the new filename to update the dataframe
        return filename_for_dataframe

    def _get_panel_columns(self):
        """
        Look for panels that have previously been defined.
        Returns:
            A list of the col names that are defined as panels.
            If none are found, an empty list is returned.
        """
        return list(self.panels.keys())

    def _get_panel_figure_columns(self):
        """
        Returns a list of the columns that are the varnames of the figures in the data frame.
        This used because when writing panels, the `varname` column will be updated to contain
        the filename, but the original figure is preserved in this "figure" column.
        """
        figure_columns = [panel.figure_varname for panel in self.panels.values()]

        return figure_columns

    def _write_display_info(self, jsonp: bool, id: str):
        """
        Creates the displayInfo json file.
        """
        file = utils.get_file_path(
            self.get_dataset_display_path(), Trelliscope.DISPLAY_INFO_FILE_NAME, jsonp
        )

        content = self.to_json(True)
        function_name = f"__loadDisplayInfo__{id}"

        utils.write_json_file(file, jsonp, function_name, content)

    def _update_display_list(self, app_path: str, jsonp: bool, id: str):
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

        display_list_file = utils.get_file_path(
            self.get_displays_path(), Trelliscope.DISPLAY_LIST_FILE_NAME, jsonp
        )
        function_name = f"__loadDisplayList__{id}"
        content = json.dumps(display_info_list, indent=2)
        utils.write_json_file(display_list_file, jsonp, function_name, content)

    def _get_metas_list(self) -> list:
        """
        Gets a list of all the metas.
        """
        meta_list = [meta.to_dict() for meta in self.metas.values()]
        return meta_list

    def _write_meta_data(self, id: str):
        """
        Writes the meta data file.

        Params:
            jsonp: bool - Should jsonp format be used instead of json?
            id: str - The id for the data set.
        """
        meta_data_filename = Trelliscope.METADATA_FILE_NAME + ".js"
        meta_data_file = os.path.join(
            self.get_dataset_display_path(), meta_data_filename
        )

        # TODO: Verify that we only want the meta columns here
        meta_columns = [meta_name for meta_name in self.metas]
        meta_df = self.data_frame[meta_columns].copy()

        # meta_df = meta_df.drop("lifeExp_time", axis=1)

        # Convert any category columns to codes
        for meta in self.metas.values():
            if isinstance(meta, FactorMeta):
                # Convert this column to use the category code (the factor index) instead
                # of the name. Also, note that we are adding one because the rendering code
                # expects the R style of 1-based indexes.
                meta_df[meta.varname] = meta_df[meta.varname].cat.codes + 1

        if self.pretty_meta_data:
            # Pretty print the json if in debug mode
            meta_data_json = meta_df.to_json(orient="records", indent=2)
        else:
            meta_data_json = meta_df.to_json(orient="records")

        # Turn the escaped \/ into just /
        meta_data_json = meta_data_json.replace("\\/", "/")

        window_var_name = "metaData"
        utils.write_window_js_file(
            file_path=meta_data_file,
            window_var_name=window_var_name,
            content=meta_data_json,
        )

    def _write_javascript_lib(self):
        """
        Writes the JavaScript libraries to the output directory
        """
        output_path = self.get_output_path()
        html_utils.write_javascript_lib(output_path)

    def _write_widget(self):
        output_path = self.get_output_path()
        config_path = self._get_existing_config_filename()
        config_file = os.path.basename(config_path)

        id = self.id
        is_spa = True

        html_utils.write_widget(output_path, id, config_file, is_spa)

    @staticmethod
    def __write_figure(
        row,
        fig_column: str,
        output_dir_for_writing: str,
        output_dir_for_dataframe: str,
        extension: str,
        key_cols: list,
        progress_bar: ProgressBar = None,
    ):
        """
        Saves a figure object to an image file. This function is designed to be passed to
        a DataFrame.apply() call to write out each figure.
        Params:
            row - The DataFrame row
            fig_column:str - The name of the figure column to write out
            output_dir_for_writing:str - Used for writing the image. It is most likely an
                absolute path.
            output_dir_for_dataframe:str - Used for the result in the dataframe. It is most likely a
                relative path.
            extension:str - The file name extension to write (for example, "png")
            key_cols:str - The columns that are used as the key (ie, index, group by) for this figure
        """
        fig = row[fig_column]

        filename_prefix = ""
        if len(key_cols) > 0:
            key_col_values = [str(row[key_col]) for key_col in key_cols]
            filename_prefix = "_".join(key_col_values)
        else:
            filename_prefix = row.name

        filename_prefix = utils.sanitize(filename_prefix)

        filename_for_writing = os.path.join(
            output_dir_for_writing, f"{filename_prefix}.{extension}"
        )
        filename_for_dataframe = os.path.join(
            output_dir_for_dataframe, f"{filename_prefix}.{extension}"
        )

        # logging.debug(f"Saving image {filename_for_writing}")
        fig.write_image(filename_for_writing)

        try:
            progress_bar.record_progress()
        except Exception:
            # If the progress display has a problem, just ignore it.
            pass

        return filename_for_dataframe

    def write_or_copy_panels(self, panel_col: str):
        """
        Writes the panels to the output directory (or copies them if they are already files).
        """
        tr = self.__copy()

        panel = self._get_panel(panel_col)

        # if not (panel.is_writeable or panel.should_copy):
        #     raise ValueError("Error: Attempting to write a panel that is not writable or should not be copied")

        absolute_output_dir = tr._get_panel_output_path(panel_col, is_absolute=True)
        relative_output_dir = tr._get_panel_output_path(panel_col, is_absolute=False)

        if not os.path.isdir(absolute_output_dir):
            os.makedirs(absolute_output_dir)

        # TODO: check if the panel is an html widget, and if so, create it here (see R)

        if panel.should_copy:
            tr._copy_images_to_build_directory(
                panel_col, absolute_output_dir, relative_output_dir
            )
        elif panel.is_writeable:
            # panel_keys = tr._get_panel_paths_from_keys()
            extension = panel.get_extension()

            # TODO: Follow the logic in the R version to match filenames, etc.
            # tr.data_frame["__PANEL_KEY__"] = tr.data_frame.apply(lambda row: Trelliscope.__write_figure(row, panel_col, output_dir, extension, self.key_cols), axis=1)

            # TODO: Do we want to overwrite the current panel column (which is full of figure objects)
            # with the new one full of filenames? Or should we create a new one and just make sure that the old
            # one is excluded from the metas list, etc.

            # SB: For now, let's preserve the old with another column
            tr.data_frame[panel.figure_varname] = tr.data_frame[panel_col]

            progress_bar = ProgressBar(len(tr.data_frame), "Saving Images:")

            tr.data_frame[panel_col] = tr.data_frame.apply(
                lambda row: Trelliscope.__write_figure(
                    row=row,
                    fig_column=panel_col,
                    output_dir_for_writing=absolute_output_dir,
                    output_dir_for_dataframe=relative_output_dir,
                    extension=extension,
                    key_cols=self.key_cols,
                    progress_bar=progress_bar,
                ),
                axis=1,
            )

            # TODO: Handle creating hash and key sig to avoid having to re-write panels
            # that have already been generated here.
            # One of the things that needs to happen here is to set the keysig to a hash of the columns

        panel.panels_written = True

        return tr

    # def _get_panel_paths_from_keys(self):
    #     path = "_".join(self.key_cols)
    #     path = utils.sanitize(path)

    #     # TODO: Make sure the sanitized key columns still uniquely identify the row
    #     # TODO: Do we need to sanitize (and change) the actual panel columns here?

    #     return path

    # Currently unused.
    # def add_meta_defs(self):
    #     return self.__copy()

    # Currently unused.
    # def add_meta_labels(self):
    #     return self.__copy()

    def set_default_labels(self, varnames: list):
        """
        Add a labels state specification to a trelliscope display.
        Params:
            varnames:list(str) - The varnames for the labels.

        Returns a copy of the Trelliscope object. The original is not modified.
        """
        tr = self.__copy()

        label_state = LabelState(varnames)
        label_state.check_with_data(tr.data_frame)

        state2 = tr.state._copy()
        state2.set(label_state)

        tr = tr.set_state(state2)

        return tr

    def set_default_layout(self, ncol: int = 1, page: int = 1):
        """
        Add a layout state specification to a trelliscope display.
        Params:
            ncol:int - The number of columns.
            page:int - The number of pages.

        Returns a copy of the Trelliscope object. The original is not modified.
        """
        tr = self.__copy()

        layout_state = LayoutState(ncol, page)
        layout_state.check_with_data(tr.data_frame)

        state2 = tr.state._copy()
        state2.set(layout_state)

        tr = tr.set_state(state2)
        return tr

    def set_default_sort(
        self, varnames: list, sort_directions: list = None, add: bool = False
    ):
        """
        Adds a SortState to the Trelliscope.
        Params:
            varnames:list - A list of variable names to sort on.
            sort_directions: - A list of "asc" and "desc" for each variable to sort on. If None,
                then ascending sort will be used for all variables. If a single direction is passed
                in the list, it will be used for all varnames.
            add:bool - Should an existing sort specification be added to? (If `False` (default),
                the entire sort specification will be overridden).

        Returns a copy of the Trelliscope object. The original is not modified.
        """
        tr = self.__copy()

        if sort_directions is None:
            sort_directions = [SortState.DIR_ASCENDING] * len(varnames)
        elif len(sort_directions) == 1:
            sort_directions = sort_directions * len(varnames)

        if len(varnames) != len(sort_directions):
            raise ValueError(
                "In setting sort state, 'varnames' must have same length as 'dirs'"
            )

        state2 = tr.state._copy()

        is_first = True
        for varname, direction in zip(varnames, sort_directions):
            ss = SortState(varname, direction)
            ss.check_with_data(tr.data_frame)

            to_add = not is_first or add
            state2.set(ss, to_add)

            is_first = False

        tr = tr.set_state(state2)

        return tr

    def set_default_filters(self, filters: list = [], add: bool = True):
        """
        Add a filter state specifications to a trelliscope display.
        Params:
            filters:list - A list of FilterState specifications
            add:bool - Should existing filter state specifications be added to?
                If False, the entire filter state specification will be overridden.

        Returns a copy of the Trelliscope object. The original is not modified.
        """
        tr = self.__copy()

        state2 = tr.state._copy()

        is_first = True
        for filter in filters:
            if not isinstance(filter, FilterState):
                raise ValueError("Filters must inherit from FilterState.")

            filter.check_with_data(tr.data_frame)

            state2.set(filter, (not is_first or add))

        tr = tr.set_state(state2)
        return tr

    def set_primary_panel(self, panel_column_name: str):
        """
        Sets the primary panel. Note that a panel with this name
        should already be defined as a panel.

        Params:
            panel_column_name:str - The name of the panel column.

        Returns a copy of the Trelliscope object. The original is not modified.
        """
        tr = self.__copy()

        if not tr._has_panel(panel_column_name):
            raise ValueError("Error: Primary panel should be a panel.")

        tr.primary_panel = panel_column_name

        return tr

    def set_panel_options(self, panel_options_dictionary: dict):
        """
        Used to pre-specify information about the `Panel` objects before they are actually
        created. Then, later when the `Panel` object is inferred, data from this object will be used
        to populate it.

        If panel objects already exist for the associated panels, a warning will be generated.

        Params:
            panel_options_dictionary:dict - This should be a dictionary mapping
                the name of the panel to a `PanelOptions` object.

        Returns a copy of the Trelliscope object. The original is not modified.
        """
        tr = self.__copy()

        for panel_name in panel_options_dictionary:
            panel_options: PanelOptions = panel_options_dictionary[panel_name]

            if not isinstance(panel_options, PanelOptions):
                raise ValueError(
                    f"Error: Panel options for {panel_name} must be specified using a PanelOptions object."
                )

            if tr._has_panel(panel_name):
                logging.warn(
                    f"Setting PanelOptions for a panel `{panel_name}` that already exists. "
                    + "The PanelOptions are designed to be set before panels are created."
                )

            tr.panel_options[panel_name] = panel_options

        return tr

    def _get_panel_options(self, panel_name: str):
        """
        Gets the `PanelOptions` object associated with the provided panel_name, if it exists. If
        it does not exist, None will be returned.
        """
        panel_options = None

        if panel_name in self.panel_options:
            panel_options = self.panel_options[panel_name]

        return panel_options

    def view_trelliscope(self):
        """
        Attempts to open the current Trelliscope in a browser.

        Note: The Trelliscope should be written first using `write_display()`
        """
        index_file = os.path.join(self.get_output_path(), "index.html")

        if not os.path.exists(index_file):
            raise ValueError(
                "No files exist for this Trelliscope exist. Before viewing the Trelliscope, "
                + "ensure that the `write_display` method has been called."
            )

        full_path = "file://" + os.path.realpath(index_file)

        NEW_TAB = 2
        webbrowser.open(full_path, NEW_TAB)

        return self

    def __copy(self):
        """
        Internal method used throughout the library to make a copy of the Trelliscope object.
        """
        # TODO: Should this do a deep copy? Should it make copies of metas?
        return copy.deepcopy(self)
