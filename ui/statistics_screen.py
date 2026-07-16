import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE
import json
import os


class StatisticsScreen(BaseScreen):
    """
    商用仕様：統計画面（完全統合版）
    BaseScreen のフェード・フォント・効果音・画面遷移を統合。
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.data = self.load_statistics()

        self.scroll_y = 0
        self.target_scroll_y = 0

    # ============================================================
    # データ読み込み
    # ============================================================

    def load_statistics(self):
        path = os.path.join("data", "scores.json")
        if not os.path.exists(path):
            return {"plays": 0, "average_score": 0, "records": []}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"plays": 0, "average_score": 0, "records": []}

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
            "STATISTICS",
            size=48,
            y=int(60 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # プレイ回数・平均スコア
        self.center_text(
            screen,
            f"Total Plays: {self.data.get('plays', 0)}",
            size=32,
            y=int(160 * UI_SCALE),
            color=UI_COLORS["text_primary"],
        )

        self.center_text(
            screen,
            f"Average Score: {self.data.get('average_score', 0)}",
            size=32,
            y=int(210 * UI_SCALE),
            color=UI_COLORS["text_primary"],
        )

        # スコア履歴リスト
        y_base = int(300 * UI_SCALE) + self.scroll_y
        font = self.res.get_font(24)

        records = self.data.get("records", [])

        for i, rec in enumerate(records[-10:][::-1]):  # 最新10件を逆順で表示
            text = f"{rec.get('title', 'Unknown')}  -  {rec.get('score', 0)} pts"
            surf = font.render(text, True, UI_COLORS["text_secondary"])
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y_base + i * int(40 * UI_SCALE)))

        # フェード描画
        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # 戻る
            if event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("title")

            # スクロール
            elif event.key == pygame.K_DOWN:
                self.target_scroll_y -= int(80 * UI_SCALE)
                self.play_se("se_move")

            elif event.key == pygame.K_UP:
                self.target_scroll_y += int(80 * UI_SCALE)
                self.play_se("se_move")
