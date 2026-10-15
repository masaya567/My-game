"""
商用品質：フォント管理モジュール（完全版・最終形態）

ゲーム内で使用するフォントを統一的に管理する。
"""

import pygame
from pathlib import Path


class FontManager:
    """
    商用品質：フォント管理クラス
    """

    def __init__(self):
        pygame.font.init()
        self.font_cache = {}

        # フォントパス
        self.font_dir = Path("assets/fonts")

        self.font_files = {
            "regular": self.font_dir / "NotoSansJP-Regular.otf",
            "bold": self.font_dir / "NotoSansJP-Bold.ttf",
            "medium": self.font_dir / "NotoSansJP-Medium.ttf",
            "light": self.font_dir / "NotoSansJP-Light.ttf",
        }

        # デフォルトフォント
        self.default_font = self.font_files["regular"]

    # ============================================================
    # フォント取得（キャッシュ対応）
    # ============================================================

    def get(self, size: int, weight: str = "regular", italic: bool = False) -> pygame.font.Font:
        """指定フォントを取得（キャッシュ対応）"""

        # フォントファイル選択
        font_path = self.font_files.get(weight, self.default_font)

        # キャッシュキー
        key = (font_path, size, weight, italic)

        if key not in self.font_cache:
            if not font_path.exists():
                fallback_font = pygame.font.match_font("meiryo") or pygame.font.get_default_font()
                if fallback_font:
                    font = pygame.font.Font(fallback_font, size)
                else:
                    font = pygame.font.SysFont(None, size)
            else:
                font = pygame.font.Font(str(font_path), size)

            font.set_bold(weight == "bold")
            font.set_italic(italic)

            self.font_cache[key] = font

        return self.font_cache[key]

    # ============================================================
    # テキスト描画
    # ============================================================

    def render(self, text: str, size: int, color=(255, 255, 255), weight="regular", italic=False):
        """テキストを描画してSurfaceを返す"""
        font = self.get(size, weight, italic)
        return font.render(text, True, color)

    # ============================================================
    # キャッシュクリア
    # ============================================================

    def clear_cache(self):
        self.font_cache.clear()
