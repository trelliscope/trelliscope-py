class Input:
    """Input object passed to trelliscope.

    TODO: explain how this is used.
    """

    def __init__(self):
        self._name = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
