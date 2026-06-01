"""
ゲーム全体で使う定数定義
"""

import pygame

# ========================
# 画面サイズ
# ========================
WIDTH = 400
HEIGHT = 600
LANES = 4
LANE_WIDTH = WIDTH // LANES

# ========================
# ノーツ判定
# ========================
JUDGE_LINE = HEIGHT - 100
PERFECT_RANGE = 20
GREAT_RANGE = 40
GOOD_RANGE = 60
LONG_NOTE_LENGTH = 300
SHORT_NOTE_LENGTH = 150
LONG_NOTE_THRESHOLD = 150
NOTE_HEIGHT = 20

# 判定タイミング（秒）
PERFECT_TIME = 0.03
GREAT_TIME = 0.06
GOOD_TIME = 0.10

# ========================
# キー設定
# ========================
KEYS_TO_LANES = {pygame.K_d: 0, pygame.K_f: 1, pygame.K_j: 2, pygame.K_k: 3}

# ========================
# 色定義
# ========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
CYAN = (0, 150, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

LANE_COLORS = [(0, 0, 0), (40, 40, 40), (80, 80, 80), (120, 120, 120)]

# ========================
# UI カラー定義
# ========================
UI_COLORS = {
    "button_selected": (80, 120, 255),
    "button_default": (200, 220, 255),
    "title_glow": (60, 120, 255),
    "text_primary": (30, 30, 30),
    "text_secondary": (60, 120, 255),
    "bg_lane_even": (255, 255, 255, 18),
    "bg_lane_odd": (220, 235, 255, 28),
    "judge_line": (60, 120, 255),
    "judge_glow": (80, 170, 255, 70),
    "lane_flash": (100, 150, 255),
    "holding_highlight": (0, 220, 255, 45),
}

# ========================
# ノーツ描画パラメータ
# ========================
NOTE_COLORS = {
    "short_body": (0, 200, 255),
    "short_border": (255, 255, 255),
    "short_inner": (200, 220, 255),
    "long_body": (0, 170, 255),
    "long_body_holding": (0, 230, 255),
    "long_border": (120, 210, 255),
    "long_glow": (80, 180, 255, 70),
    "long_core": (0, 140, 255),
}

# ========================
# 画像・グラフィックス
# ========================
JACKET_SIZE = 200

# ========================
# 譜面生成パラメータ
# ========================
CHART_GENERATION_PARAMS = {
    "EASY": {
        "note_steps": [60 / 130],  # 4分のみ（BPMで計算）
        "long_chance": 0.05,
        "long_duration_beats": (2, 3),
    },
    "NORMAL": {
        "note_steps": [1.0, 0.5],  # 4分、8分
        "long_chance": 0.20,
        "long_duration_beats": (2, 3),
    },
    "HARD": {
        "note_steps": [1.0, 0.5, 0.25],  # 4分、8分、16分
        "long_chance": 0.2,
        "long_duration_beats": (2, 3, 4),
    },
}

# ========================
# 視認性パラメータ
# ========================
VISIBLE_TIME = 1.2
SPAWN_Y = -NOTE_HEIGHT
