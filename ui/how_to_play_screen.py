import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class HowToPlayScreen(BaseScreen):
    """
    商用仕様：遊び方説明画面（市販ゲーム風・完全調整版）
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.scroll_y = 0
        self.target_scroll_y = 0

        self.instructions = [
            "🎵 遊び方 🎵",
            "",
            "1. 曲を選んでプレイを開始します。",
            "2. ノーツが判定ラインに重なった瞬間にキーを押します。",
            "3. 判定は「Perfect / Great / Good / Miss」の4種類です。",
            "4. コンボを繋げると背景が変化し、スコアが上昇します。",
            "5. 長押しノーツは押し続けて、離すタイミングも重要です。",
            "6. 曲が終わるとスコアと判定結果が表示されます。",
            "",
            "💡 ヒント",
            "- 設定画面でノーツ速度やキー配置を変更できます。",
            "- 練習モードではミスしてもコンボが途切れません。",
            "- AUTOモードで譜面を鑑賞することもできます。",
            "",
            "ESCキーでタイトルに戻ります。",
            "D / F / J / K：プレイキー",
            "Qキー：プレイ中にリザルトへ移動",
        ]

    # ===== 日本語対応の自動折り返し =====
    def wrap_text(self, text, font, max_width):
        lines = []
        current_line = ""

        for ch in text:
            test_line = current_line + ch
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = ch

        if current_line:
            lines.append(current_line)

        return lines

    def on_enter(self):
        super().on_enter()
        self.play_se("se_move")

    def update(self, dt):
        # スクロールアニメーション
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * dt * 10

        # ===== スクロール上限（上に行きすぎ防止） =====
        if self.scroll_y > 0:
            self.scroll_y = 0

        # ===== スクロール下限（下に行きすぎ防止） =====
        font_heading = self.res.get_font(21, weight="bold")
        font_text = self.res.get_font(17)

        card_width = int(WIDTH * 0.94)
        max_width = card_width - int(80 * UI_SCALE)

        total_lines = 0

        for line in self.instructions:
            if line.strip() == "":
                total_lines += 1
            elif line.startswith("🎵") or line.startswith("💡"):
                total_lines += 1
            else:
                wrapped = self.wrap_text(line, font_text, max_width)
                total_lines += len(wrapped)

        # 行間
        line_height = int(40 * UI_SCALE)

        # カード高さ
        card_height = int(HEIGHT * 0.86)

        # 下限スクロール量
        min_scroll = card_height - total_lines * line_height - int(35 * UI_SCALE) - int(90 * UI_SCALE)

        if self.scroll_y < min_scroll:
            self.scroll_y = min_scroll

    def draw(self, screen):
        screen.fill(UI_COLORS["bg_select"])

        # ===== タイトル（影付きで絶対に見える） =====
        font_title = self.res.get_font(48, weight="bold")
        title_text = "遊び方"

        shadow = font_title.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(WIDTH // 2, int(35 * UI_SCALE) + 2))
        screen.blit(shadow, shadow_rect)

        title = font_title.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, int(35 * UI_SCALE)))
        screen.blit(title, title_rect)

        # ===== 説明カード背景 =====
        card_width = int(WIDTH * 0.94)
        card_height = int(HEIGHT * 0.86)
        card_x = int(WIDTH * 0.03)
        card_y = int(90 * UI_SCALE)

        card = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(card, (0, 0, 0, 140), (0, 0, card_width, card_height), border_radius=16)
        screen.blit(card, (card_x, card_y))

        # ===== テキスト描画 =====
        y_base = card_y + int(35 * UI_SCALE) + self.scroll_y
        font_heading = self.res.get_font(21, weight="bold")
        font_text = self.res.get_font(17)
        max_text_width = card_width - int(80 * UI_SCALE)

        line_index = 0
        for line in self.instructions:

            # 見出し（中央揃え）
            if line.startswith("🎵") or line.startswith("💡"):
                surf = font_heading.render(line, True, (255, 255, 255))
                text_x = WIDTH // 2 - surf.get_width() // 2
                text_y = y_base + line_index * int(40 * UI_SCALE)
                screen.blit(surf, (text_x, text_y))
                line_index += 1

            # 空行
            elif line.strip() == "":
                line_index += 1

            # 本文（左揃え＋日本語折り返し）
            else:
                wrapped_lines = self.wrap_text(line, font_text, max_text_width)
                for subline in wrapped_lines:
                    surf = font_text.render(subline, True, (255, 255, 255))
                    text_x = card_x + int(40 * UI_SCALE)
                    text_y = y_base + line_index * int(40 * UI_SCALE)
                    screen.blit(surf, (text_x, text_y))
                    line_index += 1

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.target_scroll_y -= 80
                self.play_se("se_move")
            elif event.key == pygame.K_UP:
                self.target_scroll_y += 80
                self.play_se("se_move")
            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("title")
