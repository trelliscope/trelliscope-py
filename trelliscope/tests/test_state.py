from trelliscope.state import LabelState, SortState, DisplayState, LayoutState

import json
# Note, when using json results, we are converting the json to dictionaries
# and comparing those to ignore any differences in order or whitespace

def test_empty_display_state():
    display_state = DisplayState()
    
    actual_json = display_state.to_json(pretty=False)
    expected_json = '{"layout":null,"labels":null,"sort":[],"filter":[]}'
    assert json.loads(actual_json) == json.loads(expected_json)

def test_layout_state(iris_df):
    layout_state = LayoutState()
    layout_state.check_with_data(iris_df)