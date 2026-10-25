"""
motion_library/palette.py - High-Contrast Cohesive Color Palette for Instagram Reels.

Optimized specifically for mobile video readability:
- High contrast against both dark and light video footage.
- Cohesive visual hierarchy (Title -> Badge -> Interactive Visual -> Metrics).
- Clear, vivid domain-specific color coding for Tech, Finance, Banking, AI, Crypto.
"""

# Glass Panel Base Styling
GLASS_THEME = {
    "fill": (14, 20, 36, 175),          # Deep slate frosted acrylic (68% opacity)
    "border": (255, 255, 255, 75),       # Crisp light glass rim
    "sheen": (255, 255, 255, 140),       # Top light reflection
    "track": (255, 255, 255, 45),        # Subtle background tracks/rules
    "radius": 24,
    "width": 2
}

# Typography Colors
TYPOGRAPHY = {
    "title": (255, 255, 255, 255),       # Crisp White for Headlines
    "badge_text": (255, 255, 255, 255),  # Pure White inside Badges
    "label_primary": (195, 225, 255, 240), # Ice Cyan for Primary Labels
    "label_accent": (255, 215, 0, 255),  # Electric Gold for Metrics/Values
    "shadow": (0, 0, 0, 190)             # Drop Shadow for Subtitles
}

# Subtitle Kinetic Typography
SUBTITLE_COLORS = {
    "english_active": (255, 215, 0, 255),    # Electric Gold (#FFD700)
    "arabic_active": (0, 255, 163, 255),     # Neon Mint (#00FFA3)
    "inactive_word": (255, 255, 255, 255),   # Crisp White
    "stroke_fill": (0, 0, 0, 255),           # Heavy Black Outline
    "stroke_width": 4
}

# Domain Color Presets
DOMAIN_PRESETS = {
    "finance_markets": {
        "badge_color": (0, 235, 150, 240),     # Emerald Mint
        "accent_primary": (0, 240, 255, 255),  # Neon Cyan
        "accent_glow": (0, 240, 255, 70),
        "indicator": (255, 255, 255, 255)
    },
    "crypto_blockchain": {
        "badge_color": (255, 200, 0, 240),     # Amber Gold
        "accent_primary": (0, 255, 163, 255),  # Mint Green
        "accent_secondary": (0, 240, 255, 230),# Cyan
        "indicator": (255, 255, 255, 255)
    },
    "systemic_risk": {
        "badge_color": (255, 59, 48, 240),     # Coral Red
        "accent_primary": (255, 69, 58, 255),  # Crimson Alert
        "accent_secondary": (255, 204, 0, 240),# Warning Gold
        "indicator": (255, 255, 255, 255)
    },
    "ai_technology": {
        "badge_color": (168, 85, 247, 240),    # Electric Violet
        "accent_primary": (0, 240, 255, 255),  # Cyber Cyan
        "accent_secondary": (0, 255, 163, 255),# Mint Pulse
        "indicator": (255, 255, 255, 255)
    },
    "banking_institutions": {
        "badge_color": (59, 130, 246, 240),    # Royal Sapphire
        "accent_primary": (255, 204, 0, 255),  # Prudential Gold
        "accent_secondary": (195, 225, 255, 230),
        "indicator": (255, 255, 255, 255)
    },
    "financial_instruments": {
        "badge_color": (6, 182, 212, 240),     # Deep Cyan
        "accent_primary": (255, 149, 0, 255),  # Yield Curve Orange
        "accent_secondary": (0, 255, 163, 255),# Spread Mint
        "indicator": (255, 255, 255, 255)
    },
    "academia_research": {
        "badge_color": (37, 99, 235, 240),     # Oxford Sapphire
        "accent_primary": (255, 215, 0, 255),  # Honor Gold
        "accent_secondary": (0, 240, 255, 240),# Empirical Cyan
        "indicator": (255, 255, 255, 255)
    },
    "quantum_science": {
        "badge_color": (124, 58, 237, 240),    # Cosmic Violet
        "accent_primary": (0, 240, 255, 255),  # Electric Cyan
        "accent_secondary": (0, 255, 163, 240),# Superposition Mint
        "indicator": (255, 255, 255, 255)
    },
    "math_statistics": {
        "badge_color": (217, 119, 6, 240),     # Deep Amber
        "accent_primary": (16, 185, 129, 255), # Gaussian Emerald
        "accent_secondary": (59, 130, 246, 240),# Statistical Cobalt
        "indicator": (255, 255, 255, 255)
    },
    "market_sentiment": {
        "badge_color": (220, 38, 38, 240),     # Crimson Panic
        "accent_primary": (245, 158, 11, 255), # Momentum Gold
        "accent_secondary": (0, 240, 255, 240),# Greed Cyan
        "indicator": (255, 255, 255, 255)
    }
}


def to_tuple_color(color, default=(0, 255, 163, 230)):
    """Safely converts any color input (list, tuple) to a Pillow-safe RGBA tuple."""
    if isinstance(color, (list, tuple)):
        return tuple(color)
    return default
