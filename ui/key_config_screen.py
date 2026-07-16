import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class KeyConfigScreen(BaseScreen):
    """
    商用仕様：キー設定画面（完全統合版）
    BaseScreen のフェード・フォント・効果音・画面遷移を統合。
    """

    def __init__(self, manager):
        super().__init__(manager)

        # manager に保存されているキー設定を読み込む
        self.keys = ["Lane 1", "Lane 2", "Lane 3", "Lane 4"]
        self.bindings = manager.key_config.copy()

        self.index = 0
        self.waiting_input = False

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
            "KEY CONFIG",
            size=48,
            y=int(60 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # キー設定リスト
        y_base = int(180 * UI_SCALE) + self.scroll_y
        font = self.res.get_font(32, weight="medium")

        for i, lane in enumerate(self.keys):
            color = UI_COLORS["text_primary"] if i == self.index else UI_COLORS["text_secondary"]

            key_name = (
                pygame.key.name(self.bindings[lane]).upper() if self.bindings[lane] else "None"
            )
            text = f"{lane}: {key_name}"

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

        # 状態表示
        status = (
            "Press a key to assign..."
            if self.waiting_input
            else "Use ↑↓ to select, Enter to change"
        )
        self.center_text(
            screen, status, size=24, y=int(520 * UI_SCALE), color=UI_COLORS["text_secondary"]
        )

        # フェード描画
        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # キー割り当て待機中
            if self.waiting_input:
                self.bindings[self.keys[self.index]] = event.key
                self.waiting_input = False
                self.play_se("se_decide")
                return

            # 下キー
            if event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.keys)
                self.target_scroll_y = -self.index * int(70 * UI_SCALE)
                self.play_se("se_move")

            # 上キー
            elif event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.keys)
                self.target_scroll_y = -self.index * int(70 * UI_SCALE)
                self.play_se("se_move")

            # Enter → 割り当て開始
            elif event.key == pygame.K_RETURN:
                self.waiting_input = True
                self.play_se("se_decide")

            # R → リセット
            elif event.key == pygame.K_r:
                self.bindings = {k: None for k in self.keys}
                self.play_se("se_back")

            # ESC → 保存して戻る
            elif event.key == pygame.K_ESCAPE:
                # manager に保存
                self.manager.key_config = self.bindings.copy()
                self.play_se("se_back")
                self.request_transition("settings")
