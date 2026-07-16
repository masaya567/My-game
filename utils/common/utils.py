"""
商用仕様：ユーティリティ関数（完全版・プロジェクト統合）

テキスト描画、譜面ロード、背景色、フォント取得などを統合。
"""

import json
import os
import pygame
from typing import List, Tuple, Optional, Dict

from constants import BLACK
from utils.theme.theme import get_theme

# ============================================================
# テキスト関連
# ============================================================


def render_fit_text(
    text: str, font: pygame.font.Font, max_width: int, color: Tuple[int, int, int]
) -> pygame.Surface:
    """テキスト自動縮小（アンチエイリアス対応）"""
    surf = font.render(text, True, color)
    if surf.get_width() <= max_width:
        return surf

    scale = max_width / surf.get_width()
    new_height = int(surf.get_height() * scale)
    return pygame.transform.smoothscale(surf, (max_width, new_height))


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """自動折り返し（日本語対応）"""
    chars = list(text)
    lines = []
    current = ""

    for ch in chars:
        test = current + ch
        if font.render(test, True, BLACK).get_width() > max_width:
            lines.append(current)
            current = ch
        else:
            current = test

    if current:
        lines.append(current)

    return lines


# ============================================================
# 譜面ロード（songs/charts/ に対応）
# ============================================================


def load_chart(song: Dict[str, any], difficulty: str = "NORMAL") -> bool:
    """
    JSON ファイルから譜面を読み込む（ファイルなければ自動生成）

    Args:
        song: 曲データ辞書（song_model）
        difficulty: 難易度（EASY, NORMAL, HARD, PRO）
    """

    base = os.path.splitext(os.path.basename(song.file))[0]
    chart_file = os.path.join("songs", "charts", f"{base}_chart.json")

    # JSON が存在する場合
    if os.path.exists(chart_file):
        try:
            with open(chart_file, "r", encoding="utf-8") as f:
                song.chart = json.load(f)
            print(f"[Chart] Loaded: {chart_file} ({len(song.chart)} notes)")
            return True
        except Exception as e:
            print(f"[Chart] Failed to load {chart_file}: {e}")
            song.chart = []
            return False

    # JSON がない → 自動生成
    try:
        from songs.chart.chart_generator import auto_generate_chart

        chart = auto_generate_chart(song, difficulty)
        song.chart = chart

        with open(chart_file, "w", encoding="utf-8") as f:
            json.dump(chart, f, ensure_ascii=False, indent=2)

        print(f"[Chart] Auto-generated {difficulty}: {chart_file} ({len(chart)} notes)")
        return True

    except Exception as e:
        print(f"[Chart] Auto-generation failed: {e}")
        song.chart = []
        return False


# ============================================================
# コンボ背景色（商用品質）
# ============================================================


def get_combo_bg_color(combo: int) -> Tuple[int, int, int]:
    """コンボに応じた背景色を返す（商用品質）"""
    if combo < 30:
        return (80, 120, 255)
    elif combo < 60:
        return (140, 80, 255)
    elif combo < 100:
        return (255, 120, 200)
    elif combo < 200:
        return (255, 180, 120)
    else:
        return (255, 255, 255)


# ============================================================
# テーマカラー取得（UI と連携）
# ============================================================


def get_ui_colors() -> Dict[str, Tuple[int, int, int]]:
    """現在のテーマカラー辞書を返す"""
    return get_theme()


# ============================================================
# フォント取得（フォールバック用）
# ============================================================


def get_system_font() -> Optional[str]:
    """システムフォント取得（日本語対応）"""
    possible_fonts = [
        r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\yugothb.ttc",
        r"C:\Windows\Fonts\msmincho.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for path in possible_fonts:
        if os.path.exists(path):
            return path

    return None
