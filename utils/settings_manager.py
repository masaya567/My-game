"""
商用品質：Settings Manager（アプリ化対応・破損自動復旧）
"""

import os
import sys
import json

# ============================================================
# ★ PyInstaller 対応 BASE_DIR
# ============================================================

def get_base_dir():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

BASE_DIR = get_base_dir()
if getattr(sys, "frozen", False):
    appdata_dir = os.environ.get("LOCALAPPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Local"))
    DATA_DIR = os.path.join(appdata_dir, "PianoTiles", "data")
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")

# ============================================================
# ★ デフォルト設定（ゲーム全体で使う）
# ============================================================

DEFAULT_SETTINGS = {
    "master_volume": 0.8,
    "bgm_volume": 0.8,
    "se_volume": 0.8,
    "note_speed": 1.0,
    "ui_scale": 1.0,
    "key_config": {
        "Lane 1": 100,
        "Lane 2": 102,
        "Lane 3": 106,
        "Lane 4": 107,
    },
}


# ============================================================
# ★ 設定ファイルの読み込み（破損時は自動復旧）
# ============================================================

def load_settings():
    # data フォルダが無い場合は作成
    os.makedirs(DATA_DIR, exist_ok=True)

    # ファイルが無い → 新規作成
    if not os.path.exists(SETTINGS_PATH):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 欠けている項目を補完
        for key, value in DEFAULT_SETTINGS.items():
            if key not in data:
                data[key] = value

        return data

    except Exception:
        # JSON破損 → デフォルトで再生成
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()


# ============================================================
# ★ 設定ファイルの保存（安全書き込み）
# ============================================================

def save_settings(data):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        # 書き込み失敗時はクラッシュさせない
        pass


# ============================================================
# ★ 設定の更新（UIから呼び出す）
# ============================================================

def update_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
