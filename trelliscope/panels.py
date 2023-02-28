import pandas as pd
from .trelliscope import utils

# TODO: Determine how to work with image panels.

# class ImagePanel():
#     def __init__(self, files:list, aspect_ratio=1.5) -> None:
#         utils.check_image_extension(files)
#         utils.check_positive_numeric(aspect_ratio)

#         self.files = files
#         self.aspect_ratio = aspect_ratio

# # TODO: Add other image panel types here.


class Panel:
    def __init__(self, varname:str, aspect_ratio:float=1.5, is_local:bool=False, is_image:bool=True) -> None:
        # TODO: Should we have a flag for HTML vs Image, or just infer it??

        self.varname = varname
        self.aspect_ratio = aspect_ratio
        self.is_local = is_local
        self.is_image = is_image

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

class ImagePanel(Panel):
    def __init__(self, varname: str, aspect_ratio: float = 1.5, is_local: bool = False,) -> None:
        super().__init__(varname, aspect_ratio, is_local, is_image=True)

class IFramePanel(Panel):
    def __init__(self, varname: str, aspect_ratio: float = 1.5, is_local: bool = False,) -> None:
        super().__init__(varname, aspect_ratio, is_local, is_image=False)