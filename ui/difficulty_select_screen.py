import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE
from utils.theme.theme import get_ui_scale


class DifficultySelectScreen(BaseScreen):
    """
    商用品質：難易度選択カード UI（折り返し＋スクロール上限 完全版）
    """

    def __init__(self, manager, song):
        super().__init__(manager)
        self.song = song

        self.difficulties = ["イージー", "ノーマル", "ハード", "エキスパート"]
        self.index = 1  # ノーマル初期選択

        self.scroll_y = 0
        self.target_scroll_y = 0

        # 難易度色テーマ
        self.diff_colors = {
            "イージー": (120, 200, 255),
            "ノーマル": (120, 255, 160),
            "ハード": (255, 200, 120),
            "エキスパート": (255, 120, 160),
        }

        # 説明文
        self.descriptions = {
            "イージー": "初心者向け。ノーツ数が少なく、ゆったり進みます。",
            "ノーマル": "標準的。リズムに慣れるのに最適です。",
            "ハード": "中級者向け。連打や細かい配置が増えます。",
            "エキスパート": "上級者向け。密度が高く、速い展開です。",
        }

    # ============================================================
    # 折り返し処理（日本語対応）
    # ============================================================

    def wrap_text(self, text, font, max_width):
        """文字幅で折り返す（日本語対応）"""
        lines = []
        current = ""
        for ch in text:
            test = current + ch
            w, _ = font.size(test)
            if w <= max_width:
                current = test
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
        return lines[:2]  # 最大2行まで

    # ============================================================
    # 画面開始時
    # ============================================================

    def on_enter(self):
        super().on_enter()
        self.play_se("se_move")

    # ============================================================
    # 更新処理（スクロール上限・下限）
    # ============================================================

    def update(self, dt):

        pass

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen):
        scale = get_ui_scale()
        screen.fill(UI_COLORS["bg_select"])

        # タイトル
        self.center_text(
            screen,
            "難易度を選択",
            size=34,
            y=int(40 * scale),
            color=UI_COLORS["title_glow"],
            weight="bold",
            max_width=WIDTH - 40,
        )

        # 曲名
        self.center_text(
            screen,
            self.song.title,
            size=22,
            y=int(95 * scale),
            color=UI_COLORS["text_primary"],
            max_width=WIDTH - 40,
        )

        # カード UI
        base_y = int(160 * scale)

        for i, diff in enumerate(self.difficulties):
            is_selected = i == self.index

            card_w = int(WIDTH * 0.86)
            card_h = int(80 * scale)
            x = WIDTH // 2 - card_w // 2
            y = base_y + i * int(93 * scale)

            if is_selected:
                card_w = int(card_w * 1.02)
                card_h = int(card_h * 1.02)
                x = WIDTH // 2 - card_w // 2

            rect = pygame.Rect(x, y, card_w, card_h)

            # 影
            if is_selected:
                shadow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=12)
                screen.blit(shadow, (x + 6, y + 6))

            # カード本体
            pygame.draw.rect(screen, self.diff_colors[diff], rect, border_radius=12)

            # 発光
            if is_selected:
                glow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255, 255, 255, 180), glow.get_rect(), 4, border_radius=12)
                screen.blit(glow, rect)

            # 難易度名
            font = self.res.get_font(24, weight="bold")
            text = font.render(diff, True, (30, 30, 30))
            screen.blit(text, (x + 18, y + 10))

            # 説明文（折り返し）
            font2 = self.res.get_font(16)
            raw_desc = self.descriptions[diff]
            lines = self.wrap_text(raw_desc, font2, max_width=int(card_w - 40))

            for j, line in enumerate(lines):
                desc = font2.render(line, True, (40, 40, 40))
                screen.blit(desc, (x + 18, y + 42 + j * 18))

        # 操作説明
        self.center_text(
            screen,
            "Enter: 決定   Esc: 戻る",
            size=18,
            y=int(HEIGHT - 60 * scale),
            color=UI_COLORS["text_secondary"],
        )

        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.difficulties)
                self.play_se("se_move")

            elif event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.difficulties)
                self.play_se("se_move")

            elif event.key == pygame.K_RETURN:
                selected_diff = self.difficulties[self.index]
                self.song.chart_mode = selected_diff
                self.song.difficulty = {
                    "イージー": "easy",
                    "ノーマル": "normal",
                    "ハード": "hard",
                    "エキスパート": "expert",
                }.get(selected_diff, "normal")
                self.play_se("se_decide")
                self.request_transition(("chart_preview", {"song": self.song, "difficulty": self.song.difficulty}))

            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("song_select")
