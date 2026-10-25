"""
motion_library - Reusable Mobile-First 2D Motion Graphics Library.
"""

from .palette import GLASS_THEME, TYPOGRAPHY, DOMAIN_PRESETS, SUBTITLE_COLORS, to_tuple_color
from .catalog import MOTION_CATALOG
from .renderers import TEMPLATE_MAP, find_external_asset, draw_editorial_header

draw_light_glass_plate = draw_editorial_header

__all__ = [
    "GLASS_THEME",
    "TYPOGRAPHY",
    "DOMAIN_PRESETS",
    "SUBTITLE_COLORS",
    "to_tuple_color",
    "MOTION_CATALOG",
    "TEMPLATE_MAP",
    "find_external_asset",
    "draw_editorial_header",
    "draw_light_glass_plate"
]
