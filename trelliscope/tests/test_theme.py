import json
import os
import tempfile

import pytest

from trelliscope import Trelliscope, utils
from trelliscope.panel_source import FilePanelSource
from trelliscope.panels import ImagePanel
from trelliscope.theme import Theme

# ---------------------------------------------------------------------------
# Theme construction
# ---------------------------------------------------------------------------


def test_theme_empty():
    t = Theme()
    assert t.is_custom is False


def test_theme_with_primary():
    t = Theme(primary="#ff0000")
    assert t.primary == "#ff0000"
    assert t.is_custom is True


def test_theme_all_params():
    t = Theme(
        primary="#111",
        primary2="#222",
        primary3="#333",
        background="#444",
        background2="#555",
        background3="#666",
        bars="#777",
        text="#888",
        text2="#999",
        button_text="#aaa",
        text_disabled="#bbb",
        error="#ccc",
        font_family="sans-serif",
        logo="https://example.com/logo.png",
    )
    assert t.is_custom is True
    assert t.font_family == "sans-serif"
    assert t.logo == "https://example.com/logo.png"


def test_theme_invalid_color_type():
    with pytest.raises(ValueError, match="CSS color string"):
        Theme(primary=123)


def test_theme_invalid_font_family_type():
    with pytest.raises(ValueError, match="font_family"):
        Theme(font_family=42)


def test_theme_invalid_logo_type():
    with pytest.raises(ValueError, match="logo"):
        Theme(logo=["not", "a", "string"])


# ---------------------------------------------------------------------------
# Theme serialization
# ---------------------------------------------------------------------------


def test_theme_to_dict_defaults_match_r_package():
    d = Theme().to_dict()
    assert d["palette"]["primary"] == {
        "main": "#448aff",
        "light": "#4dabf5",
        "dark": "#2e60b1",
        "contrastText": "#757575",
    }
    assert d["typography"]["fontFamily"] == '"Poppins", sans-serif'
    assert d["logo"] is None


def test_theme_to_dict_maps_colors_to_mui_palette():
    t = Theme(
        primary="#111",
        primary2="#222",
        primary3="#333",
        background="#444",
        background2="#555",
        background3="#666",
        bars="#777",
        text="#888",
        text2="#999",
        button_text="#aaa",
        text_disabled="#bbb",
        error="#ccc",
        font_family="Arial",
        logo="logo.png",
    )
    d = t.to_dict()
    assert d["palette"] == {
        "primary": {
            "main": "#111",
            "light": "#222",
            "dark": "#333",
            "contrastText": "#aaa",
        },
        "secondary": {
            "main": "#444",
            "light": "#555",
            "dark": "#666",
            "contrastText": "#777",
        },
        "background": {"default": "#444"},
        "action": {"active": "#aaa"},
        "text": {"primary": "#888", "secondary": "#999", "disabled": "#bbb"},
        "error": {"main": "#ccc"},
    }
    assert d["typography"]["fontFamily"] == "Arial"
    assert d["logo"] == "logo.png"


def test_theme_to_json():
    t = Theme(primary="#abc")
    parsed = json.loads(t.to_json())
    assert parsed["palette"]["primary"]["main"] == "#abc"


def test_theme_repr():
    t = Theme(primary="#abc")
    r = repr(t)
    assert "Theme" in r
    assert "primary" in r


# ---------------------------------------------------------------------------
# set_theme() on Trelliscope
# ---------------------------------------------------------------------------


def test_set_theme(iris_tr):
    tr = iris_tr.set_theme(primary="#4C72B0", font_family="Helvetica")
    assert tr.theme is not None
    assert tr.theme.primary == "#4C72B0"
    assert tr.theme.font_family == "Helvetica"


def test_set_theme_does_not_mutate_original(iris_tr):
    tr2 = iris_tr.set_theme(primary="#ff0000")
    assert iris_tr.theme is None
    assert tr2.theme.primary == "#ff0000"


def _write_and_read_config(tr, output_dir):
    tr = tr.write_display()
    config = utils.read_jsonp(os.path.join(tr.get_output_path(), "config.jsonp"))
    return tr, config


def test_set_theme_written_to_app_config(iris_df_no_duplicates):
    df = iris_df_no_duplicates.copy()
    df["img"] = "test.png"
    pnl = ImagePanel("img", source=FilePanelSource(False), should_copy_to_output=False)
    with tempfile.TemporaryDirectory() as output_dir:
        tr = Trelliscope(df, "test", path=output_dir).add_panel(pnl)
        tr, config = _write_and_read_config(tr.set_theme(primary="#ff0000"), output_dir)

        # The viewer reads the theme from the app config, not the display info.
        assert config["theme"]["palette"]["primary"]["main"] == "#ff0000"
        assert "theme" not in tr.to_dict()

        # Writing again without a theme clears it from the config.
        tr.theme = None
        _, config = _write_and_read_config(tr, output_dir)
        assert "theme" not in config


def test_set_theme_invalid_color(iris_tr):
    with pytest.raises(ValueError, match="CSS color string"):
        iris_tr.set_theme(primary=42)
