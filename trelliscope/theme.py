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

    # The R package's set_theme() defaults, used for any color not given.
    _DEFAULTS = {
        "primary": "#448aff",
        "primary2": "#4dabf5",
        "primary3": "#2e60b1",
        "background": "#FEFEFE",
        "background2": "#EBEBEB",
        "background3": "#E0E0E0",
        "bars": "#FFAE25",
        "text": "#000",
        "text2": "#FFF",
        "button_text": "#757575",
        "text_disabled": "#BCBCBC",
        "error": "#ff5252",
        "font_family": '"Poppins", sans-serif',
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
        return any(
            getattr(self, attr) is not None for attr in [*self._DEFAULTS, "logo"]
        )

    def to_dict(self) -> dict:
        """
        Returns the theme as the MUI theme object the viewer reads from the app
        config, built the same way as the R package's set_theme().
        """

        def get(attr):
            val = getattr(self, attr)
            return self._DEFAULTS[attr] if val is None else val

        return {
            "palette": {
                "primary": {
                    "main": get("primary"),
                    "light": get("primary2"),
                    "dark": get("primary3"),
                    "contrastText": get("button_text"),
                },
                "secondary": {
                    "main": get("background"),
                    "light": get("background2"),
                    "dark": get("background3"),
                    "contrastText": get("bars"),
                },
                "background": {"default": get("background")},
                "action": {"active": get("button_text")},
                "text": {
                    "primary": get("text"),
                    "secondary": get("text2"),
                    "disabled": get("text_disabled"),
                },
                "error": {"main": get("error")},
            },
            "typography": {
                "fontFamily": get("font_family"),
                "fontWeightLight": 200,
                "fontWeightRegular": 300,
                "fontWeightMedium": 400,
            },
            "logo": self.logo,
        }

    def to_json(self, pretty: bool = True) -> str:
        return json.dumps(self.to_dict(), indent=2 if pretty else None)

    def __repr__(self) -> str:
        custom = [
            attr
            for attr in [*self._DEFAULTS, "logo"]
            if getattr(self, attr) is not None
        ]
        return f"Theme(is_custom={self.is_custom}, params={custom})"
