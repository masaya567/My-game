"""
商用仕様：UI マネージャ（完全統合版・テーマ対応）

BaseScreen のフェード・画面遷移・ResourceManager・テーマ切り替えを統合した
ゲーム全体の UI 管理クラス。
"""

import pygame
from constants import WIDTH, HEIGHT

# 画面クラス
from ui.title_screen import TitleScreen
from ui.song_select_screen import SongSelectScreen
from ui.difficulty_select_screen import DifficultySelectScreen
from ui.gameplay_screen import GameplayScreen
from ui.result_screen import ResultScreen
from ui.mode_select_screen import ModeSelectScreen
from ui.settings_screen import SettingsScreen
from ui.option_screen import OptionScreen
from ui.pause_screen import PauseScreen
from ui.statistics_screen import StatisticsScreen

# リソース管理
from resource_manager.resource_manager import ResourceManager

# テーマ管理
from utils.theme.theme import set_theme, set_ui_scale


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

        self.screens = {}
        self.current = None

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
            - ("gameplay", song)
            - ("difficulty", song)
            - ("result", {score, max_combo, perfect, great, good, miss, song})
        """

        set_theme(self.settings.get("theme_color", "Blue"))
        set_ui_scale(self.settings.get("ui_scale", 1.0))

        if isinstance(screen_info, tuple):
            name, args = screen_info
        else:
            name, args = screen_info, ()

        if name not in self.screens:
            print(f"[UI] Screen '{name}' not registered.")
            return

        if self.current:
            self.current.on_exit()

        screen_class = self.screens[name].__class__

        # ResultScreen だけ特別処理
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
        else:
            # 通常画面
            if isinstance(args, dict):
                self.current = screen_class(self)
            else:
                self.current = screen_class(self, *args)

        self.current.on_enter()
        print(f"[UI] Changed to screen: {name}")

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

    manager.register("title", TitleScreen)
    manager.register("mode_select", ModeSelectScreen)
    manager.register("song_select", SongSelectScreen)
    manager.register("difficulty", DifficultySelectScreen)
    manager.register("gameplay", GameplayScreen)
    manager.register("result", ResultScreen)
    manager.register("settings", SettingsScreen)
    manager.register("option", OptionScreen)
    manager.register("pause", PauseScreen)
    manager.register("statistics", StatisticsScreen)

    manager.set("title")
    return manager
