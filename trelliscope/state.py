import json
import pandas as pd
import logging
from collections import OrderedDict

from .metas import Meta
                
class State():
    """
    Base class for the various state classes.
    """
    TYPE_LAYOUT = "layout"
    TYPE_LABELS = "labels"
    TYPE_SORT = "sort"
    TYPE_FILTER = "filter"

    def __init__(self, type : str):
        self.type = type

    def to_dict(self) -> dict:
        # Default __dict__ behavior is sufficient, because we don't have custom inner types
        return self.__dict__

    def to_json(self, pretty: bool = True):
        indent_value = None

        if pretty:
            indent_value = 2

        return json.dumps(self.to_dict(), indent=indent_value)

    def check_with_data(self, df : pd.DataFrame):
        """
        Ensure that the state is consistent with this dataset.

        This function should be overridden by subclasses to do any
        state specific checks that need to be done.
        """
        return True

    def _get_error_message(self, text):
        return f"While checking a {self.type} state definition: {text}"
    
    def _get_data_error_message(self, text):
        return f"While checking {self.type} state definition against the data: {text}"

class LayoutState(State):
    def __init__(self, nrow : int = 1, ncol : int = 1, arrange : str = "rows", page : int = 1):
        super().__init__(State.TYPE_LAYOUT)

        self.nrow = nrow
        self.ncol = ncol
        self.arrange = arrange
        self.page = page

    def check_with_data(self, df: pd.DataFrame):
      # This comment is in the R version:
      # TODO: could check to see if "page" makes sense after applying filters
      # and accounting for nrow and ncol
      return True

class LabelState(State):
    def __init__(self, varnames : list = []):
        super().__init__(State.TYPE_LABELS)

        self.varnames = varnames

class SortState(State):
    DIR_ASCENDING = "asc"
    DIR_DESCENDING = "desc"

    def __init__(self, varname : str, dir : str = DIR_ASCENDING):
        super().__init__(State.TYPE_SORT)

        if dir not in [SortState.DIR_ASCENDING, SortState.DIR_DESCENDING]:
            raise ValueError(self._get_error_message(f"Sort direction is not valid. Must be '{SortState.DIR_ASCENDING}' or '{SortState.DIR_DESCENDING}'."))

        self.varname = varname
        self.dir = dir

    def check_with_data(self, df : pd.DataFrame):
        if self.varname not in df.columns:
            raise ValueError(f"'{self.varname}' not found in the dataset that the {self.type} state definition is being applied to.")

    def check_with_meta(self, meta : Meta):
        if not meta.sortable:
            raise ValueError(self._get_error_message(f"'{self.varname}' is not sortable"))

class FilterState(State):
    FILTERTYPE_CATEGORY = "category"
    FILTERTYPE_NUMBER_RANGE = "numberrange"
    FILTERTYPE_DATE_RANGE = "daterange"
    FILTERTYPE_DATETIME_RANGE = "datetimerange"

    def __init__(self, varname : str, filtertype : str, applies_to : list = None):
        """
        Params:
            varname: Variable Name
            filtertype: Type of Filter (see available constants)
            applies_to: List of meta types. None indicates this applies to all meta definitions.
        """
        super().__init__(State.TYPE_FILTER)

        # TODO: Add a check to make sure filter type is in the valid list

        self.varname = varname
        self.filtertype = filtertype
        self.applies_to = applies_to

    def check_with_data(self, df : pd.DataFrame):
        if self.varname not in df.columns:
            raise ValueError(f"'{self.varname}' not found in the dataset that the {self.type} state definition is being applied to.")

    def check_with_meta(self, meta : Meta):
        if meta.type not in self.applies_to:
            raise ValueError(self._get_error_message(f"the meta type applied to variable '{self.varname}' is not compatible with this filter"))
        
class CategoryFilterState(FilterState):
    def __init__(self, varname : str, regexp : str = None, values : list = None):
        super().__init__(varname=varname,
            filtertype=FilterState.FILTERTYPE_CATEGORY,
            applies_to=[Meta.TYPE_STRING, Meta.TYPE_FACTOR])
        
        self.regexp = regexp
        self.values = values

    def check_with_data(self, df: pd.DataFrame):
        super().check_with_data(df)

        diff = set(self.values) - set(df.columns)
        if len(diff) > 0:
            raise ValueError(self._get_error_message(f"could not find the value(s): {diff} in the variable '{self.varname}'"))

class RangeFilterState(FilterState):
    def __init__(self, varname : str, filtertype : str, applies_to : list, min : int = None, max : int = None):
        super().__init__(varname=varname, filtertype=filtertype, applies_to=applies_to)
        
        self.min = min
        self.max = max

class NumberRangeFilterState(RangeFilterState):
    def __init__(self, varname : str, min : int = None, max : int = None):
        super().__init__(varname=varname,
            filtertype=FilterState.FILTERTYPE_NUMBER_RANGE,
            applies_to=Meta.TYPE_NUMBER,
            min=min,
            max=max)
        
class DateRangeFilterState(RangeFilterState):
    def __init__(self, varname : str, min : int = None, max : int = None):
        super().__init__(varname=varname,
            filtertype=FilterState.FILTERTYPE_DATE_RANGE,
            applies_to=Meta.TYPE_DATE,
            min=min,
            max=max)

class DatetimeRangeFilterState(RangeFilterState):
    def __init__(self, varname : str, min : int = None, max : int = None):
        super().__init__(varname=varname,
            filtertype=FilterState.FILTERTYPE_DATETIME_RANGE,
            applies_to=Meta.TYPE_DATETIME,
            min=min,
            max=max)

class DisplayState():
    """
    Contains the collection of all states necessary to define a display.
    """
    def __init__(self):
        self.layout = None
        self.labels = None
        self.sort = OrderedDict()
        self.filter = OrderedDict()

        # TODO: Verify that serialization of the sort/filter states matches expected
        # output. It may want a list rather than a dict.

    def set(self, state : State, add : bool = False):
        """
        Sets the provided state. Overwriting the existing one of that type unless
        add=True, then it appends it.
        """

        # TODO: Decide if we want this convenience method or if we want to force
        # users to simply set the specific type directly

        if isinstance(state, LayoutState):
            if self.layout is not None:
                logging.info("Replacing existing layout state specification")
            self.layout = state
        elif isinstance(state, LabelState):
            if self.labels is not None:
                logging.info("Replacing existing labels state specification")
            self.labels = state
        elif isinstance(state, SortState):
            varname = state.varname

            if add:
                if varname in self.sort:
                    logging.info(f"Replacing existing sort state specification for variable {varname}")

                self.sort[varname] = state

                # Move to the end to preserve correct sort order
                self.sort.move_to_end(varname)

            else: # not add. Instead replace.
                logging.info("Replacing entire existing sort state specification")
                self.sort = OrderedDict()
                self.sort[varname] = state
        elif isinstance(state, FilterState):
            varname = state.varname

            if add:
                if varname in self.filter:
                    logging.info(f"Replacing existing filter state specification for variable {varname}")

                self.filter[varname] = state

                # Move to the end to preserve correct sort order
                self.filter.move_to_end(varname)

            else: # not add. Instead replace.
                logging.info("Replacing entire existing filter state specification")
                self.filter = OrderedDict()
                self.filter[varname] = state

    def to_dict(self) -> dict:
        result = {}

        layout_dict = None
        label_dict = None

        if self.layout is not None:
            layout_dict = self.layout.to_dict()

        if self.labels is not None:
            label_dict = self.labels.to_dict()

        # Sort and filter are stored internally as Ordered dictionaries
        # but for the output, we need to strip off the keys
        sort_list = [v.to_dict() for v in self.sort.values()]
        filter_list = [v.to_dict() for v in self.filter.values()]

        result["layout"] = layout_dict
        result["labels"] = label_dict
        result["sort"] = sort_list
        result["filter"] = filter_list

        return result

    def to_json(self, pretty: bool = True) -> str:
        indent_value = None

        if pretty:
            indent_value = 2

        dict_to_serialize = self.to_dict()

        return json.dumps(dict_to_serialize, indent=indent_value)
