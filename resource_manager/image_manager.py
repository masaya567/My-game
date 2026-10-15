"""
商用品質：画像管理モジュール（完全版・最終形態）

ゲーム内で使用する画像を統一的にロード・キャッシュ・取得する。
"""

import pygame
from pathlib import Path
from typing import Optional


class ImageManager:
    """
    商用品質：画像管理クラス
    """

    def __init__(self):
        self.image_cache = {}
        self.scaled_cache = {}

        self.base_path = Path("assets/images")
        self.extensions = [".png", ".jpg", ".jpeg", ".webp"]

    # ============================================================
    # ファイル探索
    # ============================================================

    def _find_file(self, name: str) -> Optional[Path]:
        """複数拡張子を探索して最初に見つかったファイルを返す"""
        base = self.base_path / name

        # すでに拡張子付きならそのままチェック
        if base.exists():
            return base

        # 拡張子を自動探索
        for ext in self.extensions:
            candidate = base.with_suffix(ext)
            if candidate.exists():
                return candidate

        return None

    # ============================================================
    # 画像ロード
    # ============================================================

    def load(self, name: str) -> pygame.Surface:
        """指定名の画像をロードしてキャッシュ"""

        if name in self.image_cache:
            return self.image_cache[name]

        file_path = self._find_file(name)
        if file_path is None:
            print(f"[ImageManager] Warning: 画像が見つかりません → {name}")
            # フォールバック：透明画像
            fallback = pygame.Surface((1, 1), pygame.SRCALPHA)
            self.image_cache[name] = fallback
            return fallback

        image = pygame.image.load(str(file_path)).convert_alpha()
        self.image_cache[name] = image
        return image

    # ============================================================
    # 画像取得
    # ============================================================

    def get(self, name: str) -> pygame.Surface:
        """キャッシュ済み画像を取得（未ロードならロード）"""
        if name not in self.image_cache:
            return self.load(name)
        return self.image_cache[name]

    # ============================================================
    # スケーリング（キャッシュ対応）
    # ============================================================

    def scale(self, name: str, width: int, height: int) -> pygame.Surface:
        """指定サイズにスケーリングした画像を返す（キャッシュ対応）"""

        key = (name, width, height)
        if key in self.scaled_cache:
            return self.scaled_cache[key]

        image = self.get(name)
        scaled = pygame.transform.smoothscale(image, (width, height))
        self.scaled_cache[key] = scaled
        return scaled

    # ============================================================
    # キャッシュクリア
    # ============================================================

    def clear_cache(self) -> None:
        """画像キャッシュをクリア"""
        self.image_cache.clear()
        self.scaled_cache.clear()
