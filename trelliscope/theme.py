from __future__ import annotations

import json


class Theme:
    """
    Defines visual theming for a Trelliscope display.

    All color parameters accept CSS color strings (e.g. "#4C72B0", "rgb(76,114,176)",
    "steelblue"). The logo parameter accepts a URL or a base64 data URI.
    """

    _COLOR_PARAMS = [
        "primary",
        "primary2",
        "primary3",
        "background",
        "background2",
        "background3",
        "bars",
        "text",
        "text2",
        "button_text",
        "text_disabled",
        "error",
    ]

    # Maps Python snake_case attribute names to the camelCase keys the JS viewer expects.
    _ATTR_TO_KEY = {
        "primary": "primary",
        "primary2": "primary2",
        "primary3": "primary3",
        "background": "background",
        "background2": "background2",
        "background3": "background3",
        "bars": "bars",
        "text": "text",
        "text2": "text2",
        "button_text": "buttonText",
        "text_disabled": "textDisabled",
        "error": "error",
        "font_family": "fontFamily",
        "logo": "logo",
    }

    def __init__(
        self,
        primary: str = None,
        primary2: str = None,
        primary3: str = None,
        background: str = None,
        background2: str = None,
        background3: str = None,
        bars: str = None,
        text: str = None,
        text2: str = None,
        button_text: str = None,
        text_disabled: str = None,
        error: str = None,
        font_family: str = None,
        logo: str = None,
    ):
        for param in self._COLOR_PARAMS:
            val = locals()[param]
            if val is not None and not isinstance(val, str):
                raise ValueError(
                    f"Theme color parameter '{param}' must be a CSS color string, "
                    f"got {type(val).__name__}."
                )

        if font_family is not None and not isinstance(font_family, str):
            raise ValueError("Theme 'font_family' must be a string.")
        if logo is not None and not isinstance(logo, str):
            raise ValueError("Theme 'logo' must be a string (URL or data URI).")

        self.primary = primary
        self.primary2 = primary2
        self.primary3 = primary3
        self.background = background
        self.background2 = background2
        self.background3 = background3
        self.bars = bars
        self.text = text
        self.text2 = text2
        self.button_text = button_text
        self.text_disabled = text_disabled
        self.error = error
        self.font_family = font_family
        self.logo = logo

    @property
    def is_custom(self) -> bool:
        return any(getattr(self, attr) is not None for attr in self._ATTR_TO_KEY)

    def to_dict(self) -> dict:
        result = {}
        for attr, key in self._ATTR_TO_KEY.items():
            val = getattr(self, attr)
            if val is not None:
                result[key] = val
        result["isCustom"] = self.is_custom
        return result

    def to_json(self, pretty: bool = True) -> str:
        return json.dumps(self.to_dict(), indent=2 if pretty else None)

    def __repr__(self) -> str:
        custom = {
            k: v for k, v in self._ATTR_TO_KEY.items() if getattr(self, k) is not None
        }
        return f"Theme(is_custom={self.is_custom}, params={list(custom.keys())})"
