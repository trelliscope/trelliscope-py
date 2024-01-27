from trelliscope.panel_source import (
    FilePanelSource,
    LocalWebSocketPanelSource,
    RESTPanelSource,
)


def test_file_panel_source():
    panel_source = FilePanelSource(True)
    assert panel_source.type == "file"
    assert panel_source.to_dict() == {"type": "file", "isLocal": True}

    panel_source = FilePanelSource(False)
    assert panel_source.type == "file"
    assert panel_source.to_dict() == {"type": "file", "isLocal": False}


def test_rest_panel_source():
    panel_source = RESTPanelSource("u", "a", "h")
    assert panel_source.type == "REST"
    assert panel_source.url == "u"
    assert panel_source.api_key == "a"
    assert panel_source.headers == "h"

    assert panel_source.to_dict() == {
        "type": "REST",
        "url": "u",
        "apiKey": "a",
        "headers": "h",
    }


def test_local_web_socket_panel_source():
    panel_source = LocalWebSocketPanelSource("u", 1234)
    assert panel_source.type == "localWebSocket"
    assert panel_source.url == "u"
    assert panel_source.port == 1234

    assert panel_source.to_dict() == {
        "type": "localWebSocket",
        "url": "u",
        "port": 1234,
    }
