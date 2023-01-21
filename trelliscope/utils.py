from datetime import date, datetime
import pandas as pd
from pandas.api.types import is_numeric_dtype

def check_enum(value_to_check, possible_values, get_error_message_function):
    if not value_to_check in possible_values:
        message = get_error_message_function(f"{value_to_check} must be one of {possible_values}")
        raise ValueError(message)
    
def check_is_list(value_to_check, get_error_message_function):
    if not type(value_to_check) == list:
        message = get_error_message_function(f"Expected value '{value_to_check}' to be a list")
        raise ValueError(message)

def check_has_variable(df: pd.DataFrame, varname: str, get_error_message_function):
    if varname not in df.columns:
        raise ValueError(get_error_message_function(f"Could not find variable {varname} is in the list of columns"))

def check_numeric(df: pd.DataFrame, varname: str, get_error_message_function):
    if not is_numeric_dtype(df[varname]):
        raise ValueError(get_error_message_function(f"The variable '{varname}' must be numeric."))

def check_range(df: pd.DataFrame, varname: str, min: float, max: float, get_error_message_function):
    if not df[varname].between(min, max, "both").all():
        raise ValueError(get_error_message_function(f"The variable '{varname}' must be in the range {min} to {max}."))

def check_latitude_variable(df: pd.DataFrame, varname: str, get_error_message_function):
    check_numeric(df, varname, get_error_message_function)
    check_range(df, varname, -90, 90, get_error_message_function)

def check_longitude_variable(df: pd.DataFrame, varname: str, get_error_message_function):
    check_numeric(df, varname, get_error_message_function)
    check_range(df, varname, 0, 180, get_error_message_function)
    

# From: https://stackoverflow.com/a/22238613
def custom_json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type {type(obj)} is not serializable")