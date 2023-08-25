import pandas as pd
from .panel_source import PanelSource, FilePanelSource


# def panel_local(series:pd.Series, panel_source:str):
#     panel_info = {}
#     panel_info["panel_source"] = panel_source

#     series.attrs["panel_info"] = panel_info
#     return series

class PanelDataFrame(pd.DataFrame):
    # _metadata = ["is_panel"]

    def __init__(self, df:pd.DataFrame) -> None:
        super().__init__(df)

    @property
    def _constructor(self):
        def _panel_data_frame_constructor(*args, **kwargs):

            df = PanelDataFrame(*args, **kwargs)
            # TODO: Consider checking if any panels columns actually exist,
            # and if not, we could just do a regular data frame here instead...
            # if ...:
            #     df = pd.DataFrame(df)

            return df

        return _panel_data_frame_constructor.__finalize__(self)

    @property
    def _constructor_sliced(self):
        def _panel_constructor_sliced(*args, **kwargs):
            series = PanelSeries(*args, **kwargs)

            if series.is_panel:
                print("it was a panel!")
            if not series.is_panel:
                series = pd.Series(series)

            return series

        return _panel_constructor_sliced.__finalize__(self)
    


class PanelSeries(pd.Series):
    """
    A Pandas Series object with extra Panel information.

    This class implements the decorator pattern that wraps an internal pd.Series object.
    """
    # _metadata = ["is_panel"]


    def __init__(self, data:pd.Series, panel_source:PanelSource=None, aspect_ratio:float=1.5, is_local:bool=False, is_image:bool=True, writeable:bool=False, **kwargs) -> None:
        super().__init__(data, **kwargs)

        # if not isinstance(data, pd.Series):
        #     raise AttributeError("Base series must descend from pd.Series")

        # self._base_series = base_series

        # if panel_source is not None:
        #     self.is_panel = True

        if panel_source is None:
            self.is_panel = False
        else:
            self.is_panel = True

        self.panel_source = panel_source

        self.aspect_ratio = aspect_ratio
        self.is_local = is_local
        self.is_image = is_image
        self.is_writeable = writeable
        self.panels_written = False

    _metadata = ["panel_source", "aspect_ratio", "is_local", "is_image", "is_writeable", "panels_written"]

    # @property
    # def is_panel(self):
    #     return self._is_panel

    # @is_panel.setter
    # def is_panel(self, value):
    #     self._is_panel = value

    @property
    def _constructor(self):
        def _panel_series_constructor(data=None, panel_source=None, **kwargs):
            
            # if panel_source is None:
            #     series = pd.Series(data, **kwargs)
            # else:
            #     series = PanelSeries(data, panel_source, **kwargs)
            series = PanelSeries(data, panel_source, **kwargs)

            return series

        return _panel_series_constructor.__finalize__(self)

    @property
    def _constructor_expanddim(self):
        def _panel_series_expanddim_constructor(data=None, *args, **kwargs):
            
            df = pd.DataFrame(data, *args, **kwargs)

            # Do we want something like this??
            # if isinstance(data, PanelSeries):
            # or to check if there are any PanelSeries columns in the DF,
            # and if not, return a regular DF?

            df = PanelDataFrame(df)

            return df

        return _panel_series_expanddim_constructor.__finalize__(self)
    
    def get_extension(self) -> str:
        raise NotImplementedError("This type of panel does not provide for file extensions.")

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
