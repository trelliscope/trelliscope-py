from trelliscope.state import State, FilterState, LabelState, SortState, DisplayState, LayoutState, CategoryFilterState
from trelliscope.metas import Meta, DateMeta, StringMeta, FactorMeta
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
    state = LabelState(["one", "two"])
    assert type(state.varnames) == list
    assert state.varnames == ["one", "two"]
    

def test_label_state(iris_plus_df):
    state = LabelState(["Species", "date"])
    state.check_with_data(iris_plus_df)

    with pytest.raises(ValueError, match=r"variables not found"):
        state2 = LabelState(["Species", "date", "stuff"])
        state2.check_with_data(iris_plus_df)
    
def test_sort_state_init():
    state = SortState("the var", SortState.DIR_DESCENDING)
    assert state.varname == "the var"
    assert state.dir == SortState.DIR_DESCENDING

def test_sort_state(iris_plus_df):
    state = SortState("date")
    #meta = DateMeta()

    state.check_with_data(iris_plus_df)
    # TODO: Add this check in when DateMeta is finished
    # state.check_with_meta(meta)

    assert state.to_dict() == {"dir":"asc", "varname":"date", "type":"sort"}

    actual_json = state.to_json(pretty=False)
    expected_json = '{"dir":"asc","varname":"date","type":"sort"}'
    assert json.loads(actual_json) == json.loads(expected_json)

    with pytest.raises(ValueError, match=r"not found in the dataset"):
        state2 = SortState("stuff")
        state2.check_with_data(iris_plus_df)

    with pytest.raises(ValueError, match=r"must be one of"):
        state3 = SortState("date", dir="ascc")

def test_category_filter_state_init(iris_plus_df):
    state = CategoryFilterState("the var", "regex_to_find", ["a", "b", "c"])
    assert state.varname == "the var"
    assert state.regexp == "regex_to_find"
    assert state.values == ["a", "b", "c"]
    assert set(state.applies_to) == {Meta.TYPE_STRING, Meta.TYPE_FACTOR}
    assert state.type == State.TYPE_FILTER
    assert state.FILTERTYPE_CATEGORY == FilterState.FILTERTYPE_CATEGORY


def test_category_filter_state(iris_plus_df):
    state = CategoryFilterState("datestring", values="2023-02-24")
    meta1 = StringMeta("datastring")
    
    # TODO: Add in when implemented
    #meta2 = FactorMeta("datastring")
    #meta3 = DateMeta("date")

    state.check_with_data(iris_plus_df)
    state.check_with_meta(meta1)

    # TODO: Add in when implemented
    #state.check_with_meta(meta2)
    # with pytest.raises(ValueError, match=r"is not compatible with this filter"):
    #     state.check_with_meta(meta3)

    actual_dict = state.to_dict()
    assert state.to_dict() == {"values":["2023-02-24"],
                                "regexp":None,
                                "filtertype":"category",
                                "varname":"datestring",
                                "type":"filter"}
    
    actual_json = state.to_json(pretty=False)
    expected_json = '{"values":["2023-02-24"],"regexp":null,"filtertype":"category","varname":"datestring","type":"filter"}'
    assert json.loads(actual_json) == json.loads(expected_json)
    
def test_category_filter_state_bad_values(iris_plus_df):
    state = CategoryFilterState("datestring", values="stuff")
    with pytest.raises(ValueError, match=r"could not find the value"):
        state.check_with_data(iris_plus_df)
    
