import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class SettingsScreen(BaseScreen):
    """
    商用仕様：設定画面（完全統合版）
    音量・ノーツ速度・テーマカラーなどを変更できる。
    """

    def __init__(self, manager):
        super().__init__(manager)

        # manager.settings に保存される設定値を読み込む
        self.options = [
            {
                "name": "Master Volume",
                "key": "master_volume",
                "value": manager.settings.get("master_volume", 100),
                "min": 0,
                "max": 100,
                "step": 5,
            },
            {
                "name": "Note Speed",
                "key": "note_speed",
                "value": manager.settings.get("note_speed", 1.0),
                "min": 0.5,
                "max": 2.0,
                "step": 0.1,
            },
            {
                "name": "Theme Color",
                "key": "theme_color",
                "value": manager.settings.get("theme_color", "Blue"),
                "choices": ["Blue", "Pink", "Green", "Gold"],
            },
        ]

        self.index = 0
        self.scroll_y = 0
        self.target_scroll_y = 0

    # ============================================================
    # 画面開始時
    # ============================================================

    def on_enter(self):
        super().on_enter()
        self.play_se("se_move")

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * dt * 10

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen):
        screen.fill(UI_COLORS["bg_select"])

        # タイトル
        self.center_text(
            screen,
            "SETTINGS",
            size=48,
            y=int(60 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # オプションリスト
        y_base = int(180 * UI_SCALE) + self.scroll_y
        font = self.res.get_font(36, weight="medium")

        for i, opt in enumerate(self.options):
            color = UI_COLORS["text_primary"] if i == self.index else UI_COLORS["text_secondary"]
            text = f"{opt['name']}: {opt['value']}"
            surf = font.render(text, True, color)

            text_x = WIDTH // 2 - surf.get_width() // 2
            text_y = y_base + i * int(70 * UI_SCALE)
            screen.blit(surf, (text_x, text_y))

            # 選択中の光輪
            if i == self.index:
                glow = pygame.Surface(
                    (surf.get_width() + 40, surf.get_height() + 10), pygame.SRCALPHA
                )
                pygame.draw.rect(glow, (*UI_COLORS["text_primary"], 120), glow.get_rect(), 4)
                glow_rect = glow.get_rect(center=(WIDTH // 2, text_y + surf.get_height() // 2))
                screen.blit(glow, glow_rect)

        # フェード描画
        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # 下キー
            if event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.options)
                self.target_scroll_y = -self.index * int(70 * UI_SCALE)
                self.play_se("se_move")

            # 上キー
            elif event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.options)
                self.target_scroll_y = -self.index * int(70 * UI_SCALE)
                self.play_se("se_move")

            # 左右キーで値変更
            elif event.key == pygame.K_LEFT:
                self.modify_option(-1)
                self.play_se("se_move")

            elif event.key == pygame.K_RIGHT:
                self.modify_option(1)
                self.play_se("se_move")

            # ESC → 保存して戻る
            elif event.key == pygame.K_ESCAPE:
                self.save_settings()
                self.play_se("se_back")
                self.request_transition("title")

    # ============================================================
    # オプション変更処理
    # ============================================================

    def modify_option(self, direction):
        opt = self.options[self.index]

        if "choices" in opt:
            choices = opt["choices"]
            current_index = choices.index(opt["value"])
            new_index = (current_index + direction) % len(choices)
            opt["value"] = choices[new_index]
        else:
            new_value = opt["value"] + opt["step"] * direction
            opt["value"] = round(max(opt["min"], min(opt["max"], new_value)), 2)

    # ============================================================
    # 設定保存
    # ============================================================

    def save_settings(self):
        """manager.settings に保存する"""
        for opt in self.options:
            self.manager.settings[opt["key"]] = opt["value"]
