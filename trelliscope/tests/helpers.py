"""
Used for helper functions that are shared across tests.
"""
import json


def compare_json(actual_json: str, expected_json: str):
    """
    Converts the json strings to dictionaries and compares them
    to ignore differences in order or whitespace.
    """
    actual_json_dict = json.loads(actual_json)
    expected_json_dict = json.loads(expected_json)

    assert actual_json == expected_json
