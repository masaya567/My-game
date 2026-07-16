"""
商用仕様：テーマ管理モジュール（完全版・完全統合）

ゲーム全体の配色・フォント・UIスケールを統一管理する。
"""

from typing import Dict, Tuple
from utils.color.theme_colors import THEMES  # ← あなたのテーマカラー定義を利用

# ============================================================
# UI スケール設定
# ============================================================

UI_SCALE: float = 1.0  # デフォルトスケール（設定画面で変更）


# ============================================================
# 現在のテーマ名
# ============================================================

_current_theme: str = "Blue"


# ============================================================
# テーマ操作関数
# ============================================================


def set_theme(name: str) -> None:
    """テーマを変更"""
    global _current_theme
    if name in THEMES:
        _current_theme = name
        print(f"[Theme] Changed to: {_current_theme}")
    else:
        print(f"[Theme] Invalid theme name: {name}")


def get_theme() -> Dict[str, Tuple[int, int, int]]:
    """現在のテーマカラー辞書を取得"""
    return THEMES.get(_current_theme, THEMES["Blue"])


def get_color(key: str) -> Tuple[int, int, int]:
    """キーに対応する色を取得"""
    theme = get_theme()
    return theme.get(key, (255, 255, 255))


# ============================================================
# UI スケール操作
# ============================================================


def set_ui_scale(scale: float) -> None:
    """UIスケールを変更"""
    global UI_SCALE
    UI_SCALE = max(0.5, min(2.0, scale))
    print(f"[UI] Scale set to: {UI_SCALE}")


def get_ui_scale() -> float:
    """現在のUIスケールを取得"""
    return UI_SCALE


# ============================================================
# UI カラー辞書（BaseScreen で毎フレーム更新）
# ============================================================


def get_ui_colors() -> Dict[str, Tuple[int, int, int]]:
    """UI カラー辞書を返す（UI_COLORS の代替）"""
    return get_theme()
