import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class ModeSelectScreen(BaseScreen):
    """
    商用仕様：モード選択画面（完全統合版）
    BaseScreen のフェード・フォント・効果音・画面遷移を統合。
    """

    def __init__(self, manager):
        super().__init__(manager)

        self.modes = ["STANDARD", "TRAINING", "AUTO", "REPLAY"]
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
            "SELECT MODE",
            size=48,
            y=int(60 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # モードリスト
        y_base = int(200 * UI_SCALE) + self.scroll_y
        font = self.res.get_font(40, weight="medium")

        for i, mode in enumerate(self.modes):
            color = UI_COLORS["text_primary"] if i == self.index else UI_COLORS["text_secondary"]
            surf = font.render(mode, True, color)

            text_x = WIDTH // 2 - surf.get_width() // 2
            text_y = y_base + i * int(80 * UI_SCALE)
            screen.blit(surf, (text_x, text_y))

            # 選択中の光輪
            if i == self.index:
                glow = pygame.Surface(
                    (surf.get_width() + 40, surf.get_height() + 10), pygame.SRCALPHA
                )
                pygame.draw.rect(glow, (*UI_COLORS["text_primary"], 120), glow.get_rect(), 4)
                glow_rect = glow.get_rect(center=(WIDTH // 2, text_y + surf.get_height() // 2))
                screen.blit(glow, glow_rect)

        # 説明文
        desc = self.get_mode_description(self.modes[self.index])
        self.center_text(
            screen, desc, size=24, y=int(500 * UI_SCALE), color=UI_COLORS["text_secondary"]
        )

        # フェード描画
        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # 下キー
            if event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.modes)
                self.target_scroll_y = -self.index * int(80 * UI_SCALE)
                self.play_se("se_move")

            # 上キー
            elif event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.modes)
                self.target_scroll_y = -self.index * int(80 * UI_SCALE)
                self.play_se("se_move")

            # 決定
            elif event.key == pygame.K_RETURN:
                selected_mode = self.modes[self.index]
                self.play_se("se_decide")
                self.request_transition(("song_select", selected_mode))

            # 戻る
            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("title")

    # ============================================================
    # モード説明
    # ============================================================

    def get_mode_description(self, mode):
        descriptions = {
            "STANDARD": "通常プレイモード。スコアを競います。",
            "TRAINING": "練習モード。ミスしてもコンボが途切れません。",
            "AUTO": "自動演奏モード。譜面を鑑賞できます。",
            "REPLAY": "過去のプレイを再生します。",
        }
        return descriptions.get(mode, "")
