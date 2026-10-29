"""
商用品質：リソース統合管理モジュール（完全版・最終形態）
フォント・画像・音声などのリソースを一括管理する。
"""

import sys
import os

from resource_manager.font_manager import FontManager
from resource_manager.image_manager import ImageManager
from resource_manager.sound_manager import SoundManager

# ★ アプリ化対応：BASE_DIR / ASSETS_DIR / DATA_DIR
BASE_DIR = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")


class ResourceManager:
    """
    商用品質：リソース統合管理クラス
    """

    def __init__(self):
        self.fonts = FontManager()
        self.images = ImageManager()
        self.sounds = SoundManager()

    # ============================================================
    # ★ 起動高速化：全リソースプリロード
    # ============================================================

    def preload_all(self):
        """フォント・画像・音声をすべて事前読み込みする（起動高速化）"""
        self.load_all_fonts()
        self.load_all_images()
        self.load_all_sounds()

    # ------------------------------
    # フォントプリロード
    # ------------------------------
    def load_all_fonts(self):
        font_sizes = [12, 14, 16, 18, 20, 24, 28, 32, 40, 52, 64, 72]
        weights = ["regular", "bold"]

        for size in font_sizes:
            for weight in weights:
                try:
                    self.fonts.get(size, weight)
                except Exception as e:
                    print(f"[警告] フォントプリロード失敗: size={size}, weight={weight} → {e}")

    # ------------------------------
    # 画像プリロード
    # ------------------------------
    def load_all_images(self):
        base = IMAGES_DIR
        if not os.path.exists(base):
            return

        for file in os.listdir(base):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                name = file.split(".")[0]
                try:
                    self.images.load(name)
                except Exception as e:
                    print(f"[警告] 画像プリロード失敗: {name} → {e}")

    # ------------------------------
    # 音声プリロード
    # ------------------------------
    def load_all_sounds(self):
        base = SOUNDS_DIR
        if not os.path.exists(base):
            return

        for file in os.listdir(base):
            if file.lower().endswith((".wav", ".ogg", ".mp3")):
                name = file.split(".")[0]
                try:
                    self.sounds.load(name)
                except Exception as e:
                    print(f"[警告] 音声プリロード失敗: {name} → {e}")

    # ============================================================
    # 既存 initialize()（そのまま残す）
    # ============================================================

    def initialize(self) -> None:
        """リソース初期化（必要ならプリロード）"""

        preload_images = [
            "ui/title_logo",
            "ui/button_start",
        ]

        preload_sounds = [
            "se_decide",
            "se_move",
            "se_back",
        ]

        for item in preload_images:
            try:
                self.images.load(item)
            except Exception as e:
                print(f"[警告] 画像プリロード失敗: {item} → {e}")

        for item in preload_sounds:
            try:
                self.sounds.load(item)
            except Exception as e:
                print(f"[警告] 音声プリロード失敗: {item} → {e}")

    # ============================================================
    # リソース取得
    # ============================================================

    def get_font(self, size: int, weight="regular", italic=False):
        return self.fonts.get(size, weight, italic)

    def get_image(self, name: str):
        return self.images.get(name)

    def get_sound(self, name: str):
        return self.sounds.get(name)

    # ============================================================
    # キャッシュクリア
    # ============================================================

    def clear_all(self) -> None:
        self.fonts.clear_cache()
        self.images.clear_cache()
        self.sounds.clear_cache()
