import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class DifficultyScreen(BaseScreen):
    """
    商用仕様：難易度選択画面（完全統合版）
    BaseScreen のフェード・フォント・効果音・画面遷移を統合。
    """

    def __init__(self, manager, song):
        super().__init__(manager)

        self.song = song
        self.index = 0

        # 難易度一覧
        self.levels = ["easy", "normal", "hard", "expert"]

        # スクロール演出
        self.scroll_y = 0
        self.target_scroll_y = 0

    def on_enter(self):
        super().on_enter()
        self.play_se("se_move")

    def update(self, dt):
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * dt * 10

    def draw(self, screen):
        screen.fill(UI_COLORS["bg_select"])

        # 曲名
        self.center_text(
            screen,
            self.song.title,
            size=48,
            y=int(60 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # 難易度タイトル
        self.center_text(
            screen,
            "Select Difficulty",
            size=32,
            y=int(150 * UI_SCALE),
            color=UI_COLORS["text_primary"],
        )

        # 難易度リスト
        y_base = int(240 * UI_SCALE) + self.scroll_y

        for i, level in enumerate(self.levels):
            color = UI_COLORS["text_primary"] if i == self.index else UI_COLORS["text_secondary"]

            font = self.res.get_font(48, weight="medium")
            surf = font.render(level.upper(), True, color)

            text_x = WIDTH // 2 - surf.get_width() // 2
            text_y = y_base + i * int(80 * UI_SCALE)

            screen.blit(surf, (text_x, text_y))

            if i == self.index:
                glow = pygame.Surface(
                    (surf.get_width() + 40, surf.get_height() + 10), pygame.SRCALPHA
                )
                pygame.draw.rect(glow, (*UI_COLORS["text_primary"], 120), glow.get_rect(), 4)
                glow_rect = glow.get_rect(center=(WIDTH // 2, text_y + surf.get_height() // 2))
                screen.blit(glow, glow_rect)

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.levels)
                self.target_scroll_y = -self.index * int(80 * UI_SCALE)
                self.play_se("se_move")

            elif event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.levels)
                self.target_scroll_y = -self.index * int(80 * UI_SCALE)
                self.play_se("se_move")

            elif event.key == pygame.K_RETURN:
                selected = self.levels[self.index]
                self.play_se("se_decide")

                self.request_transition((
                    "chart_preview",
                    {
                        "song": self.song,
                        "difficulty": self.song.difficulty,
                    }
                ))

            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("song_select")
