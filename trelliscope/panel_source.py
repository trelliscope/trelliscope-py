class PanelSource:
    def __init__(self, source_type: str) -> None:
        self.type = source_type

    def to_dict(self):
        # Default serialization behavior is sufficient
        return self.__dict__.copy()


class FilePanelSource(PanelSource):
    def __init__(self, is_local: bool) -> None:
        super().__init__("file")

        self.is_local = is_local

    def to_dict(self):
        result = super().to_dict()

        # Move "is_local" to be "isLocal" because that is how the JS library expects it
        result.pop("is_local", None)
        result["isLocal"] = self.is_local

        return result


class RESTPanelSource(PanelSource):
    def __init__(self, url: str, api_key: str = None, headers: str = None) -> None:
        super().__init__("REST")
        self.url = url
        self.api_key = api_key
        self.headers = headers

    def to_dict(self):
        result = super().to_dict()
        result["apiKey"] = result.pop("api_key")

        return result


class LocalWebSocketPanelSource(PanelSource):
    def __init__(self, url: str, port: int) -> None:
        super().__init__("localWebSocket")
        self.url = url
        self.port = port
