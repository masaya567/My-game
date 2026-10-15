import pygame
import math
from ui.base_screen import BaseScreen
from constants import WIDTH, UI_COLORS
from utils.theme.theme import get_ui_scale


class TitleScreen(BaseScreen):
    """
    商用仕様：タイトル画面（4項目メニュー付き）
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.timer = 0.0
        self.alpha = 255
        self.fade_dir = -1  # 点滅方向

        # ★ 4つの項目
        self.menu_items = [
            ("ゲームスタート", "song_select"),
            ("あそびかた", "how_to_play_screen"),
            ("オプション", "option_screen"),
            ("終了する", "exit"),
        ]
        self.menu_index = 0

    def on_enter(self):
        super().on_enter()
        self.play_se("se_move")

    def update(self, dt):
        self.timer += dt

        # 「PRESS ENTER」点滅アニメーション
        self.alpha += self.fade_dir * 300 * dt
        if self.alpha <= 50:
            self.alpha = 50
            self.fade_dir = 1
        elif self.alpha >= 255:
            self.alpha = 255
            self.fade_dir = -1

    def draw(self, screen):
        scale = get_ui_scale()
        screen.fill(UI_COLORS["bg_title"])

        # タイトルロゴ（揺れ）
        offset = math.sin(self.timer * 2.0) * 5 * scale
        self.center_text(
            screen,
            "ピアノリズム",
            size=52,
            y=int(150 * scale + offset),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # サブタイトル
        self.center_text(
            screen,
            "クラシックエディション",
            size=26,
            y=int(220 * scale),
            color=UI_COLORS["text_secondary"],
        )

        # ★ メニュー描画（4項目）
        base_y = int(300 * scale)
        for i, (label, _) in enumerate(self.menu_items):

            # 選択中の背景ハイライト
            if i == self.menu_index:
                highlight_rect = pygame.Rect(
                    WIDTH // 2 - int(160 * scale),
                    base_y + int(i * 55 * scale) - int(5 * scale),
                    int(320 * scale),
                    int(45 * scale),
                )
                pygame.draw.rect(
                    screen,
                    UI_COLORS["menu_highlight"],  # constants.py に追加
                    highlight_rect,
                    border_radius=8,
                )

            color = (
                UI_COLORS["text_primary"]
                if i == self.menu_index
                else UI_COLORS["text_secondary"]
            )
            size = 34 if i == self.menu_index else 28

            self.center_text(
                screen,
                label,
                size=size,
                y=base_y + int(i * 55 * scale),
                color=color,
                weight="bold" if i == self.menu_index else None,
            )

        # PRESS ENTER（点滅）
        font = self.res.get_font(28)
        press = font.render(
            "Enterで決定",
            True,
            (*UI_COLORS["text_primary"], int(self.alpha)),
        )
        screen.blit(press, (WIDTH // 2 - press.get_width() // 2, int(520 * scale)))

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # 上下移動
            if event.key == pygame.K_UP:
                self.menu_index = (self.menu_index - 1) % len(self.menu_items)
                self.play_se("se_move")

            elif event.key == pygame.K_DOWN:
                self.menu_index = (self.menu_index + 1) % len(self.menu_items)
                self.play_se("se_move")

            # 決定
            elif event.key == pygame.K_RETURN:
                label, action = self.menu_items[self.menu_index]
                self.play_se("se_decide")

                if action == "exit":
                    pygame.quit()
                    exit()
                else:
                    self.request_transition(action)

            # ESC はタイトルでは無効
            elif event.key == pygame.K_ESCAPE:
                pass
