"""
商用仕様：テーマカラー定義（完全版・テーマ切り替え対応）

ゲーム全体で使用する基本色を定義し、theme.py と連携して利用する。
"""

# ============================================================
# 基本色定義
# ============================================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (180, 180, 180)
DARK_GRAY = (60, 60, 60)

RED = (255, 80, 80)
GREEN = (80, 255, 120)
BLUE = (80, 120, 255)
YELLOW = (255, 220, 80)
PURPLE = (180, 80, 255)
PINK = (255, 120, 200)
ORANGE = (255, 180, 120)
CYAN = (120, 255, 255)

# ============================================================
# テーマカラーセット
# ============================================================

THEMES = {
    "Blue": {
        "bg_title": (20, 30, 60),
        "bg_select": (25, 35, 70),
        "title_glow": (120, 180, 255),
        "text_primary": WHITE,
        "text_secondary": LIGHT_GRAY,
        "accent": BLUE,
        "warning": RED,
        "success": GREEN,
        "highlight": YELLOW,
    },
    "Pink": {
        "bg_title": (60, 20, 40),
        "bg_select": (70, 25, 50),
        "title_glow": (255, 150, 200),
        "text_primary": WHITE,
        "text_secondary": LIGHT_GRAY,
        "accent": PINK,
        "warning": RED,
        "success": GREEN,
        "highlight": YELLOW,
    },
    "Green": {
        "bg_title": (20, 50, 40),
        "bg_select": (25, 60, 45),
        "title_glow": (120, 255, 180),
        "text_primary": WHITE,
        "text_secondary": LIGHT_GRAY,
        "accent": GREEN,
        "warning": RED,
        "success": GREEN,
        "highlight": YELLOW,
    },
    "Gold": {
        "bg_title": (60, 50, 20),
        "bg_select": (70, 60, 25),
        "title_glow": (255, 220, 120),
        "text_primary": WHITE,
        "text_secondary": LIGHT_GRAY,
        "accent": YELLOW,
        "warning": RED,
        "success": GREEN,
        "highlight": ORANGE,
    },
}

# ============================================================
# デフォルトテーマ
# ============================================================

UI_COLORS = THEMES["Blue"]

# Song IDs map to RGB jacket background colors.
SONG_COLOR_MAP = {
    "fantaisie": PURPLE,
    "moonlight": (20, 24, 60),
    "erize": PINK,
    "wakareno": (180, 80, 120),
    "lacampanella": YELLOW,
    "hungarian5": (180, 35, 45),
    "aux-enfers": (80, 25, 35),
    "arabesque1": CYAN,
    "gline": (235, 220, 180),
    "carmen": RED,
    "trukish": BLUE,
    "music": (80, 180, 140),
}
