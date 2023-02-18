import re
import os
import json
from datetime import date, datetime
from collections.abc import Iterable
import pandas as pd
from pandas.api.types import is_numeric_dtype

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
    """
    if not type(value_to_check) == list:
        message = get_error_message_function(f"Expected value '{value_to_check}' to be a list")
        raise ValueError(message)

def check_has_variable(df: pd.DataFrame, varname: str, get_error_message_function):
    """
    Verify that the dataframe contains the column.
    Params:
        df: Pandas DataFrame
        varname: The variable name to check
        get_error_message_function: The function to call to get the error message template
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
    """
    if not is_numeric_dtype(df[varname]):
        raise ValueError(get_error_message_function(f"The variable '{varname}' must be numeric."))

def check_range(df: pd.DataFrame, varname: str, min: float, max: float, get_error_message_function):
    """
    Verify that all values in 'varname' column in the dataframe are within this range.
    Params:
        df: Pandas DataFrame
        varname: The column
        min: float - The minimum value of the range (inclusive)
        max: float - The maximum value of the range (inclusive)
        get_error_message_function: The function to call to get the error message template
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
