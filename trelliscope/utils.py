from datetime import date, datetime

def check_enum(value_to_check, possible_values, get_error_message_function):
    if not value_to_check in possible_values:
        message = get_error_message_function(f"{value_to_check} must be one of {possible_values}")
        raise ValueError(message)
    
def check_is_list(value_to_check, get_error_message_function):
    if not type(value_to_check) == list:
        message = get_error_message_function(f"Expected value '{value_to_check}' to be a list")
        raise ValueError(message)

# From: https://stackoverflow.com/a/22238613
def custom_json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type {type(obj)} is not serializable")