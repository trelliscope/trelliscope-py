import json
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

class Meta:
    """
    The base class for all Meta variants.
    """
    def __init__(self, type: str, varname: str, filterable: bool, sortable: bool, label: str = None, tags: list = None):
        # TODO: Should filterable and sortable have default values?
        
        # Note: We are specifically *NOT* using an underscore in these
        # variable names so the default JSON serialization using __dict__ works
        # as expected and produced the correctly named output.
        # This also makes sense in that this class is essentially a struct or a dict
        # with a few extra features.
        self.type = type
        self.varname = varname
        self.filterable = filterable
        self.sortable = sortable
        self.label = label
        
        if tags is None:
            # TODO: Verify this behavior, it's slightly different than what is done in R
            self.tags = []
        else:
            self.tags = tags

    def get_error_message(self, error_text):
        return f"While defining a `{self.type}` meta variable for the variable `{self.varname}`: `{error_text}`"

    def get_data_error_message(self, error_text):
        return f"While checking meta variable definition for variable `{self.varname}` against the data: `{error_text}`"

    def to_json(self, pretty: bool = True):
        indent_value = None

        if pretty:
            indent_value = 2

        return json.dumps(self, default=lambda o: o.__dict__, indent=indent_value)


class NumberMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None):
        super().__init__(type="number", varname=varname, label=label, tags=tags,
            filterable=True, sortable=True)

        # TODO: Should these be settable?
        # TODO: implement checks with regard to these:
        self.digits = None
        self.locale = True

    def check_variable(self, df: pd.DataFrame):
        if not is_numeric_dtype(df[self.varname]):
            raise ValueError(self.get_data_error_message("Data type is not numeric"))



class CurrencyMeta(Meta):
    def __init__(self):
        super().__init__()
        raise NotImplementedError()


class StringMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None):
        super().__init__(type="string", varname=varname, label=label, tags=tags,
            filterable=True, sortable=False)
        
    def check_variable(self, df: pd.DataFrame):
        if not is_string_dtype(df[self.varname]):
            raise ValueError(self.get_data_error_message("Data type is not a string"))

    # TODO: Add a cast variable method

class FactorMeta(Meta):
    def __init__(self):
        super().__init__()
        raise NotImplementedError()


class DateMeta(Meta):
    def __init__(self):
        super().__init__()
        raise NotImplementedError()


class DatetimeMeta(Meta):
    def __init__(self):
        super().__init__()
        raise NotImplementedError()


class GraphMeta(Meta):
    def __init__(self):
        super().__init__()
        raise NotImplementedError()


class GeoMeta(Meta):
    def __init__(self):
        super().__init__()
        raise NotImplementedError()


class HrefMeta(Meta):
    def __init__(self):
        super().__init__()
        raise NotImplementedError()

