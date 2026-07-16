import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class HowToPlayScreen(BaseScreen):
    """
    商用仕様：遊び方説明画面（完全統合版）
    BaseScreen のフェード・フォント・効果音・画面遷移を統合。
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.scroll_y = 0
        self.target_scroll_y = 0

        # 説明テキスト
        self.instructions = [
            "🎵 ゲームの遊び方 🎵",
            "",
            "1. 曲を選択してプレイを開始します。",
            "2. ノーツが判定ラインに重なった瞬間にキーを押します。",
            "3. 判定は Perfect / Great / Good / Miss の4段階。",
            "4. コンボを繋げると背景が変化し、スコアが上昇します。",
            "5. 長押しノーツは押し続けて離すタイミングも重要です。",
            "6. 曲終了後、スコアと判定結果が表示されます。",
            "",
            "💡 ヒント",
            "- 設定画面でノーツ速度やキー配置を変更できます。",
            "- 練習モードではミスしてもコンボが途切れません。",
            "- AUTOモードで譜面を鑑賞することも可能です。",
            "",
            "Press ESC to return to Title.",
        ]

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
            "HOW TO PLAY",
            size=48,
            y=int(60 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # テキスト描画
        y_base = int(160 * UI_SCALE) + self.scroll_y

        for i, line in enumerate(self.instructions):
            color = UI_COLORS["text_primary"] if i == 0 else UI_COLORS["text_secondary"]
            size = 32 if i == 0 else 24

            self.center_text(
                screen, line, size=size, y=y_base + i * int(40 * UI_SCALE), color=color
            )

        # フェード描画
        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # スクロール
            if event.key == pygame.K_DOWN:
                self.target_scroll_y -= 80
                self.play_se("se_move")

            elif event.key == pygame.K_UP:
                self.target_scroll_y += 80
                self.play_se("se_move")

            # 戻る
            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("title")
