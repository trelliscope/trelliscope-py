import json
from datetime import date, datetime

import pytest

from trelliscope.metas import (
    DateMeta,
    DatetimeMeta,
    FactorMeta,
    Meta,
    NumberMeta,
    StringMeta,
)
from trelliscope.state import (
    CategoryFilterState,
    DateRangeFilterState,
    DatetimeRangeFilterState,
    DisplayState,
    FilterState,
    LabelState,
    LayoutState,
    NumberRangeFilterState,
    SortState,
    State,
)

# Note, when using json results, we are converting the json to dictionaries
# and comparing those to ignore any differences in order or whitespace


def test_empty_display_state():
    display_state = DisplayState()

    actual_json = display_state.to_json(pretty=False)
    expected_json = '{"layout":null,"labels":null,"sort":[],"filter":[]}'
    assert json.loads(actual_json) == json.loads(expected_json)


def test_state_bad_values():
    with pytest.raises(ValueError):
        state = State("bad type")


def test_layout_state_init():
    state = LayoutState(ncol=3, page=4)

    assert state.ncol == 3
    assert state.page == 4
    assert state.type == State.TYPE_LAYOUT
    assert state.viewtype == LayoutState.VIEWTYPE_GRID


def test_layout_state(iris_df):
    state1 = LayoutState()
    state1.check_with_data(iris_df)

    with pytest.raises(TypeError, match=r"must be an integer"):
        state2 = LayoutState(ncol="a")

    # with pytest.raises(ValueError, match=r"must be one of .+rows"):
    #     state2 = LayoutState(arrange="stuff")


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


def test_label_state_bad_values():
    with pytest.raises(ValueError, match=r"Expected value .* to be a list"):
        state = LabelState("Species")


def test_sort_state_init():
    state = SortState("the var", SortState.DIR_DESCENDING)
    assert state.varname == "the var"
    assert state.dir == SortState.DIR_DESCENDING


def test_sort_state(iris_plus_df):
    state = SortState("date")
    meta = DateMeta("date")

    state.check_with_data(iris_plus_df)
    state.check_with_meta(meta)

    assert state.to_dict() == {
        "metatype": None,
        "dir": "asc",
        "varname": "date",
        "type": "sort",
    }

    actual_json = state.to_json(pretty=False)
    expected_json = '{"metatype":null,"dir":"asc","varname":"date","type":"sort"}'
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
    assert state.filtertype == FilterState.FILTERTYPE_CATEGORY


def test_category_filter_state(iris_plus_df):
    state = CategoryFilterState("datestring", values="2023-02-24")
    meta1 = StringMeta("datestring")

    meta2 = FactorMeta("datestring")
    meta3 = DateMeta("date")

    state.check_with_data(iris_plus_df)
    state.check_with_meta(meta1)

    state.check_with_meta(meta2)
    with pytest.raises(ValueError, match=r"is not compatible with this filter"):
        state.check_with_meta(meta3)

    actual_dict = state.to_dict()
    assert state.to_dict() == {
        "values": ["2023-02-24"],
        "regexp": None,
        "filtertype": "category",
        "varname": "datestring",
        "metatype": None,
        "type": "filter",
    }

    actual_json = state.to_json(pretty=False)
    expected_json = '{"values":["2023-02-24"],"regexp":null,"metatype":null,"filtertype":"category","varname":"datestring","type":"filter"}'
    assert json.loads(actual_json) == json.loads(expected_json)


def test_category_filter_state_bad_values(iris_plus_df):
    state = CategoryFilterState("datestring", values="stuff")
    with pytest.raises(ValueError, match=r"could not find the value"):
        state.check_with_data(iris_plus_df)

    state2 = CategoryFilterState("bad_var_name", values="stuff")
    with pytest.raises(ValueError, match=r"'bad_var_name' not found in the dataset"):
        state2.check_with_data(iris_plus_df)


def test_number_range_filter_state_init():
    state = NumberRangeFilterState("the var", min=2, max=3)
    assert state.varname == "the var"
    assert state.min == 2
    assert state.max == 3
    assert set(state.applies_to) == {Meta.TYPE_NUMBER}
    assert state.type == State.TYPE_FILTER
    assert state.filtertype == FilterState.FILTERTYPE_NUMBER_RANGE


def test_number_range_filter_state(iris_plus_df):
    state = NumberRangeFilterState("Sepal.Length", min=1)
    meta1 = NumberMeta("Sepal.Length")
    meta2 = StringMeta("Species")

    state.check_with_data(iris_plus_df)
    state.check_with_meta(meta1)

    with pytest.raises(ValueError, match=r"is not compatible with this filter"):
        state.check_with_meta(meta2)

    actual_dict = state.to_dict()
    expected_dict = {
        "max": None,
        "min": 1,
        "filtertype": "numberrange",
        "varname": "Sepal.Length",
        "type": "filter",
        "metatype": "number",
    }
    assert actual_dict == expected_dict

    actual_json = state.to_json(pretty=False)
    expected_json = '{"max":null,"min":1,"filtertype":"numberrange","varname":"Sepal.Length","type":"filter","metatype":"number"}'
    assert json.loads(actual_json) == json.loads(expected_json)


def test_number_range_filter_state_bad_values(iris_plus_df):
    state = NumberRangeFilterState("stuff", min=1)
    with pytest.raises(ValueError, match=r"not found in the dataset"):
        state.check_with_data(iris_plus_df)


def test_date_range_filter_state_init():
    state = DateRangeFilterState(
        "the var", min=date(2022, 12, 25), max=date(2022, 12, 29)
    )
    assert state.varname == "the var"
    assert state.min == date(2022, 12, 25)
    assert state.max == date(2022, 12, 29)
    assert set(state.applies_to) == {Meta.TYPE_DATE}
    assert state.type == State.TYPE_FILTER
    assert state.filtertype == FilterState.FILTERTYPE_DATE_RANGE


def test_date_range_filter_state(iris_plus_df):
    state = DateRangeFilterState("date", min=date(2010, 1, 1))

    meta1 = DateMeta("date")
    meta2 = StringMeta("Species")

    state.check_with_data(iris_plus_df)
    state.check_with_meta(meta1)

    with pytest.raises(ValueError, match=r"is not compatible with this filter"):
        state.check_with_meta(meta2)

    actual_dict = state.to_dict()
    expected_dict = {
        "max": None,
        "min": date(2010, 1, 1),
        "filtertype": "daterange",
        "varname": "date",
        "type": "filter",
        "metatype": "date",
    }
    assert actual_dict == expected_dict

    actual_json = state.to_json(pretty=False)
    expected_json = '{"max":null,"min":"2010-01-01","filtertype":"daterange","varname":"date","type":"filter","metatype":"date"}'
    assert json.loads(actual_json) == json.loads(expected_json)


def test_date_range_filter_state_bad_values(iris_plus_df):
    state = DateRangeFilterState("stuff", min=date(2010, 1, 1))
    with pytest.raises(ValueError, match=r"not found in the dataset"):
        state.check_with_data(iris_plus_df)

    # TODO: Consider adding test to make sure min and max do not allow ints
    # (they must be dates)


def test_datetime_range_filter_state_init():
    state = DatetimeRangeFilterState(
        "the var",
        min=datetime(2022, 12, 25, 1, 20, 30),
        max=datetime(2022, 12, 29, 2, 40, 50),
    )
    assert state.varname == "the var"
    assert state.min == datetime(2022, 12, 25, 1, 20, 30)
    assert state.max == datetime(2022, 12, 29, 2, 40, 50)
    assert set(state.applies_to) == {Meta.TYPE_DATETIME}
    assert state.type == State.TYPE_FILTER
    assert state.filtertype == FilterState.FILTERTYPE_DATETIME_RANGE


def test_datetime_range_filter_state(iris_plus_df):
    state = DatetimeRangeFilterState("datetime", min=datetime(2010, 1, 1))

    meta1 = DatetimeMeta("datetime")
    meta2 = StringMeta("Species")

    state.check_with_data(iris_plus_df)
    state.check_with_meta(meta1)

    with pytest.raises(ValueError, match=r"is not compatible with this filter"):
        state.check_with_meta(meta2)

    actual_dict = state.to_dict()
    expected_dict = {
        "max": None,
        "min": datetime(2010, 1, 1),
        "filtertype": "datetimerange",
        "varname": "datetime",
        "type": "filter",
        "metatype": "datetime",
    }
    assert actual_dict == expected_dict

    actual_json = state.to_json(pretty=False)
    expected_json = '{"max":null,"min":"2010-01-01T00:00:00","filtertype":"datetimerange","varname":"datetime","type":"filter","metatype":"datetime"}'
    assert json.loads(actual_json) == json.loads(expected_json)


def test_date_range_filter_state_bad_values(iris_plus_df):
    state = DatetimeRangeFilterState("stuff", min=datetime(2010, 1, 1))
    with pytest.raises(ValueError, match=r"not found in the dataset"):
        state.check_with_data(iris_plus_df)

    # TODO: Consider adding test to make sure min and max do not allow ints
    # (they must be dates)
