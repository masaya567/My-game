import pygame
import math
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS
from utils.theme.theme import get_ui_scale


class TitleScreen(BaseScreen):
    """
    商用仕様：タイトル画面（4項目メニュー付き・完全版）
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.timer = 0.0
        self.alpha = 255
        self.fade_dir = -1

        self.menu_items = [
            ("ゲームスタート", "song_select"),
            ("あそびかた", "how_to_play_screen"),
            ("オプション", "option_screen"),
            ("終了する", "exit"),
        ]
        self.menu_index = 0

        self.scale = get_ui_scale()

    def on_enter(self):
        super().on_enter()
        self.set_background(UI_COLORS["bg_title"])
        self.play_se("se_move")
        self.scale = get_ui_scale()

    def update(self, dt):
        self.timer += dt

        # PRESS ENTER 点滅
        self.alpha += self.fade_dir * 300 * dt
        if self.alpha <= 50:
            self.alpha = 50
            self.fade_dir = 1
        elif self.alpha >= 255:
            self.alpha = 255
            self.fade_dir = -1

    def draw(self, screen):
        scale = self.scale
        screen.blit(self.bg_surface, (0, 0))

        # タイトルロゴ（揺れ）
        offset = math.sin(self.timer * 2.0) * 5 * scale
        self.center_text(
            screen,
            "ピアノリズム",
            size=int(52 * scale),
            y=int(140 * scale + offset),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # サブタイトル
        self.center_text(
            screen,
            "クラシックエディション",
            size=int(26 * scale),
            y=int(210 * scale),
            color=UI_COLORS["text_secondary"],
        )

        # ============================================================
        # ★ メニュー群の中央配置（市販仕様）
        # ============================================================
        item_h = int(55 * scale)
        total_h = len(self.menu_items) * item_h
        base_y = HEIGHT // 2 - total_h // 2

        for i, (label, _) in enumerate(self.menu_items):

            # ★ Rect を毎フレーム生成（ズレ防止）
            rect = pygame.Rect(
                WIDTH // 2 - int(160 * scale),
                base_y + i * item_h,
                int(320 * scale),
                item_h
            )

            # ハイライト
            if i == self.menu_index:
                pygame.draw.rect(
                    screen,
                    UI_COLORS["menu_highlight"],
                    rect,
                    border_radius=8,
                )

            # テキスト
            color = UI_COLORS["text_primary"] if i == self.menu_index else UI_COLORS["text_secondary"]
            size = int(34 * scale) if i == self.menu_index else int(28 * scale)

            self.center_text(
                screen,
                label,
                size=size,
                y=base_y + i * item_h,
                color=color,
                weight="bold" if i == self.menu_index else None,
            )

        # ============================================================
        # ★ PRESS ENTER（メニューの下に黄金比で配置）
        # ============================================================
        press_y = base_y + total_h + int(80 * scale)

        bg_r, bg_g, bg_b = UI_COLORS["bg_title"]
        brightness = (bg_r + bg_g + bg_b) / 3
        text_color = (255, 255, 255) if brightness < 128 else (20, 20, 20)

        press = self.get_text("Enterで決定", int(28 * scale), text_color)
        press.set_alpha(int(self.alpha))

        screen.blit(
            press,
            (WIDTH // 2 - press.get_width() // 2, press_y)
        )

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                self.menu_index = (self.menu_index - 1) % len(self.menu_items)
                self.play_se("se_move")

            elif event.key == pygame.K_DOWN:
                self.menu_index = (self.menu_index + 1) % len(self.menu_items)
                self.play_se("se_move")

            elif event.key == pygame.K_RETURN:
                label, action = self.menu_items[self.menu_index]
                self.play_se("se_decide")

                if action == "exit":
                    pygame.quit()
                    exit()
                else:
                    self.request_transition(action)
