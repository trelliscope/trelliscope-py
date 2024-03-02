"""State definitions for Trelliscope.

The State of a Trelliscope includes a Layout, the Labels displayed underneath panels, Sorting options and
applied Filters. The State controls the initial state the Trelliscope display opens in.
"""
from __future__ import annotations

import copy
import json
import logging
from collections import OrderedDict
from datetime import date, datetime
from typing import Literal

import pandas as pd

from trelliscope import utils
from trelliscope.metas import Meta


class State:
    """Base class for the various state classes."""

    TYPE_LAYOUT = "layout"
    TYPE_LABELS = "labels"
    TYPE_SORT = "sort"
    TYPE_FILTER = "filter"

    def __init__(self, type: str):
        """Create a new State for a given type.

        Args:
           type: Type of the State, one of ['layout', 'labels', 'sort', 'filter'].
        """
        self.type = type

        # Waiting to check the type until after setting
        # the member variable, otherwise, the get error message
        # function will have an error
        utils.check_enum(
            type,
            (State.TYPE_LAYOUT, State.TYPE_LABELS, State.TYPE_SORT, State.TYPE_FILTER),
            self._get_error_message,
        )

    def to_dict(self) -> dict:
        """Returns a dictionary that can be serialized to json."""
        result = self.__dict__.copy()

        # Remove any unwanted items
        result.pop("applies_to", None)

        return result

    def to_json(self, pretty: bool = True):
        """Returns a json version of this object that can be saved to output."""
        indent_value = None

        if pretty:
            indent_value = 2

        return json.dumps(
            self.to_dict(), default=utils.custom_json_serializer, indent=indent_value
        )

    def check_with_data(self, df: pd.DataFrame):
        """Ensure that the state is consistent with this dataset.

        This function should be overridden by subclasses to do any
        state specific checks that need to be done.
        """
        return True

    def _get_error_message(self, text):
        return f"While checking a {self.type} state definition: {text}"

    def _get_data_error_message(self, text):
        return f"While checking {self.type} state definition against the data: {text}"

    def _copy(self):
        # TODO: Shallow or deep copy??
        return copy.deepcopy(self)


class LayoutState(State):
    """State definition for Layout of trelliscope display."""

    VIEWTYPE_GRID = "grid"

    def __init__(self, ncol: int = 1, page: int = 1):
        """Create Layout state.

        Args:
            ncol: Number of columns in a single page to show.
            page: Initial page number to open on.
        """
        super().__init__(State.TYPE_LAYOUT)

        utils.check_int(ncol, "ncol")
        utils.check_int(page, "page")

        self.ncol = ncol
        self.page = page
        self.viewtype = LayoutState.VIEWTYPE_GRID

    def check_with_data(self, df: pd.DataFrame) -> bool:
        """Check if layout data is valid given the data.

        Args:
            df: Dataframe to check for this layout.

        Returns:
            Boolean indicating if data is valid. Currently, always `True`.
        """
        # This comment is in the R version:
        # TODO: could check to see if "page" makes sense after applying filters
        # and accounting for nrow and ncol
        return True


class LabelState(State):
    """State of shown panel labels."""

    def __init__(self, varnames: list = []):
        """Create Label state.

        Args:
            varnames: List of variables to display as labels.
        """
        super().__init__(State.TYPE_LABELS)

        utils.check_is_list(varnames, self._get_data_error_message)
        self.varnames = varnames

    def check_with_data(self, df: pd.DataFrame) -> bool:
        """Check if `varnames` are all columns of the provided data.

        Args:
            df: Dataframe that should contain columns matching `varnames`.

        Returns:
            True if all `varnames` are columns in the dataframe.

        Raises:
            ValueError: if any of the `varnames` are not a column in the dataframe.
        """
        extra_columns = set(self.varnames) - set(df.columns)
        if len(extra_columns) > 0:
            raise ValueError(
                self._get_data_error_message(
                    f"Label variables not found in data: {extra_columns}"
                )
            )

        return True


class SortState(State):
    """State of panel sorting."""

    DIR_ASCENDING = "asc"
    DIR_DESCENDING = "desc"

    def __init__(
        self,
        varname: str,
        dir: Literal["asc", "desc"] = DIR_ASCENDING,
        meta_type: str = None,
    ):
        """Create Sort state.

        Args:
            varname: str - The variable name
            dir: str ("asc" or "desc") - The direction of the sort

        Args:
            varname: The variable name to sort by.
            dir: The direction to sort, one of ['asc', 'desc'].
            meta_type: Optional meta type. (TODO: Should this be a `Meta` type or indeed a string?).
        """
        super().__init__(State.TYPE_SORT)

        utils.check_enum(
            dir,
            (SortState.DIR_ASCENDING, SortState.DIR_DESCENDING),
            self._get_error_message,
        )

        self.varname = varname
        self.dir = dir
        self.metatype = meta_type

    def check_with_data(self, df: pd.DataFrame) -> bool:
        """Check if `varname` exists as a column in the dataframe. Raise an error otherwise."""
        super().check_with_data(df)
        if self.varname not in df.columns:
            raise ValueError(
                self._get_data_error_message(
                    f"'{self.varname}' not found in the dataset that the {self.type} state definition is being applied to."
                )
            )

        return True

    def check_with_meta(self, meta: Meta):
        """Check if the passed Meta is sortable."""
        if not meta.sortable:
            raise ValueError(
                self._get_error_message(f"'{self.varname}' is not sortable")
            )

        return True


class FilterState(State):
    """State of filters applied to panels and their attributes."""

    FILTERTYPE_CATEGORY = "category"
    FILTERTYPE_NUMBER_RANGE = "numberrange"
    FILTERTYPE_DATE_RANGE = "daterange"
    FILTERTYPE_DATETIME_RANGE = "datetimerange"

    def __init__(
        self,
        varname: str,
        filtertype: Literal["category", "numberrange", "daterange", "datetimerange"],
        applies_to: list[Meta] = None,
        meta_type: str = None,
    ):
        """Create Filter state.

        Args:
            varname: Variable name to filter.
            filtertype: Type of filter, one of .
            applies_to: List of Meta types this filter state applies to.
            meta_type: Meta type. (TODO: explain.)
        """
        super().__init__(State.TYPE_FILTER)

        utils.check_enum(
            filtertype,
            (
                FilterState.FILTERTYPE_CATEGORY,
                FilterState.FILTERTYPE_NUMBER_RANGE,
                FilterState.FILTERTYPE_DATE_RANGE,
                FilterState.FILTERTYPE_DATETIME_RANGE,
            ),
            self._get_error_message,
        )

        utils.check_is_list(applies_to, self._get_error_message)

        self.varname = varname
        self.filtertype = filtertype
        self.applies_to = applies_to
        self.metatype = meta_type

    def check_with_data(self, df: pd.DataFrame) -> bool:
        """Check if `varname` is a column in the dataframe.

        Args:
            df: Data that should contain the column matching `varname`.

        Raises:
            ValueError: If dataframe does not contain the expected `varname` column.
        """
        super().check_with_data(df)
        if self.varname not in df.columns:
            raise ValueError(
                self._get_data_error_message(
                    f"'{self.varname}' not found in the dataset that the {self.type} state definition is being applied to."
                )
            )

        return True

    def check_with_meta(self, meta: Meta) -> bool:
        """Check if the provided Meta is valid for this filter state.

        Args:
            meta: The Meta object to check.

        Raises:
            ValueError: If the provided Meta is not in the list of metas in `applies_to`.
        """
        if meta.type not in self.applies_to:
            raise ValueError(
                self._get_error_message(
                    f"the meta type applied to variable '{self.varname}' is not compatible with this filter"
                )
            )

        return True


class CategoryFilterState(FilterState):
    """State for filtering category/factor data types."""

    def __init__(
        self, varname: str, regexp: str = None, values: str | list[str] = None
    ):
        """Create filter state for a category/factor variable.

        Args:
            varname: The variable this filter applies to.
            regexp: Regular expression to apply
            values: Either a string for the value or a list of possible values
        """
        super().__init__(
            varname=varname,
            filtertype=FilterState.FILTERTYPE_CATEGORY,
            applies_to=[Meta.TYPE_STRING, Meta.TYPE_FACTOR],
        )

        self.regexp = regexp

        # TODO: Verify that this should work for a list and a single value
        # The R unit test indicates that it should
        if isinstance(values, str):
            self.values = [values]
        else:
            self.values = values

    def check_with_data(self, df: pd.DataFrame):
        """Check if the filter is valid for the provided dataframe.

        Args:
            df: The dataframe to check.

        Raises:
            ValueError: if any of the filter `values` are not in the
                dataframe column matching `varname`.
        """
        super().check_with_data(df)

        diff = set(self.values) - set(df[self.varname].unique())
        if len(diff) > 0:
            raise ValueError(
                self._get_data_error_message(
                    f"could not find the value(s): {diff} in the variable '{self.varname}'"
                )
            )


class RangeFilterState(FilterState):
    """Base filter state for a range filter."""

    def __init__(
        self,
        varname: str,
        filtertype: str,
        applies_to: list,
        min: int | datetime = None,
        max: int | datetime = None,
    ):
        """Create base filter state that filters on a variable in a min/max range.

        This base class init function should likely only be called by
        subclass init functions.

        Args:
            varname: The variable name
            filtertype: The filter type
            applies_to: List of meta types. None indicates this applies to all meta definitions.
            min: The minimum value for the range
            max: The maximum value for the range
        """
        super().__init__(varname=varname, filtertype=filtertype, applies_to=applies_to)

        self.min = min
        self.max = max


class NumberRangeFilterState(RangeFilterState):
    """Range filter state for numeric variable."""

    def __init__(self, varname: str, min: int = None, max: int = None):
        """Create filter state for a range filter applied to a numeric variable.

        Args:
            varname: The variable name to apply filter to.
            min: Minimum value for the range.
            max: Maximum value for the range.
        """
        super().__init__(
            varname=varname,
            filtertype=FilterState.FILTERTYPE_NUMBER_RANGE,
            applies_to=[Meta.TYPE_NUMBER],
            min=min,
            max=max,
        )

        self.metatype = Meta.TYPE_NUMBER


class DateRangeFilterState(RangeFilterState):
    """Range filter state for date-type variables."""

    def __init__(self, varname: str, min: date = None, max: date = None):
        """Create a range filter state applies to a date-type variable.

        Args:
            varname: The variable name to apply filter to,
            min: Minimum date.
            max: Maximum date.
        """
        super().__init__(
            varname=varname,
            filtertype=FilterState.FILTERTYPE_DATE_RANGE,
            applies_to=[Meta.TYPE_DATE],
            min=min,
            max=max,
        )

        self.metatype = Meta.TYPE_DATE


class DatetimeRangeFilterState(RangeFilterState):
    """Range filter state for datetime-type variables."""

    def __init__(self, varname: str, min: datetime = None, max: datetime = None):
        """Create a range filter state applies to a datetime-type variable.

        Args:
            varname: The variable name to apply filter to,
            min: Minimum datetime.
            max: Maximum datetime.
        """
        super().__init__(
            varname=varname,
            filtertype=FilterState.FILTERTYPE_DATETIME_RANGE,
            applies_to=[Meta.TYPE_DATETIME],
            min=min,
            max=max,
        )

        self.metatype = Meta.TYPE_DATETIME


class DisplayState:
    """Contains the collection of all states necessary to define a display."""

    def __init__(self):
        """Create default display state.

        Display state is further customized using the :meth:`set` method.
        """
        self.layout = None
        self.labels = None
        self.sort = OrderedDict()
        self.filter = OrderedDict()

        # TODO: Verify that serialization of the sort/filter states matches expected
        # output. It may want a list rather than a dict.

    def set(self, state: State, add: bool = False) -> None:
        """Sets the provided state, either overwriting or adding to the current state.

        Updates the object in-place and does not return a value.

        Args:
            state: New state to set.
            add: Whether to add the provided State, or to overwrite the State if
                a State of the same type already exists.
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
                    logging.info(
                        f"Replacing existing sort state specification for variable {varname}"
                    )

                self.sort[varname] = state

                # Move to the end to preserve correct sort order
                self.sort.move_to_end(varname)

            else:  # not add. Instead replace.
                logging.info("Replacing entire existing sort state specification")
                self.sort = OrderedDict()
                self.sort[varname] = state
        elif isinstance(state, FilterState):
            varname = state.varname

            if add:
                if varname in self.filter:
                    logging.info(
                        f"Replacing existing filter state specification for variable {varname}"
                    )

                self.filter[varname] = state

                # Move to the end to preserve correct sort order
                self.filter.move_to_end(varname)

            else:  # not add. Instead replace.
                logging.info("Replacing entire existing filter state specification")
                self.filter = OrderedDict()
                self.filter[varname] = state

    def to_dict(self) -> dict:
        """Returns a dictionary that can be serialized to json."""
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
        """Returns a json version of this object that can be saved to output."""
        indent_value = None

        if pretty:
            indent_value = 2

        dict_to_serialize = self.to_dict()

        return json.dumps(
            dict_to_serialize, indent=indent_value, default=utils.custom_json_serializer
        )

    def _copy(self):
        # TODO: Shallow or deep copy??
        return copy.deepcopy(self)
