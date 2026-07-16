import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class PauseScreen(BaseScreen):
    """
    商用仕様：ポーズ画面（完全統合版）
    BaseScreen のフェード・フォント・効果音・画面遷移を統合。
    """

    def __init__(self, manager, song):
        super().__init__(manager)
        self.song = song

        self.options = ["Resume", "Retry", "Title"]
        self.index = 0

        self.scroll_y = 0
        self.target_scroll_y = 0

    # ============================================================
    # 画面開始時
    # ============================================================

    def on_enter(self):
        super().on_enter()
        pygame.mixer.music.pause()
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
        # 半透明オーバーレイ
        screen.fill((0, 0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # タイトル
        self.center_text(
            screen,
            "PAUSED",
            size=64,
            y=int(200 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # オプションリスト
        y_base = int(320 * UI_SCALE) + self.scroll_y
        font = self.res.get_font(36, weight="medium")

        for i, opt in enumerate(self.options):
            color = UI_COLORS["text_primary"] if i == self.index else UI_COLORS["text_secondary"]
            surf = font.render(opt, True, color)

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

            # 決定
            elif event.key == pygame.K_RETURN:
                selected = self.options[self.index]

                if selected == "Resume":
                    pygame.mixer.music.unpause()
                    self.play_se("se_decide")
                    self.request_transition(("gameplay", self.song))

                elif selected == "Retry":
                    pygame.mixer.music.stop()
                    self.play_se("se_decide")
                    self.request_transition(("gameplay", self.song))

                elif selected == "Title":
                    pygame.mixer.music.stop()
                    self.play_se("se_back")
                    self.request_transition("title")

            # ESC → Resume
            elif event.key == pygame.K_ESCAPE:
                pygame.mixer.music.unpause()
                self.play_se("se_back")
                self.request_transition(("gameplay", self.song))
