import pandas as pd
from .panel_source import PanelSource, FilePanelSource


class PanelSeries(pd.Series):
    def __init__(self, panel_source:PanelSource, aspect_ratio:float=1.5, is_local:bool=False, is_image:bool=True, writeable:bool=False) -> None:
        super().__init__()

        self.panel_source = panel_source

        self.aspect_ratio = aspect_ratio
        self.is_local = is_local
        self.is_image = is_image
        self.is_writeable = writeable

    def get_extension(self) -> str:
        raise NotImplementedError("This type of panel does not provide for file extensions.")
    
class ImagePanelSeries(PanelSeries):
    def __init__(self, aspect_ratio: float = 1.5, is_local: bool = False) -> None:
        super().__init__(FilePanelSource(), aspect_ratio, is_local, is_image=True, writeable=False)

class IFramePanelSeries(PanelSeries):
    def __init__(self, panel_source: PanelSource, aspect_ratio: float = 1.5, is_local: bool = False) -> None:
        super().__init__(panel_source, aspect_ratio, is_local, is_image=False, writeable=False)

class FigurePanelSeries(PanelSeries):
    def __init__(self, extension: str = "png", aspect_ratio: float = 1.5, is_local: bool = True) -> None:
        super().__init__(FilePanelSource(), aspect_ratio, is_local, is_image=False, writeable=True)
        self.extension = extension

    def get_extension(self) -> str:
        return self.extension
