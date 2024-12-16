"""Panels module."""
import pandas as pd

from trelliscope import utils
from trelliscope.panel_source import FilePanelSource, PanelSource


class PanelOptions:
    """Stores settings associated with panel.

    The PanelOptions object is used by the :func:`trelliscope.trelliscope.Trelliscope.set_panel_options`
    method to pre-specify information about the :class:`.Panel` before it is actually
    created. Then, later when the :class:`.Panel` object is inferred, data from this object will be used
    to populate it.
    """

    def __init__(
        self,
        width: int = 600,
        height: int = 400,
        format: str = None,
        force: bool = False,
        prerender: bool = True,
        type: str = None,
        aspect: float = None,
    ) -> None:
        """Create PanelOptions objects.

        Args:
            width: Strictly positive integer representing the panel width in pixels.
            height: Stricly positive integer representing the panel height in pixels.
            format: One of 'png', 'svg' or 'html'. If `None` then is inferred.
            force: (Default False) Whether to force creation of plots, even if they already exist.
            prerender: (Default True) Prerender.
            type: Type of panel. TODO: list possible types.
            aspect: Aspect ratio of the panel, if not given it is determined from ``width`` / ``height``.

        Raises:
            ValueError: If ``width`` or ``height`` is not a positive numeric value.
                Or, if ``force`` or ``prerender`` is not a boolean.
                Or, if ``format`` not an allowed value.
        """
        utils.check_positive_numeric(width, "width")
        utils.check_positive_numeric(height, "height")
        utils.check_bool(force, "force")
        utils.check_bool(prerender, "prerender")

        if format is not None:
            utils.check_enum(format, ["png", "svg", "html"])

        self.width = width
        self.height = height
        self.format = format
        self.force = force
        self.prerender = prerender
        self.type = type

        if aspect is None:
            self.aspect = width / height
        else:
            self.aspect = aspect


class Panel:
    """Base Panel object."""

    _FIGURE_SUFFIX = "__FIGURE"
    _PANEL_TYPE_IMAGE = "img"
    _PANEL_TYPE_IFRAME = "iframe"

    def __init__(
        self,
        varname: str,
        panel_type_str: str,
        source: PanelSource,
        aspect_ratio: float = 1.5,
        is_image: bool = True,
        writeable: bool = False,
    ) -> None:
        """Create Panel object.

        Args:
            varname: Variable name.
            panel_type_str: Panel type, one of ['img', 'iframe'].
            source: PanelSource object, defining where the load the panel content from.
            aspect_ratio: Aspect ratio of the displayed panel.
            is_image: Boolean flag whether panel is an image.
            writeable: Boolean flag whether panel is writable.
        """
        self.varname = varname
        self.aspect_ratio = aspect_ratio
        self.is_image = is_image
        self.is_writeable = writeable
        self.should_copy = False
        self.source = source
        self.panel_type_str = panel_type_str

        self.panels_written = False
        self.figure_varname = None

    def to_dict(self):
        """Return a dictionary of this Panel's attributes.."""
        # Default serialization behavior is sufficient
        return self.__dict__.copy()

    def get_extension(self) -> str:
        """Get the extension of this Panel.

        Raise:
            NotImplementedError: if not overwritten in subclasses.
        """
        raise NotImplementedError("This type of panel does not provide for extensions.")

    def check_valid(self, df: pd.DataFrame):
        """Check that the dataframe contains the panel variable as a column."""
        # Check that varname exists
        utils.check_has_variable(df, self.varname)

    @staticmethod
    def create_panel(
        df: pd.DataFrame,
        panel_column: str,
        panel_options: PanelOptions = None,
        is_known_figure_col: bool = False,
        is_known_image_col: bool = False,
    ):
        """A factory method to create a new panel object by inferring the type of the panel.

        This method infers the type and other parameters based on the data found in the
        `panel_col` column in the data frame.

        Params:
            df: The pandas DataFrame to create the panel from.
            panel_column: The name of the panel column.
            panel_options: Optionally pass explicit panel options, otherwise defaults are used.
            is_known_figure_col: Boolean flag to use if type of panel is a figure, inferred if `False`.
            is_known_image_col: Boolean flag to use if type of panel is an image, inferred if `False`.

        Returns:
            Either a :class:`trelliscope.panels.FigurePanel` or a :class:`trelliscope.panels.ImagePanel`.

        Raise:
            NotImplementedError: If panel options are passed but `panel_options.prerender=False`.
            ValueError: If `is_known_image_col` and `is_known_image_col` are False and panel type
                cannot be inferred otherwise.
        """
        # Note: In R, much of this logic is found in: infer_meta_variable

        # It is not already determined to be an image or figure column
        # Check to see if it is one of these before proceeding
        if not (is_known_image_col or is_known_figure_col):
            if utils.is_image_column(df, panel_column):
                is_known_image_col = True
            elif utils.is_figure_column(df, panel_column):
                is_known_figure_col = True

        panel = None
        panel_source = None

        # In R, there is a check here for lazy panels. This will need to be added when those
        # are made available in Python.

        if panel_options is not None and not panel_options.prerender:
            # panel_source = LocalWebSocketPanelSource()
            raise NotImplementedError(
                "Local Web Socket Panel Source is not implemented yet."
            )
        else:
            panel_source = FilePanelSource(is_local=True)

        if is_known_figure_col:
            panel_source.is_local = True
            panel = FigurePanel(panel_column, source=panel_source)

            if panel_options is not None and panel_options.format is not None:
                panel.extension = panel_options.format

        elif is_known_image_col or utils.is_image_column(df, panel_column):
            is_local = not utils.is_all_remote(df[panel_column])
            panel_source.is_local = is_local

            # If it is a local image file, set to copy to the output directory
            should_copy = is_local

            panel = ImagePanel(
                panel_column, source=panel_source, should_copy_to_output=should_copy
            )

        else:
            raise ValueError(
                f"Could not determine how to create a panel for {panel_column}"
            )

        # General settings that could come from panel options
        if panel_options is not None:
            if panel_options.aspect is not None:
                panel.aspect_ratio = panel_options.aspect

        # TODO: Implement infer aspect ratio logic if it is not specified explicitly.
        # In R, this is found in the `infer_aspect_ratio` function in infer.R

        return panel


class ImagePanel(Panel):
    """Panel for displaying images directly."""

    def __init__(
        self,
        varname: str,
        source: PanelSource,
        aspect_ratio: float = 1.5,
        should_copy_to_output: bool = True,
    ) -> None:
        """Create Panel object to display image.

        Args:
            varname: Variable name.
            source: Panel source object to define where image comes from.
            aspect_ratio: Aspect ratio to display.
            should_copy_to_output: Boolean whether image files should be copied to output directory.
        """
        super().__init__(
            varname=varname,
            panel_type_str=Panel._PANEL_TYPE_IMAGE,
            source=source,
            aspect_ratio=aspect_ratio,
            is_image=True,
            writeable=False,
        )

        self.should_copy = should_copy_to_output

    # def get_panel_source(self) -> dict:
    #     # TODO: check if remote panels still have type=file
    #     return super().get_panel_source()


class IFramePanel(Panel):
    """Create Panel object to embed iframes."""

    def __init__(
        self, varname: str, source: PanelSource, aspect_ratio: float = 1.5
    ) -> None:
        """Create Panel object to embed iframes.

        Args:
            varname: Variable name.
            source: Panel source object to define where html source to iframe comes from.
            aspect_ratio: Aspect ratio to display.
        """
        super().__init__(
            varname=varname,
            panel_type_str=Panel._PANEL_TYPE_IFRAME,
            source=source,
            aspect_ratio=aspect_ratio,
            is_image=False,
            writeable=False,
        )


class FigurePanel(Panel):
    """Create Panel object from plotly Figures directly.

    Effectively creates an Image panel by saving the Figure to a static file.
    """

    def __init__(
        self,
        varname: str,
        source: PanelSource,
        extension: str = "png",
        aspect_ratio: float = 1.5,
    ) -> None:
        """Create Panel object to display png image from a plotly Figure.

        Args:
            varname: Variable name.
            source: Panel source to define where figure file is loaded from.
            extension: Extension of figure file, defaults to 'png'.
            aspect_ratio: Aspect ratio to display.
        """
        super().__init__(
            varname=varname,
            panel_type_str=Panel._PANEL_TYPE_IMAGE,
            source=source,
            aspect_ratio=aspect_ratio,
            is_image=False,
            writeable=True,
        )

        self.extension = extension
        self.figure_varname = self.varname + Panel._FIGURE_SUFFIX

    def get_extension(self) -> str:
        """Get expected extension of the figure file."""
        return self.extension

    # def get_panel_source(self) -> dict:
    #     return {"type": "file"}
