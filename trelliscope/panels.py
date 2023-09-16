import pandas as pd
from trelliscope import utils
from .panel_source import PanelSource, FilePanelSource

class Panel:
    _FIGURE_SUFFIX = "__FIGURE"
    _PANEL_TYPE_IMAGE = "img"
    _PANEL_TYPE_IFRAME = "iframe"

    def __init__(self, varname:str, panel_type_str:str, source:PanelSource, aspect_ratio:float=1.5,
                 is_image:bool=True, writeable:bool=False) -> None:
        # TODO: Should we have a flag for HTML vs Image, or just infer it??

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

    @staticmethod
    def create_panel(df: pd.DataFrame, panel_col: str):
        """
        A factory method to create a new panel object. This method
        infers the type and other parameters based on the data found in the
        `panel_col` column in the data frame.
        """
        # TODO: Fill in the inference logic here
        
        # For now, just return an image panel for test purposes
        return ImagePanel(panel_col, FilePanelSource())

class ImagePanel(Panel):
    def __init__(self, varname: str, source:PanelSource, aspect_ratio: float = 1.5, should_copy_to_output=True) -> None:
        super().__init__(varname, Panel._PANEL_TYPE_IMAGE, source, aspect_ratio, is_image=True, writeable=False)

        self.should_copy = should_copy_to_output

    # def get_panel_source(self) -> dict:
    #     # TODO: check if remote panels still have type=file
    #     return super().get_panel_source()

class IFramePanel(Panel):
    def __init__(self, varname: str, source:PanelSource, aspect_ratio: float = 1.5) -> None:
        super().__init__(varname, Panel._PANEL_TYPE_IFRAME, source, aspect_ratio, is_image=False, writeable=False)

class FigurePanel(Panel):
    def __init__(self, varname: str, source:PanelSource, extension: str = "png", aspect_ratio: float = 1.5) -> None:
        super().__init__(varname, Panel._PANEL_TYPE_IMAGE, source, aspect_ratio, is_image=False, writeable=True)

        self.extension = extension
        self.figure_varname = self.varname + Panel._FIGURE_SUFFIX

    def get_extension(self) -> str:
        return self.extension
    
    # def get_panel_source(self) -> dict:
    #     return {"type": "file"}

# class ImagePanelSeries(pd.Series):
#     def __init__(self) -> None:
#         super().__init__()

class PanelOptions():
    def __init__(self, width:int = 500, height:int = 500, format:str = None,
                 force:bool = False, prerender:bool = True, type:str = None, aspect:float = None) -> None:
        utils.check_positive_numeric(width, "width")
        utils.check_positive_numeric(height, "height")
        utils.check_bool(force, "force")
        utils.check_bool(prerender, "prerender")

        if format is not None:
            utils.check_enum(format, ["png", "svg", "html"])
            
        self.width = width
        self.height = height
        self.force = force
        self.prerender = prerender
        self.type = type

        if aspect is None:
            self.aspect = width / height
        else:
            self.aspect = aspect
