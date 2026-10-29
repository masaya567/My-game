"""
ゲーム全体で使う定数定義（市販音ゲー品質・自動スケーリング対応・最終統合版）
"""

import pygame

# ========================
# 画面サイズ（自由に変更可能）
# ========================
WIDTH = 480
HEIGHT = 720

# ========================
# UI スケール（画面サイズに応じて自動調整）
# ========================
BASE_WIDTH = 400
BASE_HEIGHT = 600

UI_SCALE_X = WIDTH / BASE_WIDTH
UI_SCALE_Y = HEIGHT / BASE_HEIGHT
UI_SCALE = (UI_SCALE_X + UI_SCALE_Y) / 2   # 黄金比を崩さない平均スケール


# ========================
# レーン設定
# ========================
LANES = 4
LANE_WIDTH = WIDTH // LANES
LANE_X = [int((i + 0.5) * LANE_WIDTH) for i in range(LANES)]


# ========================
# 判定ライン（画面比率で安定）
# ========================
JUDGE_LINE = int(HEIGHT * 0.78)
JUDGE_LINE_WIDTH = int(4 * UI_SCALE)

NOTE_FALL_TIME = 1.8


# ========================
# ノーツ速度（BPM依存）
# ========================
def calc_note_speed(song_bpm):
    return 280 + (song_bpm * 0.8)


# ========================
# 判定タイミング（速度依存）
# ========================
def calc_judge_times(note_speed):
    speed_factor = note_speed / 380.0

    PERFECT_TIME = 0.045 / speed_factor
    GREAT_TIME = 0.090 / speed_factor
    GOOD_TIME = 0.140 / speed_factor
    MISS_TIME = 0.220 / speed_factor

    return PERFECT_TIME, GREAT_TIME, GOOD_TIME, MISS_TIME


# ========================
# 判定幅（px）速度同期
# ========================
def calc_px_ranges(note_speed, PERFECT_TIME, GREAT_TIME, GOOD_TIME):
    PERFECT_RANGE = int(note_speed * PERFECT_TIME)
    GREAT_RANGE = int(note_speed * GREAT_TIME)
    GOOD_RANGE = int(note_speed * GOOD_TIME)
    return PERFECT_RANGE, GREAT_RANGE, GOOD_RANGE


# ========================
# 難易度別判定スケール
# ========================
DIFFICULTY_JUDGE_SCALE = {
    "EASY": 1.20,
    "NORMAL": 1.00,
    "HARD": 0.90,
    "EXPERT": 0.80,
}


# ========================
# ノーツサイズ（自動スケーリング）
# ========================
NOTE_HEIGHT = int(20 * UI_SCALE)
NOTE_START_Y = int(-40 * UI_SCALE)

def calc_long_length(peak_strength):
    return int((200 + (peak_strength * 180)) * UI_SCALE)

LONG_NOTE_THRESHOLD = int(150 * UI_SCALE)


# ========================
# 視認性（速度依存）
# ========================
def calc_visible_time(note_speed):
    return max(3.5, 6.0 - (note_speed / 200))


SPAWN_Y = -NOTE_HEIGHT
BPM_SMOOTHING = 0.12


# ========================
# キー設定
# ========================
KEYS_TO_LANES = {
    pygame.K_d: 0,
    pygame.K_f: 1,
    pygame.K_j: 2,
    pygame.K_k: 3,
}


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
# UI カラー
# ========================
UI_COLORS = {
    "button_selected": (80, 120, 255),
    "button_default": (200, 220, 255),
    "title_glow": (60, 120, 255),
    "bg_title": (20, 30, 60),
    "text_primary": (30, 30, 30),
    "text_secondary": (60, 120, 255),
    "bg_lane_even": (255, 255, 255, 18),
    "bg_lane_odd": (220, 235, 255, 28),
    "bg_select": (240, 245, 255),
    "judge_line": (60, 120, 255),
    "judge_glow": (80, 170, 255, 70),
    "lane_flash": (100, 150, 255),
    "holding_highlight": (0, 220, 255, 45),
    "menu_highlight": (40, 80, 160),
}


# ========================
# ノーツ描画カラー
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
# 判定カラー
# ========================
JUDGE_COLORS = {
    "perfect": (120, 180, 255),
    "great": (180, 255, 120),
    "good": (255, 220, 120),
    "miss": (255, 80, 80),
}

JUDGE_STRENGTH = {
    "perfect": 1.0,
    "great": 0.8,
    "good": 0.6,
    "miss": 0.0,
}


# ========================
# スコア
# ========================
SCORE_PERFECT = 1000
SCORE_GREAT = 500
SCORE_GOOD = 200
SCORE_MISS = 0

COMBO_MULTIPLIER = 1.02
JUDGE_TEXT_DURATION = 0.45


# ========================
# 負荷対策
# ========================
MAX_VISIBLE_NOTES = 200


# ========================
# FPS
# ========================
TARGET_FPS = 60
FPS = TARGET_FPS


# ========================
# 音量
# ========================
DEFAULT_BGM_VOLUME = 0.8
DEFAULT_SE_VOLUME = 0.9
