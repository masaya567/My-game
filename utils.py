"""
ユーティリティ関数
"""

import json
import os

import pygame

from constants import *


def render_fit_text(text, font, max_width, color):
    """テキスト自動縮小"""
    # 通常描画
    surf = font.render(text, True, color)

    # 収まるならそのまま返す
    if surf.get_width() <= max_width:
        return surf

    # はみ出す場合は縮小
    scale = max_width / surf.get_width()
    new_height = int(surf.get_height() * scale)

    # アンチエイリアス付きで縮小
    return pygame.transform.smoothscale(surf, (max_width, new_height))


def wrap_text(text, font, max_width):
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


def load_chart(song, difficulty="NORMAL"):
    """JSON ファイルから譜面を読み込む（ファイルなければ自動生成）

    Args:
        song: 曲データ辞書
        difficulty: 難易度（EASY, NORMAL, HARD, PRO）
    """
    base = os.path.splitext(os.path.basename(song["file"]))[0]
    chart_file = f"{base}_chart.json"

    if os.path.exists(chart_file):
        with open(chart_file, "r", encoding="utf-8") as f:
            song["chart"] = json.load(f)
        print(f"[Chart] Loaded from file: {chart_file} ({len(song['chart'])} notes)")
        return True
    else:
        # JSON ファイルがない場合は自動生成
        try:
            from chart_generator import auto_generate_chart

            chart = auto_generate_chart(song, difficulty)
            song["chart"] = chart
            print(f"[Chart] Auto-generated {difficulty}: {chart_file} ({len(chart)} notes)")
            return True
        except Exception as e:
            print(f"[Chart] Auto-generation failed for {chart_file}: {e}")
            song["chart"] = []
            return False


def get_combo_bg_color(combo):
    """コンボに応じた背景色を返す"""
    if combo < 30:
        return (80, 120, 255)  # 青
    elif combo < 60:
        return (140, 80, 255)  # 紫
    elif combo < 100:
        return (255, 120, 200)  # ピンク
    elif combo < 200:
        return (255, 180, 120)  # オレンジ
    else:
        return (255, 255, 255)  # 白発光


def get_system_font():
    """システムフォント取得（日本語対応）"""
    import os

    # Windowsシステムフォントのパスから日本語フォントを取得
    font_path = None
    possible_fonts = [
        r"C:\Windows\Fonts\meiryo.ttc",  # メイリオ
        r"C:\Windows\Fonts\yugothb.ttc",  # 游ゴシック Bold
        r"C:\Windows\Fonts\msmincho.ttc",  # MS 明朝
    ]

    for path in possible_fonts:
        if os.path.exists(path):
            return path

    # フォールバック：Noneを返す（SysFont を使用）
    return None
