"""Definitions of sources for Panels.

Panels can be laoded from files, REST endpoints and websockets. Depending on the panel's source,
the properties expected by Trelliscope are different.
"""


class PanelSource:
    """Base Panel source class."""

    def __init__(self, source_type: str) -> None:
        """Create the base Panel source.

        Args:
            source_type: Type of source. One of ['file', 'REST', 'websocket'].
        """
        self.type = source_type

    def to_dict(self):
        """Dictionary of class properties as expected by Trelliscope."""
        # Default serialization behavior is sufficient
        return self.__dict__.copy()


class FilePanelSource(PanelSource):
    """Panel source class for reading from local files."""

    def __init__(self, is_local: bool) -> None:
        """Create file panel source.

        Args:
            is_local: Boolean flag whether to read from local file.
        """
        super().__init__("file")
        self.is_local = is_local

    def to_dict(self):
        """Dictionary of class properties as expected by Trelliscope."""
        result = super().to_dict()

        # Move "is_local" to be "isLocal" because that is how the JS library expects it
        result.pop("is_local", None)
        result["isLocal"] = self.is_local

        return result


class RESTPanelSource(PanelSource):
    """Panel source class for requesting panel from REST endpoint."""

    def __init__(self, url: str, api_key: str = None, headers: str = None) -> None:
        """Create REST panel source.

        Args:
            url: URL for GET request for panel.
            api_key: Optional api key to authenticate with REST api.
            headers: Optional additional headers to send with request.
        """
        super().__init__("REST")
        self.url = url
        self.api_key = api_key
        self.headers = headers

    def to_dict(self):
        """Dictionary of class properties as expected by Trelliscope."""
        result = super().to_dict()
        result["apiKey"] = result.pop("api_key")

        return result


class LocalWebSocketPanelSource(PanelSource):
    """Panel source class for loading from local websockets."""

    def __init__(self, url: str, port: int) -> None:
        """Create local websocket panel source.

        Args:
            url: Local URL of websocket.
            port: Port to connect to.
        """
        super().__init__("localWebSocket")
        self.url = url
        self.port = port
