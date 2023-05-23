import re
import os
import json
from datetime import date, datetime
from collections.abc import Iterable
import pandas as pd
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_string_dtype
from pandas.api.types import is_object_dtype
from pandas.api.types import infer_dtype
import plotly

from .currencies import get_valid_currencies

def __generic_error_message(text:str):
    """
    This function can be used if a custom error message function is not provided.
    It simply returns the text it was passed.
    """
    return text

def check_int(value_to_check, name:str, get_error_message_function=__generic_error_message):
    """
    Verify that the provided value is an integer. If not, this will raise
    an error.
    Params:
        value_to_check: The value in question.
        name: The variable name for the error message.
        get_error_message_function: The function to call to get the error message template.
    Raises:
        TypeError - If the check fails.
    """
    if not isinstance(value_to_check, int):
        message = get_error_message_function(f"{name} must be an integer.")
        raise TypeError(message)

def check_positive_numeric(value_to_check, name:str, get_error_message_function=__generic_error_message):
    """
    Verify that the provided value is a positive number (int or float). If not, this will raise
    an error.
    Params:
        value_to_check: The value in question.
        name: The variable name for the error message.
        get_error_message_function: The function to call to get the error message template.
    Raises:
        TypeError - If the check fails.
    """
    if (isinstance(value_to_check, int) or isinstance(value_to_check, float)) and value_to_check > 0:
        pass
    else:
        message = get_error_message_function(f"{name} must be a positive number.")
        raise ValueError(message)


def check_int(value_to_check, name:str, get_error_message_function=__generic_error_message):
    """
    Verify that the provided value is an integer. If not, this will raise
    an error.
    Params:
        value_to_check: The value in question.
        name: The variable name for the error message.
        get_error_message_function: The function to call to get the error message template.
    Raises:
        TypeError - If the check fails.
    """
    if not isinstance(value_to_check, int):
        message = get_error_message_function(f"{name} must be an integer.")
        raise TypeError(message)

def check_bool(value_to_check, name:str, get_error_message_function=__generic_error_message):
    """
    Verify that the provided value is a boolean. If not, this will raise
    an error.
    Params:
        value_to_check: The value in question.
        name: The variable name for the error message.
        get_error_message_function: The function to call to get the error message template.
    Raises:
        TypeError - If the check fails.
    """
    if not isinstance(value_to_check, bool):
        message = get_error_message_function(f"{name} must be a boolean value (must be logical).")
        raise TypeError(message)

def check_scalar(value_to_check, name:str, get_error_message_function=__generic_error_message):
    """
    Verify that the provided value is a scalar value, meaning, that it is NOT
    a iterable. Note that for these purposes strings are considered scalars,
    even though they are technically iterable.
    Params:
        value_to_check: The value in question.
        name: The variable name for the error message.
        get_error_message_function: The function to call to get the error message template.
    Raises:
        TypeError - If the check fails.
    """
    if not isinstance(value_to_check, str) and isinstance(value_to_check, Iterable):
        message = get_error_message_function(f"{name} must be a scalar (not a list or other iterable type).")
        raise TypeError(message)

def check_enum(value_to_check, possible_values, get_error_message_function=__generic_error_message):
    """
    Verify that the provided value is in a list of possible values.
    Params:
        value_to_check: The value in question
        possible_values: An iterable list of values
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    if not value_to_check in possible_values:
        message = get_error_message_function(f"{value_to_check} must be one of {possible_values}")
        raise ValueError(message)
    
def check_is_list(value_to_check, get_error_message_function):
    """
    Verify that the provided value is a list.
    Params:
        value_to_check: The value in question
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    if not isinstance(value_to_check, list):
        message = get_error_message_function(f"Expected value '{value_to_check}' to be a list")
        raise ValueError(message)

def check_has_variable(df: pd.DataFrame, varname: str, get_error_message_function):
    """
    Verify that the dataframe contains the column.
    Params:
        df: Pandas DataFrame
        varname: The variable name to check
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    if varname not in df.columns:
        raise ValueError(get_error_message_function(f"Could not find variable {varname} is in the list of columns"))

def check_numeric(df: pd.DataFrame, varname: str, get_error_message_function):
    """
    Verify that in the dataframe, the column 'varname' is numeric.
    Params:
        df: Pandas DataFrame
        varname: The variable name to check
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    if not is_numeric_dtype(df[varname]):
        raise ValueError(get_error_message_function(f"The variable '{varname}' must be numeric."))


def check_string_datatype(df: pd.DataFrame, varname: str, get_error_message_function=__generic_error_message):
    """
    Verify that in the dataframe, the column 'varname' is a string datatype.
    Params:
        df: Pandas DataFrame
        varname: The variable name to check
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    if not is_string_column(df[varname]):
        raise ValueError(get_error_message_function(f"The variable '{varname}' is not a string."))

def check_atomic_vector(df: pd.DataFrame, varname: str, get_error_message_function=__generic_error_message):
    """
    Verify that in the dataframe, the column 'varname' is an atomic vector, or
    in other words, not a nested type.
    Params:
        df: Pandas DataFrame
        varname: The variable name to check
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    if infer_dtype(df[varname]) == "mixed":
        raise ValueError(get_error_message_function(f"The variable '{varname}' is must be an atomic vector (not a nested type)."))

def check_valid_currency(value_to_check: str, get_error_message_function):
    """
    Verify that the provided currency is a valid one (e.g., USD, EUR).
    Params:
        value_to_check: the value in question.
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    check_enum(value_to_check, get_valid_currencies(), get_error_message_function)

def check_range(df: pd.DataFrame, varname: str, min: float, max: float, get_error_message_function):
    """
    Verify that all values in 'varname' column in the dataframe are within this range.
    Params:
        df: Pandas DataFrame
        varname: The column
        min: float - The minimum value of the range (inclusive)
        max: float - The maximum value of the range (inclusive)
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    if not df[varname].between(min, max, "both").all():
        raise ValueError(get_error_message_function(f"The variable '{varname}' must be in the range {min} to {max}."))

def check_latitude_variable(df: pd.DataFrame, varname: str, get_error_message_function):
    """
    Verify that the latitude variable is numeric and in the proper range.
    Params:
        df: Pandas DataFrame
        varname: The latitude column
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    check_numeric(df, varname, get_error_message_function)
    check_range(df, varname, -90, 90, get_error_message_function)

def check_longitude_variable(df: pd.DataFrame, varname: str, get_error_message_function):
    """
    Verify that the longitude variable is numeric and in the proper range.
    Params:
        df: Pandas DataFrame
        varname: The longitude column
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    check_numeric(df, varname, get_error_message_function)
    check_range(df, varname, 0, 180, get_error_message_function)
    

# From: https://stackoverflow.com/a/22238613
def custom_json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type {type(obj)} is not serializable")

def check_exhaustive_levels(df: pd.DataFrame, levels: list, varname: str, get_error_message_function):
    """
    Verifies that the values in the `varname` column contains only those values specified
    in `levels`. If any extras are found, an error is raised.
    Params:
        df: Pandas DataFrame
        levels: list - The possible values
        varname: The column to check
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    actual_values = set(df[varname].unique())
    expected_values = set(levels)

    diff = actual_values - expected_values

    if len(diff) > 0:
        raise ValueError(get_error_message_function(f"{varname} contains values not specified in levels:{levels}"))

def check_graph_var(df: pd.DataFrame, varname: str, id_varname: str, get_error_message_function):
    """
    """
    # TODO: After we have determined how to handle the graph data in Pandas,
    # implement this method to verify it.

    raise NotImplementedError()

valid_image_extensions = {"apng", "avif", "gif", "jpg", "jpeg", "jfif", "pjpeg",
  "pjp", "png", "svg", "webp"}

def _extension_matches(text:str, ext_to_match:str, match_case:bool = False):
    """
    Returns true if the extension of `text` matches the provided
    `ext_to_match`.

    Params:
        text: str - The filepath
        ext_to_match: str - The extension not including the . (pass "jpg" not ".jpg")

    Designed to be used as a "lambda" function in an apply method.
    """
    (_, ext) = os.path.splitext(text)

    # Get rid of the leading . in .jpg
    ext = ext.removeprefix(".")

    is_match = False

    if match_case:
        is_match = (ext == ext_to_match)
    else:
        is_match = (ext.lower() == ext_to_match.lower())

    return is_match

def find_figure_columns(df:pd.DataFrame):
    """
    Finds a list of columns in the dataframe that are completely filled with
    `Figure` objects.
    """

    # SB: This function (and its unit tests)  place a dependency on plotly,
    # because they check for plotly figure object. If this is not desired,
    # another approach could be used such as checking for a "facel_panel"
    # column name or something similar.

    figure_cols = []
    obj_cols = [col for col in df.columns if is_object_dtype(df[col])]

    for col in obj_cols:
        if isinstance(df[col][0], plotly.graph_objs.Figure):
            # The first row is a Figure, check all now
            if df[col].apply(lambda x: isinstance(x, plotly.graph_objs.Figure)).all():
                figure_cols.append(col)
    
    return figure_cols

def find_image_columns(df:pd.DataFrame):
    """
    Finds a list of columns in the dataframe that are completely filled with
    image references.
    """
    image_cols = []
    str_cols = [col for col in df.columns if is_string_column(df[col])]

    for col in str_cols:
        # Get the extension of the first item
        (_, ext) = os.path.splitext(df[col][0])

        # Get rid of the leading . in .jpg
        ext = ext.removeprefix(".")

        if ext in valid_image_extensions:
            # The first row had a valid image extension, now check if
            # they all have this same extension
            if df[col].apply(lambda x: _extension_matches(x, ext)).all():
                # All rows in this column have this extension
                image_cols.append(col)

    return image_cols

def check_image_extension(list_to_check:list, get_error_message_function=__generic_error_message):
    """
    Verify that each element in the list has a valid image extension.
    Params:
        list_to_check: The list of strings.
        get_error_message_function: The function to call to get the error message template
    Raises:
        ValueError - If the check fails.
    """
    for item in list_to_check:
        filename, ext = os.path.splitext(item)
        
        # Get rid of the leading . in .jpg
        ext = ext.removeprefix(".")
        
        if ext not in valid_image_extensions:
            # Found invalid file extension
            message = get_error_message_function(f"Extension {ext} is not valid. All file extensions must be one of: {valid_image_extensions}")
            raise ValueError(message)

def is_all_remote(col:pd.Series):
    """
    Determines if every value in the provided `col` column is
    remote, meaning that they all begin with `http:`.
    """
    return col.apply(lambda x: x.startswith("http")).all()

def sanitize(text:str, to_lower=True) -> str:
    if to_lower:
        text = text.lower()
    
    text = text.replace(" ", "_")
    text = re.sub(r"[^\w]", "", text)

    return text

def get_jsonp_wrap_text_dict(jsonp: bool, function_name: str) -> dict():
    """
    Gets the starting and ending text to use for the config file.
    If it is jsonp, it will have a function name and ()'s. If it is
    not (ie, regular json), it will have empty strings.
    """
    text_dict = {}
    if jsonp:
        text_dict["start"] = f"{function_name}("
        text_dict["end"] = ")"
    else:
        text_dict["start"] = ""
        text_dict["end"] = ""

    return text_dict

def write_json_file(file_path: str, jsonp: bool, function_name: str, content: str):
    wrap_text_dict = get_jsonp_wrap_text_dict(jsonp, function_name)
    wrapped_content = wrap_text_dict["start"] + content + wrap_text_dict["end"]

    with open(file_path, "w") as output_file:
        output_file.write(wrapped_content)

def get_file_path(directory: str, filename_no_ext: str, jsonp: bool):
    file_ext = "jsonp" if jsonp else "json"
    filename = f"{filename_no_ext}.{file_ext}"

    file_path = os.path.join(directory, filename)

    return file_path

def read_jsonp(file: str) -> dict():
    """
    Reads the json content of the .json or .jsonp file. If the file is
    a .jsonp file, the function name and ()'s will be ignored.
    Params:
        file: str - The full path to the file.
    Returns:
        dict - The content of the .json or .jsonp file.
    """
    content = ""
    with open(file) as file_handle:
        content = file_handle.read()

    json_content = ""

    if file.endswith(".json"):
        json_content = content
    elif file.endswith(".jsonp"):
        open_paren_index = content.index("(")
        close_paren_index = content.rindex(")")
        json_content = content[open_paren_index + 1 : close_paren_index]
    else:
        raise ValueError(f"Unrecognized file extension for file {file}. Expected .json or .jsonp")

    result = json.loads(json_content)
    return result

def is_dataframe_grouped(df: pd.DataFrame) -> bool:
    index_names = df.index.names
    
    is_empty_index = len(index_names) == 1 and index_names[0] is None
    return not is_empty_index

def get_dataframe_grouped_columns(df: pd.DataFrame) -> list:
    return df.index.names

def get_string_columns(df: pd.DataFrame) -> list:
    char_cols = [c for c in df.columns if is_string_column(df[c])]
    return char_cols

def get_string_or_factor_columns(df: pd.DataFrame) -> list:
    char_cols = [c for c in df.columns if is_string_column(df[c]) or df[c].dtype == "category"]
    return char_cols

def get_numeric_columns(df: pd.DataFrame) -> list:
    return list(df.select_dtypes('number'))

def get_uniquely_identifying_cols(df: pd.DataFrame) -> list:
    unique_key_cols = []
    
    # Try all columns, beginning with characters
    char_cols = get_string_columns(df)
    numeric_cols = get_numeric_columns(df)
    all_cols = char_cols + numeric_cols

    key_cols = []

    for col in all_cols:
        key_cols.append(col)

        if df.set_index(key_cols).index.is_unique:
            # This set of key_cols uniquely identifies the rows
            unique_key_cols = key_cols
            break

    return unique_key_cols

def is_string_column(column: pd.Series):
    """
    Checks to see if the provided column (Pandas Series) is a string datatype,
    including checking that it is not a Figure object.
    """
    is_string = False

    if is_string_dtype(column):
        # This is a "string dtype" but that could include other types of
        # objects such as a plotly `Figure`, so verify that the first value
        # is actually a string.
        if type(column[0]) == str:
            is_string = True

    return is_string