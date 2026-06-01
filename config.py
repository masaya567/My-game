"""
ゲーム設定モジュール

このモジュールは、ゲーム全体の設定を管理します。
外部ファイルから設定を読み込み、実行時に変更可能です。

使用例:
    from config import Config
    config = Config.load()
    print(config.screen.width)
    print(config.game.difficulty)
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class ScreenConfig:
    """画面設定"""

    width: int = 400
    height: int = 600
    fps: int = 60
    title: str = "Piano Tiles"


@dataclass
class GameConfig:
    """ゲーム設定"""

    difficulty: str = "NORMAL"
    speed_level: int = 3
    auto_save: bool = True
    debug_mode: bool = False


@dataclass
class AudioConfig:
    """音声設定"""

    master_volume: float = 1.0
    bgm_volume: float = 0.8
    se_volume: float = 0.9
    enable_sound: bool = True


@dataclass
class KeyConfig:
    """キー設定"""

    lane1: str = "d"
    lane2: str = "f"
    lane3: str = "j"
    lane4: str = "k"

    def to_dict(self) -> Dict[str, str]:
        """辞書に変換"""
        return {
            "lane1": self.lane1,
            "lane2": self.lane2,
            "lane3": self.lane3,
            "lane4": self.lane4,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "KeyConfig":
        """辞書から生成"""
        return cls(**data)


@dataclass
class Config:
    """ゲーム全体設定"""

    screen: ScreenConfig = field(default_factory=ScreenConfig)
    game: GameConfig = field(default_factory=GameConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    keys: KeyConfig = field(default_factory=KeyConfig)

    # 設定ファイルパス
    _config_path: str = "config.json"

    def save(self) -> None:
        """設定をファイルに保存"""
        data = {
            "screen": self.screen.__dict__,
            "game": self.game.__dict__,
            "audio": self.audio.__dict__,
            "keys": self.keys.to_dict(),
        }

        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls) -> "Config":
        """設定をファイルから読み込む"""
        config = cls()

        if os.path.exists(config._config_path):
            try:
                with open(config._config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 各設定を更新
                if "screen" in data:
                    config.screen = ScreenConfig(**data["screen"])
                if "game" in data:
                    config.game = GameConfig(**data["game"])
                if "audio" in data:
                    config.audio = AudioConfig(**data["audio"])
                if "keys" in data:
                    config.keys = KeyConfig.from_dict(data["keys"])

            except Exception as e:
                print(f"設定ファイル読み込みエラー: {e}")

        return config

    @classmethod
    def default(cls) -> "Config":
        """デフォルト設定を返す"""
        return cls()
