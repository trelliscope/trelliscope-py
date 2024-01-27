import json

from trelliscope.state import LabelState, SortState
from trelliscope.view import View

# Note, when using json results, we are converting the json to dictionaries
# and comparing those to ignore any differences in order or whitespace


def test_create_view_with_no_state():
    view = View("test view")

    # Look at just the state
    state = view.state
    actual_json = state.to_json()
    expected_json = '{"layout":null,"labels":null,"sort":[],"filter":[]}'
    assert json.loads(actual_json) == json.loads(expected_json)

    # look at the whole view
    actual_json = view.to_json(pretty=False)
    expected_json = '{"name":"test view","state":{"layout":null,"labels":null,"sort":[],"filter":[]}}'
    assert json.loads(actual_json) == json.loads(expected_json)


def test_create_view_with_state_parameters():
    view = View(
        "test view",
        label_state=LabelState(["manufacturer", "class"]),
        sort_state=SortState("manufacturer"),
    )

    actual_json = view.to_json(pretty=False)
    expected_json = '{"name":"test view","state":{"layout":null,"labels":{"varnames":["manufacturer","class"],"type":"labels"},"sort":[{"metatype":null,"dir":"asc","varname":"manufacturer","type":"sort"}],"filter":[]}}'
    assert json.loads(actual_json) == json.loads(expected_json)
