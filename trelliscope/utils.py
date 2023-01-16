def check_enum(value_to_check, possible_values, get_error_message_function):
    if not value_to_check in possible_values:
        message = get_error_message_function(f"{value_to_check} must be one of {possible_values}")
        raise ValueError(message)