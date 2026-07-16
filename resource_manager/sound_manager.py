"""
商用品質：音声管理モジュール（完全版・最終形態）

ゲーム内で使用する効果音・BGMを統一的に管理する。
"""

import pygame
from pathlib import Path


class SoundManager:
    """
    商用品質：音声管理クラス
    """

    def __init__(self):
        pygame.mixer.init()

        self.sound_cache = {}
        self.music_volume = 0.8
        self.effect_volume = 0.9

        self.base_path = Path("assets/sounds")
        self.extensions = [".wav", ".ogg", ".mp3"]

    # ============================================================
    # ファイル探索
    # ============================================================

    def _find_file(self, name: str) -> Path | None:
        """複数拡張子を探索して最初に見つかった音声ファイルを返す"""
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
    # 効果音ロード
    # ============================================================

    def load(self, name: str) -> pygame.mixer.Sound:
        """指定名の効果音をロードしてキャッシュ"""

        if name in self.sound_cache:
            return self.sound_cache[name]

        file_path = self._find_file(name)
        if file_path is None:
            print(f"[SoundManager] Warning: 効果音が見つかりません → {name}")
            silent = pygame.mixer.Sound(buffer=b"\x00\x00")
            self.sound_cache[name] = silent
            return silent

        try:
            sound = pygame.mixer.Sound(str(file_path))
        except Exception as e:
            print(f"[SoundManager] Warning: 効果音ロード失敗 → {file_path} ({e})")
            silent = pygame.mixer.Sound(buffer=b"\x00\x00")
            self.sound_cache[name] = silent
            return silent

        sound.set_volume(self.effect_volume)
        self.sound_cache[name] = sound
        return sound

    # ============================================================
    # 効果音再生
    # ============================================================

    def play(self, name: str) -> None:
        """効果音を再生"""
        sound = self.get(name)
        sound.play()

    # ============================================================
    # BGM再生
    # ============================================================

    def play_music(self, name: str, loop: bool = True) -> None:
        """BGMを再生"""

        file_path = self._find_file(name)
        if file_path is None:
            print(f"[SoundManager] Warning: BGMが見つかりません → {name}")
            return

        try:
            pygame.mixer.music.load(str(file_path))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print(f"[SoundManager] Warning: BGMロード失敗 → {file_path} ({e})")

    # ============================================================
    # 停止処理
    # ============================================================

    def stop_music(self) -> None:
        pygame.mixer.music.stop()

    def stop_all(self) -> None:
        pygame.mixer.stop()

    # ============================================================
    # 音量調整
    # ============================================================

    def set_volume(self, music: float = None, effect: float = None) -> None:
        if music is not None:
            self.music_volume = max(0.0, min(1.0, music))
            pygame.mixer.music.set_volume(self.music_volume)

        if effect is not None:
            self.effect_volume = max(0.0, min(1.0, effect))
            for sound in self.sound_cache.values():
                sound.set_volume(self.effect_volume)

    # ============================================================
    # キャッシュ取得・クリア
    # ============================================================

    def get(self, name: str) -> pygame.mixer.Sound:
        if name not in self.sound_cache:
            return self.load(name)
        return self.sound_cache[name]

    def clear_cache(self) -> None:
        self.sound_cache.clear()
