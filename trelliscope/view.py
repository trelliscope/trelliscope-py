"""Objects that define the View of a Trelliscope display.

A specified View for Trelliscope contains a pre-defined State, including layouts,
labels, sorting and filter states.
"""
from __future__ import annotations

import copy
import json

from trelliscope.state import (
    DisplayState,
    FilterState,
    LabelState,
    LayoutState,
    SortState,
)


class View:
    """Pre-defined View for Trelliscope display.

    A Trelliscope can have multiple Views, which are selectable in the app.
    """

    # TODO: Verify desirable API around passing in states
    # Should they be a list? Should it just be the display obj?
    # Should we keep an option for both single sort and multiple sort?
    def __init__(
        self,
        name: str,
        layout_state: LayoutState = None,
        label_state: LabelState = None,
        sort_state: SortState = None,
        sort_states: list = [],
        filter_state: FilterState = None,
        filter_states: list = [],
    ):
        """Create a pre-defined View state for Trelliscope display.

        Args:
            name: Name of the view, used for selecting the View from a dropdown menu in the app.
            layout_state: Layout in this View.
            label_state: Labels displayed in this View.
            sort_state: Sorting state in this View.
            sort_states: List of sorting states in this View
            filter_state: Filter state in this View.
            filter_states: List of filter states in this View.
        """
        self.name = name

        display_state = DisplayState()

        if layout_state is not None:
            display_state.set(layout_state)

        if label_state is not None:
            display_state.set(label_state)

        if sort_state is not None:
            display_state.set(sort_state, add=True)

        for sort_state in sort_states:
            display_state.set(sort_state, add=True)

        if filter_state is not None:
            display_state.set(filter_state, add=True)

        for filter_state in filter_states:
            display_state.set(filter_state, add=True)

        self.state = display_state

    def to_dict(self) -> dict:
        """Create dictioanry of attributes of a View expected by Trelliscope app."""
        result = {}

        result["name"] = self.name
        result["state"] = self.state.to_dict()

        return result

    def to_json(self, pretty: bool = True) -> str:
        """Format dictionary of this object as json.

        Args:
          pretty: If `True`, dumps to json using indent=2.
        """
        indent_value = None

        if pretty:
            indent_value = 2

        return json.dumps(self.to_dict(), indent=indent_value)

    def _copy(self) -> View:
        # TODO: Shallow or deep copy??
        return copy.deepcopy(self)
