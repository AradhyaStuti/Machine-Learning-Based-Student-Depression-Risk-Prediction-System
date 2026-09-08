# Tests for GUI constants (colors, sliders, dropdown options)

import re

from src.GUI import (
    ACCENT,
    BG_CARD,
    BG_DARK,
    BG_INPUT,
    BORDER,
    DIET_OPTIONS,
    GENDER_OPTIONS,
    GREEN,
    ORANGE,
    RED,
    SLEEP_OPTIONS,
    SLIDER_DEFAULT,
    SLIDER_MAX,
    SLIDER_MIN,
    TEXT_BRIGHT,
    TEXT_DIM,
    TEXT_MID,
)

ALL_COLORS = [
    GREEN,
    ORANGE,
    RED,
    ACCENT,
    BORDER,
    BG_DARK,
    BG_CARD,
    BG_INPUT,
    TEXT_DIM,
    TEXT_MID,
    TEXT_BRIGHT,
]
ALL_DROPDOWNS = {"diet": DIET_OPTIONS, "sleep": SLEEP_OPTIONS, "gender": GENDER_OPTIONS}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class TestGUIConstants:
    def test_slider_range_consistent(self):
        assert SLIDER_MIN < SLIDER_MAX
        assert SLIDER_MIN <= SLIDER_DEFAULT <= SLIDER_MAX

    def test_all_colors_valid_hex(self):
        for color in ALL_COLORS:
            assert HEX_RE.match(color), f"{color} is not valid hex"
