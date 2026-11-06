import json

import pytest

from trelliscope.input import (
    CheckboxInput,
    Input,
    MultiselectInput,
    NumberInput,
    RadioInput,
    SelectInput,
    TextInput,
)

# ---------------------------------------------------------------------------
# TextInput
# ---------------------------------------------------------------------------


def test_text_input_defaults():
    inp = TextInput("notes")
    assert inp.name == "notes"
    assert inp.label == "notes"
    assert inp.type == Input.TYPE_TEXT
    assert inp.width == 80
    assert inp.height == 3


def test_text_input_custom():
    inp = TextInput("comments", label="My Comments", width=60, height=5)
    assert inp.label == "My Comments"
    assert inp.width == 60
    assert inp.height == 5


def test_text_input_to_dict():
    inp = TextInput("notes", label="Notes", width=80, height=4)
    d = inp.to_dict()
    assert d == {
        "name": "notes",
        "label": "Notes",
        "type": "text",
        "width": 80,
        "height": 4,
    }


def test_text_input_to_json():
    inp = TextInput("notes")
    parsed = json.loads(inp.to_json())
    assert parsed["type"] == "text"


def test_text_input_invalid_width():
    with pytest.raises(ValueError, match="width"):
        TextInput("notes", width=0)


def test_text_input_invalid_height():
    with pytest.raises(ValueError, match="height"):
        TextInput("notes", height=-1)


# ---------------------------------------------------------------------------
# NumberInput
# ---------------------------------------------------------------------------


def test_number_input_defaults():
    inp = NumberInput("score")
    assert inp.name == "score"
    assert inp.type == Input.TYPE_NUMBER
    assert inp.min is None
    assert inp.max is None


def test_number_input_with_bounds():
    inp = NumberInput("score", label="Quality Score", min=0, max=10)
    assert inp.min == 0
    assert inp.max == 10


def test_number_input_to_dict():
    inp = NumberInput("score", min=1, max=5)
    d = inp.to_dict()
    assert d["min"] == 1
    assert d["max"] == 5
    assert d["type"] == "number"


def test_number_input_to_dict_no_bounds():
    inp = NumberInput("score")
    d = inp.to_dict()
    assert "min" not in d
    assert "max" not in d


def test_number_input_invalid_bounds():
    with pytest.raises(ValueError, match="min.*max|max.*min"):
        NumberInput("score", min=10, max=5)


def test_number_input_invalid_min_type():
    with pytest.raises(ValueError, match="numeric"):
        NumberInput("score", min="bad")


# ---------------------------------------------------------------------------
# RadioInput
# ---------------------------------------------------------------------------


def test_radio_input():
    inp = RadioInput("quality", label="Quality", options=["good", "bad", "ugly"])
    assert inp.type == Input.TYPE_RADIO
    assert inp.options == ["good", "bad", "ugly"]


def test_radio_input_to_dict():
    inp = RadioInput("quality", options=["yes", "no"])
    d = inp.to_dict()
    assert d["options"] == ["yes", "no"]
    assert d["type"] == "radio"


def test_radio_input_empty_options():
    with pytest.raises(ValueError, match="options"):
        RadioInput("quality", options=[])


def test_radio_input_none_options():
    with pytest.raises(ValueError, match="options"):
        RadioInput("quality", options=None)


# ---------------------------------------------------------------------------
# CheckboxInput
# ---------------------------------------------------------------------------


def test_checkbox_input():
    inp = CheckboxInput("tags", options=["a", "b", "c"])
    assert inp.type == Input.TYPE_CHECKBOX
    assert len(inp.options) == 3


def test_checkbox_input_to_dict():
    inp = CheckboxInput("tags", label="Tags", options=["x", "y"])
    d = inp.to_dict()
    assert d["type"] == "checkbox"
    assert d["options"] == ["x", "y"]


def test_checkbox_input_invalid_options():
    with pytest.raises(ValueError, match="options"):
        CheckboxInput("tags", options="not-a-list")


# ---------------------------------------------------------------------------
# SelectInput
# ---------------------------------------------------------------------------


def test_select_input():
    inp = SelectInput("category", options=["A", "B", "C"])
    assert inp.type == Input.TYPE_SELECT


def test_select_input_to_dict():
    inp = SelectInput("category", label="Category", options=["A", "B"])
    d = inp.to_dict()
    assert d["type"] == "select"
    assert d["options"] == ["A", "B"]


def test_select_input_invalid_options():
    with pytest.raises(ValueError, match="options"):
        SelectInput("category", options=[])


# ---------------------------------------------------------------------------
# MultiselectInput
# ---------------------------------------------------------------------------


def test_multiselect_input():
    inp = MultiselectInput("tags", options=["x", "y", "z"])
    assert inp.type == Input.TYPE_MULTISELECT


def test_multiselect_input_to_dict():
    inp = MultiselectInput("tags", label="Tags", options=["p", "q"])
    d = inp.to_dict()
    assert d["type"] == "multiselect"
    assert d["options"] == ["p", "q"]


def test_multiselect_input_invalid_options():
    with pytest.raises(ValueError, match="options"):
        MultiselectInput("tags", options=None)


# ---------------------------------------------------------------------------
# Base Input validation
# ---------------------------------------------------------------------------


def test_input_empty_name():
    with pytest.raises(ValueError, match="name"):
        TextInput("")


def test_input_name_setter_validation():
    inp = TextInput("notes")
    with pytest.raises(ValueError, match="name"):
        inp.name = ""


def test_input_repr():
    inp = RadioInput("q", label="Quality", options=["good"])
    assert "RadioInput" in repr(inp)
    assert "q" in repr(inp)
