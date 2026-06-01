"""
リソース管理モジュール

このモジュールは、画像・音声・フォントなどのリソースを一元管理します。
メモリ効率を考慮し、キャッシング機構を実装しています。

使用例:
    from resource_manager import ResourceManager
    manager = ResourceManager()
    font = manager.get_font("default")
    sound = manager.get_sound("perfect.wav")
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import pygame

from exceptions import AudioLoadError, FontError, ResourceError
from logger import get_logger

logger = get_logger(__name__)


class ResourceManager:
    """リソース管理クラス"""

    def __init__(self):
        """初期化"""
        self._fonts: Dict[str, pygame.font.Font] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._images: Dict[str, pygame.Surface] = {}

        logger.info("ResourceManager を初期化しました")

    def get_font(self, name: str, size: int = 32, path: Optional[str] = None) -> pygame.font.Font:
        """
        フォントを取得（キャッシング機構付き）

        Args:
            name: フォント名（キャッシュキー）
            size: フォントサイズ
            path: フォントファイルパス（Noneの場合はシステムフォント）

        Returns:
            pygame.font.Font: フォントオブジェクト

        Raises:
            FontError: フォント読み込みエラー
        """
        cache_key = f"{name}_{size}"

        if cache_key in self._fonts:
            return self._fonts[cache_key]

        try:
            if path and os.path.exists(path):
                font = pygame.font.Font(path, size)
            else:
                # システムフォント取得
                font = self._get_system_font(size)

            self._fonts[cache_key] = font
            logger.debug(f"フォントをロード: {name} (size={size})")
            return font

        except Exception as e:
            logger.error(f"フォント読み込みエラー: {name} - {e}")
            raise FontError(f"フォント '{name}' の読み込みに失敗しました: {e}")

    def _get_system_font(self, size: int) -> pygame.font.Font:
        """システムフォント取得（日本語対応）"""
        possible_fonts = [
            r"C:\Windows\Fonts\meiryo.ttc",
            r"C:\Windows\Fonts\yugothb.ttc",
            r"C:\Windows\Fonts\msmincho.ttc",
        ]

        for path in possible_fonts:
            if os.path.exists(path):
                return pygame.font.Font(path, size)

        # フォールバック
        return pygame.font.SysFont("arial", size)

    def get_sound(self, filename: str, path: str = "assets/sounds") -> Optional[pygame.mixer.Sound]:
        """
        サウンドを取得（キャッシング機構付き）

        Args:
            filename: ファイル名
            path: 検索パス

        Returns:
            pygame.mixer.Sound: サウンドオブジェクト（失敗時は None）
        """
        if filename in self._sounds:
            return self._sounds[filename]

        full_path = os.path.join(path, filename)

        if not os.path.exists(full_path):
            logger.warning(f"サウンドファイルが見つかりません: {full_path}")
            return None

        try:
            sound = pygame.mixer.Sound(full_path)
            self._sounds[filename] = sound
            logger.debug(f"サウンドをロード: {filename}")
            return sound

        except Exception as e:
            logger.error(f"サウンド読み込みエラー: {filename} - {e}")
            return None

    def get_image(self, filename: str, path: str = "assets/images") -> Optional[pygame.Surface]:
        """
        画像を取得（キャッシング機構付き）

        Args:
            filename: ファイル名
            path: 検索パス

        Returns:
            pygame.Surface: 画像サーフェス（失敗時は None）
        """
        if filename in self._images:
            return self._images[filename]

        full_path = os.path.join(path, filename)

        if not os.path.exists(full_path):
            logger.warning(f"画像ファイルが見つかりません: {full_path}")
            return None

        try:
            image = pygame.image.load(full_path)
            self._images[filename] = image
            logger.debug(f"画像をロード: {filename}")
            return image

        except Exception as e:
            logger.error(f"画像読み込みエラー: {filename} - {e}")
            return None

    def preload_fonts(self, sizes: list[int] = None) -> None:
        """複数サイズのフォントをプリロード"""
        if sizes is None:
            sizes = [32, 40, 48, 64]

        logger.info("フォントをプリロード中...")
        for size in sizes:
            try:
                self.get_font(f"default", size)
            except Exception as e:
                logger.warning(f"フォントプリロード失敗 (size={size}): {e}")

    def preload_sounds(self, filenames: list[str]) -> None:
        """複数サウンドをプリロード"""
        logger.info("サウンドをプリロード中...")
        for filename in filenames:
            try:
                self.get_sound(filename)
            except Exception as e:
                logger.warning(f"サウンドプリロード失敗 ({filename}): {e}")

    def clear_cache(self) -> None:
        """キャッシュをクリア"""
        self._fonts.clear()
        self._sounds.clear()
        self._images.clear()
        logger.info("リソースキャッシュをクリアしました")

    def get_memory_usage(self) -> Dict[str, int]:
        """メモリ使用量情報を返す"""
        return {
            "fonts": len(self._fonts),
            "sounds": len(self._sounds),
            "images": len(self._images),
        }


# グローバルリソースマネージャー
_resource_manager: Optional[ResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """グローバルリソースマネージャーを取得"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager
