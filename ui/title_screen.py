import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS
from utils.theme.theme import get_ui_scale


class TitleScreen(BaseScreen):
    """
    商用仕様：タイトル画面（完全統合版）
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.timer = 0.0
        self.alpha = 255
        self.fade_dir = -1  # 点滅方向

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

        # タイトルロゴ
        self.center_text(
            screen,
            "PIANO RHYTHM",
            size=72,
            y=int(200 * scale),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # サブタイトル
        self.center_text(
            screen,
            "CLASSICAL EDITION",
            size=36,
            y=int(300 * scale),
            color=UI_COLORS["text_secondary"],
        )

        # PRESS ENTER（点滅）
        font = self.res.get_font(36)
        press = font.render("PRESS ENTER", True, (*UI_COLORS["text_primary"], int(self.alpha)))
        screen.blit(press, (WIDTH // 2 - press.get_width() // 2, int(500 * scale)))

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:
                self.play_se("se_decide")
                self.request_transition("song_select")

            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                pygame.quit()
                exit()
