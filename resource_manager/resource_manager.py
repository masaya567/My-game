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

        # 画像プリロード（フォルダ名 + ファイル名）
        preload_images = [
            "ui/title_logo",
            "ui/button_start",
        ]

        # 音声プリロード（SoundManager の仕様に合わせて “名前だけ”）
        preload_sounds = [
            "se_decide",
            "se_move",
            "se_back",
        ]

        # 画像ロード
        for item in preload_images:
            try:
                self.images.load(item)
            except Exception as e:
                print(f"[警告] 画像プリロード失敗: {item} → {e}")

        # 音声ロード
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
