import pandas as pd
from trelliscope import utils
from .panel_source import PanelSource, FilePanelSource

class PanelOptions():
    """
    Stores settings associated with panel. The PanelOptions object is used by the `Trelliscope`
    `set_panel_options` method to pre-specify information about the `Panel` before it is actually
    created. Then, later when the `Panel` object is inferred, data from this object will be used
    to populate it.
    """

    def __init__(self, width:int = 600, height:int = 400, format:str = None,
                 force:bool = False, prerender:bool = True, type:str = None, aspect:float = None) -> None:
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
    _FIGURE_SUFFIX = "__FIGURE"
    _PANEL_TYPE_IMAGE = "img"
    _PANEL_TYPE_IFRAME = "iframe"

    def __init__(self, varname:str, panel_type_str:str, source:PanelSource, aspect_ratio:float=1.5,
                 is_image:bool=True, writeable:bool=False) -> None:
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
        # Default serialization behavior is sufficient
        return self.__dict__.copy()
    
    def get_extension(self) -> str:
        raise NotImplementedError("This type of panel does not provide for extensions.")

    def check_valid(self, df: pd.DataFrame):
        # Check that varname exists
        utils.check_has_variable(df, self.varname)

        # Check that the extension matches
        # TODO: Add this in
        pass

    # SB: This method doesn't really make much sense because the only properties you can set
    # at this point are aspect ratio and extension.
    # def set_options(self, panel_options:PanelOptions):
    #     """
    #     Sets values on this `Panel` object as specified in the provided `PanelOptions` object.

    #     Params:
    #         panel_options:PanelOptions - The values to set.

    #     Side Effects: The `Panel` object is updated.
    #     """
    #     # TODO: Should panels store width and height directly, or just the aspect ratio?
        
    #     if panel_options.aspect is not None:
    #         self.aspect_ratio = panel_options.aspect



    # # Not currently used:
    # @staticmethod
    # def create_panel(df: pd.DataFrame, panel_col: str):
    #     """
    #     A factory method to create a new panel object. This method
    #     infers the type and other parameters based on the data found in the
    #     `panel_col` column in the data frame.
    #     """
    #     # TODO: Fill in the inference logic here
        
    #     # For now, just return an image panel for test purposes
    #     return ImagePanel(panel_col, FilePanelSource())

class ImagePanel(Panel):
    def __init__(self, varname: str, source:PanelSource, aspect_ratio: float = 1.5, should_copy_to_output=True) -> None:
        super().__init__(varname=varname, panel_type_str=Panel._PANEL_TYPE_IMAGE, source=source,
                         aspect_ratio=aspect_ratio, is_image=True, writeable=False)

        self.should_copy = should_copy_to_output

    # def get_panel_source(self) -> dict:
    #     # TODO: check if remote panels still have type=file
    #     return super().get_panel_source()

class IFramePanel(Panel):
    def __init__(self, varname: str, source:PanelSource, aspect_ratio: float = 1.5) -> None:
        super().__init__(varname=varname, panel_type_str=Panel._PANEL_TYPE_IFRAME, source=source,
                         aspect_ratio=aspect_ratio, is_image=False, writeable=False)

class FigurePanel(Panel):
    def __init__(self, varname: str, source:PanelSource, extension: str = "png", aspect_ratio: float = 1.5) -> None:
        super().__init__(varname=varname, panel_type_str=Panel._PANEL_TYPE_IMAGE, source=source,
                         aspect_ratio=aspect_ratio, is_image=False, writeable=True)

        self.extension = extension
        self.figure_varname = self.varname + Panel._FIGURE_SUFFIX

    def get_extension(self) -> str:
        return self.extension
    
    # def get_panel_source(self) -> dict:
    #     return {"type": "file"}

