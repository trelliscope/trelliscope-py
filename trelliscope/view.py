import copy
import json

from .state import DisplayState, FilterState, LabelState, LayoutState, SortState


class View:
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
        result = {}

        result["name"] = self.name
        result["state"] = self.state.to_dict()

        return result

    def to_json(self, pretty: bool = True) -> str:
        indent_value = None

        if pretty:
            indent_value = 2

        return json.dumps(self.to_dict(), indent=indent_value)

    def _copy(self):
        # TODO: Shallow or deep copy??
        return copy.deepcopy(self)
