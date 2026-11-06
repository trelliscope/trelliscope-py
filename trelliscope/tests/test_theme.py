import json

import pytest

from trelliscope import Theme
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


def test_theme_to_dict_empty():
    d = Theme().to_dict()
    assert d == {"isCustom": False}


def test_theme_to_dict_camelcase_keys():
    t = Theme(button_text="#fff", text_disabled="#ccc", font_family="Arial")
    d = t.to_dict()
    # Python snake_case attrs must be serialized as camelCase keys
    assert "buttonText" in d
    assert "textDisabled" in d
    assert "fontFamily" in d
    assert "button_text" not in d
    assert "text_disabled" not in d
    assert "font_family" not in d


def test_theme_to_dict_only_non_none():
    t = Theme(primary="#123", text="#abc")
    d = t.to_dict()
    assert d["primary"] == "#123"
    assert d["text"] == "#abc"
    assert "primary2" not in d
    assert d["isCustom"] is True


def test_theme_to_json():
    t = Theme(primary="#abc")
    parsed = json.loads(t.to_json())
    assert parsed["primary"] == "#abc"
    assert parsed["isCustom"] is True


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


def test_set_theme_in_to_dict(iris_tr):
    tr = iris_tr.set_theme(primary="#ff0000")
    d = tr.to_dict()
    assert d["theme"] is not None
    assert d["theme"]["primary"] == "#ff0000"
    assert d["theme"]["isCustom"] is True


def test_no_theme_in_to_dict(iris_tr):
    d = iris_tr.to_dict()
    assert d["theme"] is None


def test_set_theme_invalid_color(iris_tr):
    with pytest.raises(ValueError, match="CSS color string"):
        iris_tr.set_theme(primary=42)
