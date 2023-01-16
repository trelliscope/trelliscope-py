from trelliscope.state import LabelState, SortState, DisplayState, LayoutState
import pytest

import json
# Note, when using json results, we are converting the json to dictionaries
# and comparing those to ignore any differences in order or whitespace

def test_empty_display_state():
    display_state = DisplayState()
    
    actual_json = display_state.to_json(pretty=False)
    expected_json = '{"layout":null,"labels":null,"sort":[],"filter":[]}'
    assert json.loads(actual_json) == json.loads(expected_json)

def test_layout_state_init():
    state = LayoutState(nrow=2, ncol=3, arrange="cols", page=4)

    assert state.nrow == 2
    assert state.ncol == 3
    assert state.arrange == "cols"
    assert state.page == 4

def test_layout_state(iris_df):
    state1 = LayoutState()
    state1.check_with_data(iris_df)

    with pytest.raises(ValueError, match=r"must be one of .+rows"):
        state2 = LayoutState(arrange="stuff")
    
def test_label_state_init():
    pass

def test_label_state(iris_plus_df):
    state = LabelState(["Species", "date"])
    state.check_with_data(iris_plus_df)

    with pytest.raises(ValueError, match=r"variables not found"):
        state2 = LabelState(["Species", "date", "stuff"])
        state2.check_with_data(iris_plus_df)
    