from __future__ import annotations

import json
from typing import Any

import pandas as pd

from trelliscope import utils
from trelliscope.panel_source import PanelSource
from trelliscope.panels import Panel


class Meta:
    """
    The base class for all Meta variants.

    The Meta objects describe each variable in the Trelliscope widget and controls
    their filtering, sorting, tags, rounding, etc.
    """

    TYPE_STRING = "string"
    TYPE_PANEL = "panel"
    TYPE_HREF = "href"
    TYPE_FACTOR = "factor"
    TYPE_NUMBER = "number"
    TYPE_DATE = "date"
    TYPE_DATETIME = "datetime"
    TYPE_CURRENCY = "currency"
    TYPE_GRAPH = "graph"
    TYPE_GEO = "geo"

    def __init__(
        self,
        type: str,
        varname: str,
        filterable: bool,
        sortable: bool,
        label: str = None,
        tags: list = None,
    ):
        """

        Args:
            type: Type of the variable, should match one of the class TYPE_* attributes.
            varname: Name of variable
            filterable: Boolean whether variable can be filtered by.
            sortable: Boolean whether variable can be sorted by.
            label: Label of the variable being displayed.
            tags: List of string tags used for categorizing the variable.
        """
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

    def _get_error_message(self, error_text: str) -> str:
        """Returns a generic error message string using the provided text,
        combined with the Meta type and varname.

        Args:
            error_text: The text of the message to include
        """
        return f"While defining a `{self.type}` meta variable for the variable `{self.varname}`: `{error_text}`"

    def _get_data_error_message(self, error_text: str) -> str:
        """Returns a data specific error message string using the provided text,
        combined with the varname.

        Args:
            error_text: str - the text of the message to include
        """
        return f"While checking meta variable definition for variable `{self.varname}` against the data: `{error_text}`"

    def to_dict(self) -> dict[str, Any]:
        """Gets a dictionary containing the attributes of the meta.

        This could be used directly, but if JSON is desired, consider using the
        `to_json` method instead, which calls this one internally.

        Returns:
            A dictionary of this class properties.
        """
        # Default __dict__ behavior is sufficient, because we don't have custom inner types
        result = self.__dict__.copy()

        # We need a label when it gets serialized, so use varname if needed
        if self.label is None:
            result["label"] = self.varname

        return result

    def to_json(self, pretty: bool = True) -> str:
        """Gets a JSON string containing all the attributes of a meta. This
        is used when serializing.

        Args:
            pretty: Boolean whether to dump JSON with indent=2.

        Returns:
            JSON representation of this object.
        """
        indent_value = None

        if pretty:
            indent_value = 2

        return json.dumps(self.to_dict(), indent=indent_value)

    def check_varname(self, df: pd.DataFrame) -> None:
        """Assert that the varname exists as a column in the provided
        pandas DataFrame.

        Args:
            df: The dataframe that should contain the column.

        Raises:
            ValueError: If the varname is not found.
        """
        utils.check_has_variable(df, self.varname, self._get_error_message)

    def check_variable(self, df: pd.DataFrame) -> None:
        """Overridden in sub-classes to contain any variable checks specific
        to that type.

        If the check fails, this should raise an error.

        Params:
            df: he dataframe that to check.
        Raises:
            ValueError: If the check fails.
        """
        pass

    def check_with_data(self, df: pd.DataFrame) -> None:
        """Runs checks of this meta on the ``df``.

        Calls methods to check that the variable exists in the dataframe and any
        additional checks for specific sub classes. If these checks fail,
        this will raise an error.

        Params:
            df: The dataframe to check.
        Raises:
            ValueError: If any of the checks fail.
        """
        self.check_varname(df)
        self.check_variable(df)


class NumberMeta(Meta):
    """A Meta for numeric data.

    A Number Meta is always filterable and sortable.
    """

    def __init__(
        self,
        varname: str,
        label: str = None,
        tags: list = None,
        digits: int = None,
        locale: bool = True,
    ):
        """

        Args:
            varname: Name of variable.
            label: Label of the variable being displayed.
            tags: List of string tags used for categorizing the variable.
            digits: Number of digits to display in the variable.
            locale: Boolean choice whether to use locale for digits (TODO: describe this.)

        Raises:
            ValueError: If ``digits`` is not an integer scalar. Or, if ``locale`` is given but ``digits`` is not.
        """
        super().__init__(
            type=Meta.TYPE_NUMBER,
            varname=varname,
            label=label,
            tags=tags,
            filterable=True,
            sortable=True,
        )

        if digits is not None:
            utils.check_scalar(digits, "digits", self._get_error_message)
            utils.check_int(digits, "digits", self._get_error_message)

        if locale is not None:
            utils.check_scalar(digits, "locale", self._get_error_message)
            utils.check_bool(locale, "locale", self._get_data_error_message)

        self.digits = digits
        self.locale = locale

    def check_variable(self, df: pd.DataFrame):
        """Verifies that the column in the data frame specified by the varname is numeric.

        Args:
            df: Dataframe that should contain a column matching ``self.varname``.

        Raises:
            ValueError: if ``self.varname`` column in the data frame is not numeric.
        """
        utils.check_numeric(df, self.varname, self._get_data_error_message)


class CurrencyMeta(Meta):
    """A Meta for currency data."""

    def __init__(self, varname, label: str = None, tags: list = None, code="USD"):
        super().__init__(
            type=Meta.TYPE_CURRENCY,
            varname=varname,
            label=label,
            tags=tags,
            filterable=True,
            sortable=True,
        )

        if code is not None:
            utils.check_scalar(code, "code", self._get_error_message)

            # Ensure that this currency code is valid
            utils.check_valid_currency(code, self._get_error_message)

        self.code = code

    def check_variable(self, df: pd.DataFrame):
        """
        Verifies that the column in the data frame specified by
        the varname is numeric.
        """
        utils.check_numeric(df, self.varname, self._get_data_error_message)


class StringMeta(Meta):
    """A Meta for string data."""

    def __init__(self, varname: str, label: str = None, tags: list = None):
        super().__init__(
            type=Meta.TYPE_STRING,
            varname=varname,
            label=label,
            tags=tags,
            filterable=True,
            sortable=True,
        )

    def check_variable(self, df: pd.DataFrame):
        """
        Verifies that the column in the data frame is an atomic vector
        (not a nested type). It does not have to be a string, rather
        anything that can easily be coerced to it.
        """
        # This would check that hte datatype is actually a string:
        # utils.check_string_datatype(df, self.varname, self._get_data_error_message)

        utils.check_atomic_vector(df, self.varname, self._get_data_error_message)

    def cast_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts the `self.varname` column in the data frame to be a string type.
        This will change the original data frame.
        Params:
            df: Pandas DataFrame
        Returns:
            The updated Pandas DataFrame
        """
        df[self.varname] = df[self.varname].astype(str)
        return df


class PanelMeta(Meta):
    """A Meta for Panels."""

    def __init__(self, panel: Panel, label: str = None, tags: list = None):
        super().__init__(
            type=Meta.TYPE_PANEL,
            varname=panel.varname,
            label=label,
            tags=tags,
            filterable=False,
            sortable=False,
        )

        utils.check_positive_numeric(
            panel.aspect_ratio, "aspect", self._get_error_message
        )
        self.aspect = panel.aspect_ratio

        if not isinstance(panel.source, PanelSource):
            raise ValueError("`panel_source` must be of type `PanelSource`")

        self.panel_source = panel.source

        utils.check_enum(
            panel.panel_type_str, ["img", "iframe"], self._get_error_message
        )

        self.panel_type = panel.panel_type_str

    def to_dict(self) -> dict:
        result = super().to_dict()

        result["aspect"] = self.aspect

        result.pop(
            "panel_source", None
        )  # remove the reference to the object put in by the default behavior
        result["source"] = self.panel_source.to_dict()

        result.pop(
            "panel_type", None
        )  # remove the reference to the object put in by the default behavior
        # notice this does not have an _ because this is what the JavaScript expects
        result["paneltype"] = self.panel_type

        return result

    def check_variable(self, df: pd.DataFrame):
        """
        Checks that the variable is an appropriate type for panels.
        """
        # TODO: Fill this in
        pass


class FactorMeta(Meta):
    """A meta for a categorical, factor variable."""

    def __init__(
        self, varname: str, label: str = None, tags: list = None, levels: list = None
    ):
        super().__init__(
            type=Meta.TYPE_FACTOR,
            varname=varname,
            label=label,
            tags=tags,
            filterable=True,
            sortable=True,
        )

        if levels is not None:
            utils.check_is_list(levels, self._get_error_message)

        self.levels = levels

    def infer_levels(self, df: pd.DataFrame):
        """
        Infers the factor levels from the dataframe. If the column is
        a category, the category levels will be used directly. If the column
        is not, it will be cast as a category to pull the levels.
        """
        if df[self.varname].dtype != "category":
            df[self.varname] = df[self.varname].astype("category")

        self.levels = df[self.varname].cat.categories.to_list()

        # if df[self.varname].dtype == "category":
        #     self.levels = df[self.varname].cat.categories.to_list()
        # else:
        #     self.levels = df[self.varname].astype("category").cat.categories.to_list()

    def check_variable(self, df: pd.DataFrame):
        """
        Infers the levels for this factor and verifies that the dataframe matches.
        """
        # Infer levels if not provided
        if self.levels is None:
            # TODO: Verify that this is the behavior we want.
            # This seems a little dangerous to change the object in a check function.
            # Could we have them call an infer method instead?
            self.infer_levels(df)

        # Ensure that levels match the data
        utils.check_exhaustive_levels(
            df, self.levels, self.varname, self._get_data_error_message
        )

    def cast_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts the `self.varname` column in the data frame to be a string type.
        This will change the original data frame.
        Params:
            df: Pandas DataFrame
        Returns:
            The updated Pandas DataFrame
        """
        # TODO: This seems we should cast it to a categorical variable
        # rather than just a string. And it seems like this would be a
        # better place to actual infer the levels than the "check_variable"
        # function above.
        raise NotImplementedError()
        df[self.varname] = df[self.varname].astype(str)
        return df


class DateMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None):
        super().__init__(
            type=Meta.TYPE_DATE,
            varname=varname,
            label=label,
            tags=tags,
            filterable=True,
            sortable=True,
        )

    def check_variable(self, df: pd.DataFrame):
        utils.check_datetime(df, self.varname, self._get_data_error_message)


class DatetimeMeta(Meta):
    def __init__(
        self, varname: str, label: str = None, tags: list = None, timezone="UTC"
    ):
        super().__init__(
            type=Meta.TYPE_DATETIME,
            varname=varname,
            label=label,
            tags=tags,
            filterable=True,
            sortable=True,
        )

        # TODO: Consider validating timezone

        self.timezone = timezone

    def check_variable(self, df: pd.DataFrame):
        utils.check_datetime(df, self.varname, self._get_data_error_message)

    def cast_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converts the `self.varname` column in the data frame to be a DateTime type.

        This will change the original data frame.

        Params:
            df: Pandas DataFrame
        Returns:
            The updated Pandas DataFrame
        """
        # Convert the Series to datetime with errors='coerce'
        df[self.varname] = pd.to_datetime(df[self.varname], errors="coerce")

        # Check if every value is a valid date
        are_all_dates = df[self.varname].notna().all()

        if not are_all_dates:
            raise ValueError("Not all values could be coerced into DateTime values.")

        return df


class GraphMeta(Meta):
    def __init__(
        self,
        varname: str,
        label: str = None,
        tags: list = None,
        idvarname: str = None,
        direction: str = "none",
    ):
        super().__init__(
            type=Meta.TYPE_GRAPH,
            varname=varname,
            label=label,
            tags=tags,
            filterable=True,
            sortable=False,
        )

        utils.check_enum(direction, ("none", "to", "from"), self._get_error_message)

        self.direction = direction
        self.idvarname = idvarname

    def check_variable(self, df: pd.DataFrame):
        utils.check_has_variable(df, self.idvarname, self._get_data_error_message)
        utils.check_graph_var(
            df, self.varname, self.idvarname, self._get_data_error_message
        )


class GeoMeta(Meta):
    def __init__(
        self,
        varname: str,
        latvar: str,
        longvar: str,
        label: str = None,
        tags: list = None,
    ):
        super().__init__(
            type=Meta.TYPE_GEO,
            varname=varname,
            label=label,
            tags=tags,
            filterable=True,
            sortable=False,
        )

        self.latvar = latvar
        self.longvar = longvar

    def check_varname(self, df: pd.DataFrame):
        utils.check_has_variable(df, self.latvar, self._get_data_error_message)
        utils.check_has_variable(df, self.longvar, self._get_data_error_message)

    def check_variable(self, df: pd.DataFrame):
        utils.check_latitude_variable(df, self.latvar, self._get_data_error_message)
        utils.check_longitude_variable(df, self.longvar, self._get_data_error_message)

    # TODO: add a cast variable function that converts lat and long into a single var name

    def to_dict(self) -> dict:
        # Overriding to make it so latvar and longvar are not serialized
        result = self.__dict__.copy()

        result.pop("latvar", None)
        result.pop("longvar", None)

        return result


class HrefMeta(Meta):
    def __init__(self, varname: str, label: str = None, tags: list = None):
        super().__init__(
            type=Meta.TYPE_HREF,
            varname=varname,
            label=label,
            tags=tags,
            filterable=False,
            sortable=False,
        )

    def check_variable(self, df: pd.DataFrame):
        if not utils.is_string_column(df[self.varname]):
            raise ValueError(self._get_data_error_message("Data type is not a string"))

    # TODO: Add cast variable?
