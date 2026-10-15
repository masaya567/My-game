"""
商用仕様：UI マネージャ（完全統合版・テーマ対応）

BaseScreen のフェード・画面遷移・ResourceManager・テーマ切り替えを統合した
ゲーム全体の UI 管理クラス。
"""

import json
from pathlib import Path

import pygame
from constants import WIDTH, HEIGHT

# 画面クラス
from ui.title_screen import TitleScreen
from ui.song_select_screen import SongSelectScreen
from ui.difficulty_select_screen import DifficultySelectScreen  # ← 古い画面を使う
from ui.chart_preview_screen import ChartPreviewScreen
from ui.gameplay.screen import GameplayScreen
from ui.result_screen import ResultScreen
from ui.mode_select_screen import ModeSelectScreen
from ui.settings_screen import SettingsScreen
from ui.key_config_screen import KeyConfigScreen
from ui.option_screen import OptionScreen
from ui.pause_screen import PauseScreen
from ui.statistics_screen import StatisticsScreen

# リソース管理
from resource_manager.resource_manager import ResourceManager

# テーマ管理
from utils.theme.theme import set_theme, set_ui_scale

SETTINGS_PATH = Path(__file__).resolve().parent.parent / "data" / "settings.json"


class ScreenManager:
    """
    商用仕様：画面管理クラス（完全統合版・テーマ対応）
    """

    def __init__(self):
        self.resources = ResourceManager()

        self.settings = {
            "theme_color": "Blue",
            "ui_scale": 1.0,
            "note_speed": 1.0,
            "master_volume": 100,
            "key_config": {
                "Lane 1": pygame.K_d,
                "Lane 2": pygame.K_f,
                "Lane 3": pygame.K_j,
                "Lane 4": pygame.K_k,
            },
        }
        self.load_settings()

        self.screens = {}
        self.current = None

    def load_settings(self):
        try:
            with SETTINGS_PATH.open("r", encoding="utf-8") as settings_file:
                saved_settings = json.load(settings_file)
        except (OSError, ValueError):
            return

        if not isinstance(saved_settings, dict):
            return

        saved_key_config = saved_settings.pop("key_config", None)
        self.settings.update(saved_settings)
        if isinstance(saved_key_config, dict):
            defaults = self.settings["key_config"]
            defaults.update(
                {
                    lane: key
                    for lane, key in saved_key_config.items()
                    if lane in defaults and (key is None or isinstance(key, int))
                }
            )

    def save_settings(self):
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = SETTINGS_PATH.with_suffix(".tmp")
        with temporary_path.open("w", encoding="utf-8") as settings_file:
            json.dump(self.settings, settings_file, ensure_ascii=False, indent=2)
        temporary_path.replace(SETTINGS_PATH)

    # ============================================================
    # 画面登録
    # ============================================================

    def register(self, name, screen):
        self.screens[name] = screen

    # ============================================================
    # 画面切り替え（テーマ反映を統合）
    # ============================================================

    def set(self, screen_info):
        """
        screen_info:
            - "title"
            - ("gameplay", {song, difficulty})
            - ("difficulty", song)
            - ("chart_preview", {song, difficulty})
            - ("result", {...})
        """

        set_theme(self.settings.get("theme_color", "Blue"))
        set_ui_scale(self.settings.get("ui_scale", 1.0))

        # --- 画面名と引数を分解 ---
        if isinstance(screen_info, tuple):
            name, args = screen_info
        else:
            name, args = screen_info, None

        if name not in self.screens:
            print(f"[UI] Screen '{name}' not registered.")
            return

        if self.current:
            self.current.on_exit()

        screen_class = self.screens[name]

        # --- 特殊画面：ResultScreen ---
        if name == "result":
            self.current = screen_class(
                self,
                args.get("score"),
                args.get("max_combo"),
                args.get("perfect"),
                args.get("great"),
                args.get("good"),
                args.get("miss"),
                args.get("song"),
            )

        # --- DifficultyScreen は Song を受け取る ---
        elif name == "difficulty":
            self.current = screen_class(self, args)

        # --- ChartPreviewScreen / GameplayScreen は dict を受け取る ---
        elif name in ("chart_preview", "gameplay"):
            self.current = screen_class(self, args)

        # --- その他の画面は引数なし ---
        else:
            self.current = screen_class(self)

        self.current.on_enter()
        print(f"[UI] Changed to screen: {name}")

    # ============================================================
    # 画面遷移要求
    # ============================================================

    def request_transition(self, target):
        self.set(target)

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen):
        if self.current:
            self.current.draw(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if self.current:
            self.current.handle_event(event)


# ============================================================
# 初期化関数
# ============================================================

def create_manager():
    manager = ScreenManager()

    manager.resources.initialize()
    manager.screen = pygame.display.get_surface()

    manager.register("title", TitleScreen)
    manager.register("mode_select", ModeSelectScreen)
    manager.register("song_select", SongSelectScreen)

    # ★ 難易度画面は新しい DifficultyScreen を使用
    manager.register("difficulty", DifficultySelectScreen)

    manager.register("chart_preview", ChartPreviewScreen)
    manager.register("gameplay", GameplayScreen)
    manager.register("result", ResultScreen)
    manager.register("settings", SettingsScreen)
    manager.register("key_config", KeyConfigScreen)

    from ui.how_to_play_screen import HowToPlayScreen
    manager.register("how_to_play_screen", HowToPlayScreen)

    manager.register("option_screen", OptionScreen)
    manager.register("pause", PauseScreen)
    manager.register("statistics", StatisticsScreen)

    manager.set("title")
    return manager
