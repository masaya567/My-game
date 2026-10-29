import pygame
import json
import os
import sys
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


# ============================================================
# ★ PyInstaller 対応 BASE_DIR
# ============================================================

def get_base_dir():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

BASE_DIR = get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")
SCORES_PATH = os.path.join(DATA_DIR, "scores.json")


# ============================================================
# ★ デフォルト統計データ
# ============================================================

DEFAULT_SCORES = {
    "plays": 0,
    "average_score": 0,
    "records": []
}


# ============================================================
# ★ scores.json の安全読み込み（破損自動復旧）
# ============================================================

def load_scores():
    os.makedirs(DATA_DIR, exist_ok=True)

    # ファイルが無い → 新規作成
    if not os.path.exists(SCORES_PATH):
        save_scores(DEFAULT_SCORES)
        return DEFAULT_SCORES.copy()

    try:
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 欠損項目を補完
        for key, value in DEFAULT_SCORES.items():
            if key not in data:
                data[key] = value

        # records が壊れている場合の補正
        if not isinstance(data.get("records"), list):
            data["records"] = []

        return data

    except Exception:
        # JSON破損 → デフォルトで再生成
        save_scores(DEFAULT_SCORES)
        return DEFAULT_SCORES.copy()


# ============================================================
# ★ scores.json の安全保存
# ============================================================

def save_scores(data):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SCORES_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        pass  # 書き込み失敗時はクラッシュさせない


# ============================================================
# ★ 統計画面（完全版）
# ============================================================

class StatisticsScreen(BaseScreen):
    """
    商用品質：統計画面（破損対策・アプリ化対応・完全統合版）
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.data = load_scores()

        self.scroll_y = 0
        self.target_scroll_y = 0

    def on_enter(self):
        super().on_enter()
        self.play_se("se_move")

    def update(self, dt):
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * dt * 10

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
            title = rec.get("title", "Unknown")
            score = rec.get("score", 0)
            text = f"{title}  -  {score} pts"

            surf = font.render(text, True, UI_COLORS["text_secondary"])
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2,
                               y_base + i * int(40 * UI_SCALE)))

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("title")

            elif event.key == pygame.K_DOWN:
                self.target_scroll_y -= int(80 * UI_SCALE)
                self.play_se("se_move")

            elif event.key == pygame.K_UP:
                self.target_scroll_y += int(80 * UI_SCALE)
                self.play_se("se_move")
