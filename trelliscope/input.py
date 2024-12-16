"""Input objects for Trelliscope."""


class Input:
    """Input object passed to trelliscope.

    TODO: explain how this is used.
    """

    def __init__(self):
        """Initialize with default name=""."""
        self._name = ""

    @property
    def name(self):
        """Name of Input."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
