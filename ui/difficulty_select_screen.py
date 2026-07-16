import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class DifficultySelectScreen(BaseScreen):
    """
    商用品質：難易度選択カード UI
    - カード拡大
    - 発光
    - 影
    - スライドアニメーション
    - 難易度説明統合
    """

    def __init__(self, manager, song):
        super().__init__(manager)
        self.song = song

        self.difficulties = ["EASY", "NORMAL", "HARD", "EXPERT"]
        self.index = 1  # NORMAL を初期選択

        self.scroll_y = 0
        self.target_scroll_y = 0

        # 難易度色テーマ
        self.diff_colors = {
            "EASY": (120, 200, 255),
            "NORMAL": (120, 255, 160),
            "HARD": (255, 200, 120),
            "EXPERT": (255, 120, 160),
        }

        # 説明文
        self.descriptions = {
            "EASY": "初心者向け。ノーツ数が少なく、テンポも穏やか。",
            "NORMAL": "標準的な難易度。リズムに慣れるのに最適。",
            "HARD": "中級者向け。複雑な配置と連打が登場。",
            "EXPERT": "上級者向け。高密度ノーツと高速展開。",
        }

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
            "SELECT DIFFICULTY",
            size=48,
            y=int(60 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # 曲名
        self.center_text(
            screen,
            self.song.title,
            size=32,
            y=int(140 * UI_SCALE),
            color=UI_COLORS["text_primary"],
        )

        # カード UI
        base_y = int(240 * UI_SCALE) + self.scroll_y

        for i, diff in enumerate(self.difficulties):
            is_selected = i == self.index

            # カードサイズ
            card_w = int(600 * UI_SCALE)
            card_h = int(110 * UI_SCALE)
            x = WIDTH // 2 - card_w // 2
            y = base_y + i * int(140 * UI_SCALE)

            # 選択中は拡大
            if is_selected:
                card_w = int(card_w * 1.08)
                card_h = int(card_h * 1.08)
                x = WIDTH // 2 - card_w // 2

            rect = pygame.Rect(x, y, card_w, card_h)

            # カード色
            color = self.diff_colors[diff]

            # 影
            if is_selected:
                shadow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=12)
                screen.blit(shadow, (x + 6, y + 6))

            # カード本体
            pygame.draw.rect(screen, color, rect, border_radius=12)

            # 枠線（選択中のみ発光）
            if is_selected:
                glow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255, 255, 255, 180), glow.get_rect(), 4, border_radius=12)
                screen.blit(glow, rect)

            # 難易度名
            font = self.res.get_font(40, weight="bold")
            text = font.render(diff, True, (30, 30, 30))
            screen.blit(text, (x + 20, y + 15))

            # 説明文
            font2 = self.res.get_font(24)
            desc = font2.render(self.descriptions[diff], True, (40, 40, 40))
            screen.blit(desc, (x + 20, y + 65))

        # 操作説明
        self.center_text(
            screen,
            "Enter: 決定   Esc: 戻る",
            size=24,
            y=int(HEIGHT - 80 * UI_SCALE),
            color=UI_COLORS["text_secondary"],
        )

        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # 下キー
            if event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.difficulties)
                self.target_scroll_y = -self.index * int(140 * UI_SCALE)
                self.play_se("se_move")

            # 上キー
            elif event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.difficulties)
                self.target_scroll_y = -self.index * int(140 * UI_SCALE)
                self.play_se("se_move")

            # 決定
            elif event.key == pygame.K_RETURN:
                selected_diff = self.difficulties[self.index]
                self.play_se("se_decide")
                self.request_transition(("chart_preview", self.song))

            # 戻る
            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("song_select")
