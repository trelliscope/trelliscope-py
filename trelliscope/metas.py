import json
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

from .utils import check_enum
from .currencies import get_valid_currencies

class Meta():
    TYPE_STRING = "string"
    TYPE_HREF = "href"
    TYPE_FACTOR = "factor"
    TYPE_NUMBER = "number"
    TYPE_DATE = "date"
    TYPE_DATETIME = "datetime"
    TYPE_CURRENCY = "currency"
    TYPE_GRAPH = "graph"
    TYPE_GEO = "geo"

    """
    The base class for all Meta variants.
    """
    def __init__(self, type: str, varname: str, filterable: bool, sortable: bool, label: str = None, tags: list = None):
        self.type = type
        self.varname = varname
        self.filterable = filterable
        self.sortable = sortable
        self.label = label
        self.tags = []
        
        if tags is None:
            # TODO: Verify this behavior, it's slightly different than what is done in R
            self.tags = []
        elif isinstance(tags, str):
            self.tags = [tags]
        elif isinstance(tags, list):
            self.tags = tags
        else:
            raise ValueError("Tags is an unrecognized type.")

    def _get_error_message(self, error_text: str):
        return f"While defining a `{self.type}` meta variable for the variable `{self.varname}`: `{error_text}`"

    def _get_data_error_message(self, error_text: str):
        return f"While checking meta variable definition for variable `{self.varname}` against the data: `{error_text}`"

    def to_dict(self) -> dict:
        # Default __dict__ behavior is sufficient, because we don't have custom inner types
        result = self.__dict__

        # We need a label when it gets serialized, so use varname if needed
        if self.label is None:
            result["label"] = self.varname

        return result

    def to_json(self, pretty: bool = True):
        indent_value = None

        if pretty:
            indent_value = 2

        return json.dumps(self.to_dict(), indent=indent_value)

    def check_varname(self, df: pd.DataFrame):        
        if self.varname not in df.columns:
            raise ValueError(self._get_error_message("Could not find variable {self.varname} is in the list of columns"))

    def check_variable(self, df: pd.DataFrame):
        # To be overridden by sub classes
        pass

    def check_with_data(self, df: pd.DataFrame):
        self.check_varname(df)
        self.check_variable(df)


class NumberMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None, digits: int = None, locale: bool = True):
        super().__init__(type=Meta.TYPE_NUMBER, varname=varname, label=label, tags=tags,
            filterable=True, sortable=True)

        if digits is not None and not isinstance(digits, int):
            raise TypeError("Digits must be an integer")

        if locale is not None and not isinstance(locale, bool):
            raise TypeError("Locale must be logical (boolean)")

        self.digits = digits
        self.locale = locale

    def check_variable(self, df: pd.DataFrame):
        if not is_numeric_dtype(df[self.varname]):
            raise ValueError(self._get_data_error_message("Data type must be numeric"))


class CurrencyMeta(Meta):
    def __init__(self, varname, label: str = None, tags: list = None, code = "USD"):
        super().__init__(type=Meta.TYPE_CURRENCY, varname=varname, label=label, tags=tags,
            filterable=True, sortable=True)

        # Ensure that this currency code is valid
        check_enum(code, get_valid_currencies(), self._get_error_message)

        self.code = code

    def check_variable(self, df: pd.DataFrame):
        if not is_numeric_dtype(df[self.varname]):
            raise ValueError(self._get_data_error_message("Data type must be numeric"))


class StringMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None):
        super().__init__(type=Meta.TYPE_STRING, varname=varname, label=label, tags=tags,
            filterable=True, sortable=False)
        
    def check_variable(self, df: pd.DataFrame):
        if not is_string_dtype(df[self.varname]):
            raise ValueError(self._get_data_error_message("Data type is not a string"))

    # TODO: Add a cast variable method?

class FactorMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None, levels: list = None):
        super().__init__(type=Meta.TYPE_FACTOR, varname=varname, label=label, tags=tags,
            filterable=True, sortable=True)
        
        # TODO: Determine how to approach factors in pandas.. Categories?

        self.levels = levels

    def check_variable(self, df: pd.DataFrame):
        # TODO: Implement this to verify the factor levels match
        raise NotImplementedError()
    
    # TODO: Add a cast_variable function? Convert this to a string column?


class DateMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None):
        super().__init__(type=Meta.TYPE_DATE, varname=varname, label=label, tags=tags,
            filterable=True, sortable=True)

    def check_variable(self, df: pd.DataFrame):
        # TODO: Determine approach to dates in pandas. Should they
        # be actual date objects, or should they be strings that
        # are representations of the date

        # TODO: Implement this to verify column is a date
        raise NotImplementedError()


class DatetimeMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None, timezone="UTC"):
        super().__init__(type=Meta.TYPE_DATETIME, varname=varname, label=label, tags=tags,
            filterable=True, sortable=True)
        
        # TODO: Consider validating timezone

        self.timezone = timezone

    def check_variable(self, df: pd.DataFrame):
        # TODO: Determine approach to dates in pandas. Should they
        # be actual date objects, or should they be strings that
        # are representations of the date

        # TODO: Implement this to verify column is a date
        raise NotImplementedError()


class GraphMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None, idvarname: str = None,
                direction: str = "none"):
        super().__init__(type=Meta.TYPE_GRAPH, varname=varname, label=label, tags=tags,
            filterable=True, sortable=False)
        
        check_enum(direction, ("none", "to", "from"), self._get_error_message)

        self.direction = direction
        self.idvarname = idvarname


class GeoMeta(Meta):
    def __init__(self, varname: str, latvar: str, longvar: str, label: str = None, tags: list = None,):
        super().__init__(type=Meta.TYPE_GEO, varname=varname, label=label, tags=tags,
            filterable=True, sortable=False)
        
        self.latvar = latvar
        self.longvar = longvar

        # TODO: Add checks for these variables, to make sure:
        # 1. The variables exist
        # 2. They are valid lat/longs

    def to_dict(self) -> dict:
        # Overriding to make it so latvar and longvar are not serialized
        result = self.__dict__

        result.pop("latvar", None)
        result.pop("longvar", None)

        return result


class HrefMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None):
        super().__init__(type=Meta.TYPE_HREF, varname=varname, label=label, tags=tags,
            filterable=False, sortable=False)
        
    def check_variable(self, df: pd.DataFrame):
        if not is_string_dtype(df[self.varname]):
            raise ValueError(self._get_data_error_message("Data type is not a string"))

    # TODO: Add cast variable?

