"""
商用品質：リソース統合管理モジュール（完全版・最終形態）

フォント・画像・音声などのリソースを一括管理する。
"""

from resource_manager.font_manager import FontManager
from resource_manager.image_manager import ImageManager
from resource_manager.sound_manager import SoundManager


class ResourceManager:
    """
    商用品質：リソース統合管理クラス
    """

    def __init__(self):
        self.fonts = FontManager()
        self.images = ImageManager()
        self.sounds = SoundManager()

    # ============================================================
    # 初期化処理（プリロード）
    # ============================================================

    def initialize(self) -> None:
        """リソース初期化（必要ならプリロード）"""

        preload_list = [
            "ui/title_logo",
            "ui/button_start",
            "sounds/select",
        ]

        for item in preload_list:
            try:
                # 画像（拡張子自動探索）
                self.images.load(item)

                # 音声（拡張子自動探索）
                self.sounds.load(item)

            except Exception as e:
                print(f"[警告] リソースプリロード失敗: {item} → {e}")

    # ============================================================
    # リソース取得
    # ============================================================

    def get_font(self, size: int, weight="regular", italic=False):
        """フォント取得（FontManager の完全版に対応）"""
        return self.fonts.get(size, weight, italic)

    def get_image(self, name: str):
        """画像取得（ImageManager の完全版に対応）"""
        return self.images.get(name)

    def get_sound(self, name: str):
        """音声取得（SoundManager の完全版に対応）"""
        return self.sounds.get(name)

    # ============================================================
    # キャッシュクリア
    # ============================================================

    def clear_all(self) -> None:
        """全リソースキャッシュをクリア"""
        self.fonts.clear_cache()
        self.images.clear_cache()
        self.sounds.clear_cache()
