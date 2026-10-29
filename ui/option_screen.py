import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class OptionScreen(BaseScreen):
    """
    商用仕様：オプション画面（HowToPlayScreenと完全統一版）
    """

    def __init__(self, manager):
        super().__init__(manager)

        self.options = [
            {"name": "判定タイミング", "key": "judge_timing",
             "value": manager.settings.get("judge_timing", 0.18),
             "min": 0.10, "max": 0.30, "step": 0.01},

            {"name": "ノーツサイズ", "key": "note_size",
             "value": manager.settings.get("note_size", 25),
             "min": 15, "max": 40, "step": 1},

            {"name": "背景の明るさ", "key": "bg_brightness",
             "value": manager.settings.get("bg_brightness", 0.8),
             "min": 0.3, "max": 1.0, "step": 0.05},

            {"name": "テーマカラー", "key": "theme",
             "value": manager.settings.get("theme", "Blue"),
             "choices": ["Blue", "Pink", "Green", "Gold"]},
        ]

        self.index = 0
        self.scroll_y = 0
        self.target_scroll_y = 0

    # ===== 日本語折り返し =====
    def wrap_text(self, text, font, max_width):
        lines = []
        current = ""
        for ch in text:
            test = current + ch
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
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
        # オプション行数
        option_lines = len(self.options)

        # 説明文の行数（折り返し含む）
        font_desc = self.res.get_font(18)
        card_width = int(WIDTH * 0.94)
        max_width = card_width - int(80 * UI_SCALE)

        desc_text = self.get_description(self.options[self.index]["name"])
        wrapped_desc = []
        for line in desc_text.split("\n"):
            wrapped_desc.extend(self.wrap_text(line, font_desc, max_width))

        desc_lines = len(wrapped_desc)

        # 総行数
        total_lines = option_lines + desc_lines + 2  # 余白 + 見出し分

        # 行間
        line_height = int(40 * UI_SCALE)

        # カード高さ
        card_height = int(HEIGHT * 0.86)

        # 下限スクロール量
        min_scroll = -(total_lines * line_height - card_height)

        if self.scroll_y < min_scroll:
            self.scroll_y = min_scroll

    def draw(self, screen):
        screen.fill(UI_COLORS["bg_select"])

        # ===== タイトル（HowToPlayと同じ） =====
        font_title = self.res.get_font(48, weight="bold")
        title_text = "オプション設定"

        shadow = font_title.render(title_text, True, (0, 0, 0))
        screen.blit(shadow, shadow.get_rect(center=(WIDTH // 2, int(35 * UI_SCALE) + 2)))

        title = font_title.render(title_text, True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, int(35 * UI_SCALE))))

        # ===== カード背景（HowToPlayと同じサイズ） =====
        card_width = int(WIDTH * 0.94)
        card_height = int(HEIGHT * 0.86)
        card_x = int(WIDTH * 0.03)
        card_y = int(90 * UI_SCALE)

        card = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(card, (0, 0, 0, 140), (0, 0, card_width, card_height), border_radius=16)
        screen.blit(card, (card_x, card_y))

        # ===== オプションリスト（カード内スクロール） =====
        y_base = card_y + int(35 * UI_SCALE) + self.scroll_y
        font_opt = self.res.get_font(22)
        max_width = card_width - int(80 * UI_SCALE)

        line_index = 0
        for i, opt in enumerate(self.options):

            text = f"{opt['name']}: {opt['value']}"
            surf = font_opt.render(text, True, (255, 255, 255))

            text_x = card_x + int(40 * UI_SCALE)
            text_y = y_base + line_index * int(40 * UI_SCALE)

            # ハイライト（HowToPlayと同じ控えめの強調）
            if i == self.index:
                highlight = pygame.Surface(
                    (surf.get_width() + 40, surf.get_height() + 10),
                    pygame.SRCALPHA
                )
                highlight.fill((120, 170, 255, 110))
                screen.blit(highlight, highlight.get_rect(
                    center=(text_x + surf.get_width() // 2, text_y + surf.get_height() // 2)
                ))

            screen.blit(surf, (text_x, text_y))
            line_index += 1

        # ===== 説明文（HowToPlayと同じ折り返し方式） =====
        current_opt = self.options[self.index]["name"]
        desc_text = self.get_description(current_opt)

        font_desc = self.res.get_font(18)
        wrapped_lines = []
        for line in desc_text.split("\n"):
            wrapped_lines.extend(self.wrap_text(line, font_desc, max_width))

        # 説明文はカード内の下部に表示
        desc_start_y = y_base + line_index * int(40 * UI_SCALE) + int(20 * UI_SCALE)

        for i, line in enumerate(wrapped_lines):
            surf = font_desc.render(line, True, (240, 240, 240))
            screen.blit(surf, (card_x + int(40 * UI_SCALE),
                               desc_start_y + i * int(32 * UI_SCALE)))

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.options)
                self.target_scroll_y -= 40
                self.play_se("se_move")

            elif event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.options)
                self.target_scroll_y += 40
                self.play_se("se_move")

            elif event.key == pygame.K_LEFT:
                self.modify_option(-1)
                self.play_se("se_move")

            elif event.key == pygame.K_RIGHT:
                self.modify_option(1)
                self.play_se("se_move")

            elif event.key == pygame.K_ESCAPE:
                self.save_settings()
                self.play_se("se_back")
                self.request_transition("title")

    def modify_option(self, direction):
        opt = self.options[self.index]
        if "choices" in opt:
            choices = opt["choices"]
            idx = choices.index(opt["value"])
            opt["value"] = choices[(idx + direction) % len(choices)]
        else:
            new_value = opt["value"] + opt["step"] * direction
            opt["value"] = round(max(opt["min"], min(opt["max"], new_value)), 2)

    def get_description(self, name):
        descriptions = {
            "判定タイミング": "ノーツを押すタイミングの厳しさを調整します。\n値が小さいほど厳しく、大きいほど緩くなります。",
            "ノーツサイズ": "ノーツの大きさを変更します。\n大きいほど見やすく、小さいほど難しくなります。",
            "背景の明るさ": "プレイ中の背景の明るさを調整します。\n暗くするとノーツが見やすくなります。",
            "テーマカラー": "ゲーム全体の色テーマを変更します。\nBlue / Pink / Green / Gold から選択できます。",
        }
        return descriptions.get(name, "")

    def save_settings(self):
        for opt in self.options:
            self.manager.settings[opt["key"]] = opt["value"]
        save_settings = getattr(self.manager, "save_settings", None)
        if callable(save_settings):
            save_settings()
