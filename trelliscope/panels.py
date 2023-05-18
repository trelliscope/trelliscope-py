import pandas as pd
from trelliscope import utils

# TODO: Determine how to work with image panels.

# class ImagePanel():
#     def __init__(self, files:list, aspect_ratio=1.5) -> None:
#         utils.check_image_extension(files)
#         utils.check_positive_numeric(aspect_ratio)

#         self.files = files
#         self.aspect_ratio = aspect_ratio

# # TODO: Add other image panel types here.


class Panel:
    def __init__(self, varname:str, aspect_ratio:float=1.5, is_local:bool=False, is_image:bool=True, writeable:bool=False) -> None:
        # TODO: Should we have a flag for HTML vs Image, or just infer it??

        self.varname = varname
        self.aspect_ratio = aspect_ratio
        self.is_local = is_local
        self.is_image = is_image
        self.is_writeable = writeable

    def get_extension(self) -> str:
        raise NotImplementedError("This type of panel does not provide for extensions.")

    def _infer_params(self):
        """
        Infers where possible:
        * is_local
        * is_image
        """
        pass

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
        return ImagePanel(panel_col)

class ImagePanel(Panel):
    def __init__(self, varname: str, aspect_ratio: float = 1.5, is_local: bool = False) -> None:
        super().__init__(varname, aspect_ratio, is_local, is_image=True, writeable=False)

class IFramePanel(Panel):
    def __init__(self, varname: str, aspect_ratio: float = 1.5, is_local: bool = False) -> None:
        super().__init__(varname, aspect_ratio, is_local, is_image=False, writeable=False)

class FigurePanel(Panel):
    def __init__(self, varname: str, extension: str = "png", aspect_ratio: float = 1.5, is_local: bool = True) -> None:
        super().__init__(varname, aspect_ratio, is_local, is_image=False, writeable=True)
        self.extension = extension

    def get_extension(self) -> str:
        return self.extension


# class ImagePanelSeries(pd.Series):
#     def __init__(self) -> None:
#         super().__init__()