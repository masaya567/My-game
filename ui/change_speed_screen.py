import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class ChangeSpeedScreen(BaseScreen):
    """
    商用仕様：ノーツ速度変更画面（完全統合版）
    BaseScreen のフェード・フォント・効果音・画面遷移を統合。
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.speed = manager.note_speed  # 現在の速度を反映
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
            "CHANGE NOTE SPEED",
            size=48,
            y=int(60 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # 現在の速度表示
        self.center_text(
            screen,
            f"Current Speed: x{self.speed:.1f}",
            size=36,
            y=int(200 * UI_SCALE),
            color=UI_COLORS["text_primary"],
        )

        # 説明文
        desc_lines = [
            "↑ / ↓ : 速度を変更",
            "Enter : 保存して戻る",
            "ESC : 設定画面に戻る",
        ]

        y_base = int(320 * UI_SCALE) + self.scroll_y
        for i, line in enumerate(desc_lines):
            self.center_text(
                screen,
                line,
                size=24,
                y=y_base + i * int(40 * UI_SCALE),
                color=UI_COLORS["text_secondary"],
            )

        # プレビューライン
        pygame.draw.line(
            screen,
            UI_COLORS["accent"],
            (WIDTH // 2 - 150, int(500 * UI_SCALE)),
            (WIDTH // 2 + 150, int(500 * UI_SCALE)),
            3,
        )

        # ノーツプレビュー（速度に応じて移動）
        note_y = int(500 * UI_SCALE - (pygame.time.get_ticks() / 10 * self.speed) % 400)
        pygame.draw.circle(screen, UI_COLORS["highlight"], (WIDTH // 2, note_y), 12)

        # フェード描画
        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # 上キー → 速度アップ
            if event.key == pygame.K_UP:
                self.speed = min(5.0, round(self.speed + 0.1, 1))
                self.play_se("se_move")

            # 下キー → 速度ダウン
            elif event.key == pygame.K_DOWN:
                self.speed = max(0.5, round(self.speed - 0.1, 1))
                self.play_se("se_move")

            # Enter → 保存して戻る
            elif event.key == pygame.K_RETURN:
                self.manager.note_speed = self.speed
                self.play_se("se_decide")
                self.request_transition("settings")

            # ESC → 戻る
            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("settings")
