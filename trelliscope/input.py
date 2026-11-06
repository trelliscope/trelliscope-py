from __future__ import annotations

import json


class Input:
    """Base class for all user annotation input types."""

    TYPE_TEXT = "text"
    TYPE_NUMBER = "number"
    TYPE_RADIO = "radio"
    TYPE_CHECKBOX = "checkbox"
    TYPE_SELECT = "select"
    TYPE_MULTISELECT = "multiselect"

    def __init__(self, type: str, name: str, label: str = None):
        if not isinstance(name, str) or not name:
            raise ValueError("Input 'name' must be a non-empty string.")
        self._name = name
        self.type = type
        self.label = label if label is not None else name
        self.active = True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value:
            raise ValueError("Input 'name' must be a non-empty string.")
        self._name = value

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "label": self.label,
            "type": self.type,
            "active": self.active,
        }

    def to_json(self, pretty: bool = True) -> str:
        return json.dumps(self.to_dict(), indent=2 if pretty else None)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name!r}, label={self.label!r})"


class TextInput(Input):
    """Free-form multi-line text annotation input."""

    def __init__(self, name: str, label: str = None, width: int = 80, height: int = 3):
        super().__init__(Input.TYPE_TEXT, name, label)
        if not isinstance(width, int) or width <= 0:
            raise ValueError("TextInput 'width' must be a positive integer.")
        if not isinstance(height, int) or height <= 0:
            raise ValueError("TextInput 'height' must be a positive integer.")
        self.width = width
        self.height = height

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["width"] = self.width
        d["height"] = self.height
        return d


class NumberInput(Input):
    """Numeric annotation input with optional min/max bounds."""

    def __init__(
        self,
        name: str,
        label: str = None,
        min: float = None,
        max: float = None,
    ):
        super().__init__(Input.TYPE_NUMBER, name, label)
        if min is not None and not isinstance(min, (int, float)):
            raise ValueError("NumberInput 'min' must be numeric.")
        if max is not None and not isinstance(max, (int, float)):
            raise ValueError("NumberInput 'max' must be numeric.")
        if min is not None and max is not None and min > max:
            raise ValueError("NumberInput 'min' must not exceed 'max'.")
        self.min = min
        self.max = max

    def to_dict(self) -> dict:
        d = super().to_dict()
        if self.min is not None:
            d["min"] = self.min
        if self.max is not None:
            d["max"] = self.max
        return d


class RadioInput(Input):
    """Single-choice radio button annotation input."""

    def __init__(self, name: str, label: str = None, options: list = None):
        super().__init__(Input.TYPE_RADIO, name, label)
        if options is None or not isinstance(options, list) or len(options) == 0:
            raise ValueError("RadioInput 'options' must be a non-empty list.")
        self.options = options

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["options"] = self.options
        return d


class CheckboxInput(Input):
    """Multi-choice checkbox annotation input."""

    def __init__(self, name: str, label: str = None, options: list = None):
        super().__init__(Input.TYPE_CHECKBOX, name, label)
        if options is None or not isinstance(options, list) or len(options) == 0:
            raise ValueError("CheckboxInput 'options' must be a non-empty list.")
        self.options = options

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["options"] = self.options
        return d


class SelectInput(Input):
    """Single-choice dropdown annotation input."""

    def __init__(self, name: str, label: str = None, options: list = None):
        super().__init__(Input.TYPE_SELECT, name, label)
        if options is None or not isinstance(options, list) or len(options) == 0:
            raise ValueError("SelectInput 'options' must be a non-empty list.")
        self.options = options

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["options"] = self.options
        return d


class MultiselectInput(Input):
    """Multi-choice dropdown annotation input."""

    def __init__(self, name: str, label: str = None, options: list = None):
        super().__init__(Input.TYPE_MULTISELECT, name, label)
        if options is None or not isinstance(options, list) or len(options) == 0:
            raise ValueError("MultiselectInput 'options' must be a non-empty list.")
        self.options = options

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["options"] = self.options
        return d
