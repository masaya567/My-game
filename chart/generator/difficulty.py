# ============================================================
# 共通 DIFFICULTY（ベース値）
# ============================================================

DIFFICULTY_BASE = {
    "easy":   {"density": 0.45, "long_rate": 0.10, "rhythm_rate": 0.10, "variation": 0.05},
    "normal": {"density": 0.58, "long_rate": 0.20, "rhythm_rate": 0.25, "variation": 0.15},
    "hard":   {"density": 0.90, "long_rate": 0.32, "rhythm_rate": 0.45, "variation": 0.30},
    "expert": {"density": 1.25, "long_rate": 0.12, "rhythm_rate": 0.45, "variation": 0.38},
}

# ============================================================
# 曲別 DIFFICULTY（13曲すべて）
# ============================================================

SONG_DIFFICULTY = {

    # 1. アラベスク第1番（123 BPM）
    "arabesque1": {
        "normal": {"density": 0.60},
        "hard":   {"density": 0.95},
        "expert": {"density": 1.30},
    },

    # 2. 地獄のオルフェ（84 BPM）
    "aux-enfers": {
        "easy":   {"density": 0.40},
        "normal": {"density": 0.55},
        "hard":   {"density": 0.85},
        "expert": {"density": 1.25},
    },

    # 3. カルメン前奏曲（126 BPM）
    "carmen": {
        "normal": {"density": 0.62, "rhythm_rate": 0.30},
        "hard":   {"density": 1.00, "rhythm_rate": 0.50},
        "expert": {"density": 1.40, "variation": 0.55},
    },

    # 4. エリーゼのために（74 BPM）
    "erize": {
        "easy":   {"density": 0.35, "long_rate": 0.20},
        "normal": {"density": 0.45, "long_rate": 0.30},
        "hard":   {"density": 0.70, "long_rate": 0.40},
        "expert": {"density": 1.00, "long_rate": 0.55},
    },

    # 5. 幻想即興曲（161 BPM）
    "fantaisie": {
        "normal": {"density": 0.70},
        "hard":   {"density": 1.20, "variation": 0.40},
        "expert": {"density": 1.60, "variation": 0.60},
    },

    # 6. G線上のアリア（60 BPM）
    "gline": {
        "easy":   {"density": 0.25, "long_rate": 0.25},
        "normal": {"density": 0.35, "long_rate": 0.35},
        "hard":   {"density": 0.55, "long_rate": 0.45},
        "expert": {"density": 0.80, "long_rate": 0.55},
    },

    # 7. ハンガリー舞曲第5番（129 BPM）
    "hungarian5": {
        "normal": {"density": 0.65, "rhythm_rate": 0.30},
        "hard":   {"density": 1.05, "variation": 0.40},
        "expert": {"density": 1.45, "variation": 0.60},
    },

    # 8. ラ・カンパネラ（172 BPM）
    "lacampanella": {
        "normal": {"density": 0.70},
        "hard":   {"density": 1.15, "variation": 0.45},
        "expert": {"density": 1.55, "variation": 0.65},
    },

    # 9. 月光ソナタ第1楽章（58 BPM）
    "moonlight": {
        "easy":   {"density": 0.25, "long_rate": 0.30},
        "normal": {"density": 0.35, "long_rate": 0.40},
        "hard":   {"density": 0.55, "long_rate": 0.50},
        "expert": {"density": 0.80, "long_rate": 0.60},
    },

    # 10. テスト曲（BPM 0）
    "music": {
        "easy":   {"density": 0.10},
        "normal": {"density": 0.20},
        "hard":   {"density": 0.30},
        "expert": {"density": 0.40},
    },

    # 11. 乙女の祈り（78 BPM）
    "otomenoinori": {
        "easy":   {"density": 0.40},
        "normal": {"density": 0.55},
        "hard":   {"density": 0.85},
        "expert": {"density": 1.20},
    },

    # 12. トルコ行進曲（126 BPM）
    "trukish": {
        "normal": {"density": 0.65, "rhythm_rate": 0.35},
        "hard":   {"density": 1.05, "variation": 0.40},
        "expert": {"density": 1.45, "variation": 0.60},
    },

    # 13. 別れの曲（99 BPM）
    "wakareno": {
        "easy":   {"density": 0.40, "long_rate": 0.20},
        "normal": {"density": 0.55, "long_rate": 0.30},
        "hard":   {"density": 0.85, "long_rate": 0.40},
        "expert": {"density": 1.20, "long_rate": 0.55},
    },
}

# ============================================================
# 曲別 DIFFICULTY を適用する関数
# ============================================================

def apply_style_params(base_params, difficulty, song_id):
    params = dict(base_params)

    if song_id in SONG_DIFFICULTY:
        if difficulty in SONG_DIFFICULTY[song_id]:
            for k, v in SONG_DIFFICULTY[song_id][difficulty].items():
                params[k] = v

    return params
