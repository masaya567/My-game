# ============================================================
# 共通 DIFFICULTY（ベース値）※市販音ゲー基準の完全版
# ============================================================

DIFFICULTY_BASE = {
    "easy":   {"density": 0.18, "long_rate": 0.10, "rhythm_rate": 0.05, "variation": 0.02},
    "normal": {"density": 0.26, "long_rate": 0.15, "rhythm_rate": 0.06, "variation": 0.03},
    "hard":   {"density": 0.65, "long_rate": 0.22, "rhythm_rate": 0.22, "variation": 0.20},
    "expert": {"density": 1.00, "long_rate": 0.35, "rhythm_rate": 0.30, "variation": 0.35},
}


# ============================================================
# 曲別 DIFFICULTY（13曲すべて・最適化済み）
# ============================================================

SONG_DIFFICULTY = {

    "arabesque1": {
        "normal": {"density": 0.42},
        "hard":   {"density": 0.75},
        "expert": {"density": 1.10},
    },

    "aux-enfers": {
        "easy":   {"density": 0.22},
        "normal": {"density": 0.40},
        "hard":   {"density": 0.70},
        "expert": {"density": 1.05},
    },

    "carmen": {
        "normal": {"density": 0.45, "rhythm_rate": 0.18},
        "hard":   {"density": 0.80, "rhythm_rate": 0.30},
        "expert": {"density": 1.20, "variation": 0.45},
    },

    "erize": {
        "easy":   {"density": 0.20, "long_rate": 0.15},
        "normal": {"density": 0.32, "long_rate": 0.20},
        "hard":   {"density": 0.55, "long_rate": 0.30},
        "expert": {"density": 0.90, "long_rate": 0.45},
    },

    "fantaisie": {
        "normal": {"density": 0.40},
        "hard":   {"density": 0.85, "variation": 0.30},
        "expert": {"density": 1.25, "variation": 0.50},
    },

    "gline": {
        "easy":   {"density": 0.18, "long_rate": 0.20},
        "normal": {"density": 0.28, "long_rate": 0.25},
        "hard":   {"density": 0.45, "long_rate": 0.35},
        "expert": {"density": 0.70, "long_rate": 0.45},
    },

    "hungarian5": {
        "normal": {"density": 0.48, "rhythm_rate": 0.18},
        "hard":   {"density": 0.85, "variation": 0.30},
        "expert": {"density": 1.20, "variation": 0.50},
    },

    "lacampanella": {
        "normal": {"density": 0.50},
        "hard":   {"density": 0.90, "variation": 0.35},
        "expert": {"density": 1.30, "variation": 0.55},
    },

    "moonlight": {
        "easy":   {"density": 0.18, "long_rate": 0.25},
        "normal": {"density": 0.28, "long_rate": 0.30},
        "hard":   {"density": 0.45, "long_rate": 0.40},
        "expert": {"density": 0.70, "long_rate": 0.50},
    },

    "music": {
        "easy":   {"density": 0.10},
        "normal": {"density": 0.20},
        "hard":   {"density": 0.30},
        "expert": {"density": 0.40},
    },

    "otomenoinori": {
        "easy":   {"density": 0.25},
        "normal": {"density": 0.40},
        "hard":   {"density": 0.70},
        "expert": {"density": 1.05},
    },

    "trukish": {
        "normal": {"density": 0.48, "rhythm_rate": 0.20},
        "hard":   {"density": 0.85, "variation": 0.30},
        "expert": {"density": 1.20, "variation": 0.50},
    },

    "wakareno": {
        "easy":   {"density": 0.25, "long_rate": 0.15},
        "normal": {"density": 0.40, "long_rate": 0.20},
        "hard":   {"density": 0.70, "long_rate": 0.30},
        "expert": {"density": 1.05, "long_rate": 0.45},
    },
}

# ============================================================
# 曲別 DIFFICULTY を適用する関数（完全版）
# ============================================================

def apply_style_params(base_params, difficulty, song_id):
    params = dict(base_params)

    if song_id in SONG_DIFFICULTY:
        if difficulty in SONG_DIFFICULTY[song_id]:
            for k, v in SONG_DIFFICULTY[song_id][difficulty].items():
                params[k] = v

    return params
