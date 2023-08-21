import pandas as pd
from .panel_source import PanelSource, FilePanelSource


class PanelSeries(pd.Series):
    """
    A Pandas Series object with extra Panel information.

    This class implements the decorator pattern that wraps an internal pd.Series object.
    """
    def __init__(self, base_series:pd.Series, panel_source:PanelSource, aspect_ratio:float=1.5, is_local:bool=False, is_image:bool=True, writeable:bool=False) -> None:
        if not isinstance(base_series, pd.Series):
            raise ValueError("Base series must descend from pd.Series")

        self._base_series = base_series
        self.panel_source = panel_source

        self.aspect_ratio = aspect_ratio
        self.is_local = is_local
        self.is_image = is_image
        self.is_writeable = writeable
        self.panels_written = False

        super().__init__()


    def get_extension(self) -> str:
        raise NotImplementedError("This type of panel does not provide for file extensions.")

    # Using the dynamic class wrapper approach outlined here: https://python-patterns.guide/gang-of-four/decorator-pattern/

    # Two methods we don't actually want to intercept,
    # but iter() and next() will be upset without them.
    def __iter__(self):
        return self.__dict__["_base_series"].__iter__()

    def __next__(self):
        return self.__dict__["_base_series"].__next__()
    
    # Offer every other method and property dynamically.
    def __getattr__(self, name):
        return getattr(self.__dict__["_base_series"], name)

    def __setattr__(self, name, value):
        current_member_variables = self.__dict__.keys()
        if name in current_member_variables:
            self.__dict__[name] = value
        else:
            setattr(self.__dict__["_base_series"], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__["_base_series"], name)


class ImagePanelSeries(PanelSeries):
    def __init__(self, base_series:pd.Series, aspect_ratio: float = 1.5, is_local: bool = False) -> None:
        super().__init__(base_series, FilePanelSource(), aspect_ratio, is_local, is_image=True, writeable=False)

class IFramePanelSeries(PanelSeries):
    def __init__(self, base_series:pd.Series, panel_source: PanelSource, aspect_ratio: float = 1.5, is_local: bool = False) -> None:
        super().__init__(base_series, panel_source, aspect_ratio, is_local, is_image=False, writeable=False)

class FigurePanelSeries(PanelSeries):
    def __init__(self, base_series:pd.Series, extension: str = "png", aspect_ratio: float = 1.5, is_local: bool = True) -> None:
        super().__init__(base_series, FilePanelSource(), aspect_ratio, is_local, is_image=False, writeable=True)
        self.extension = extension

    def get_extension(self) -> str:
        return self.extension
