import pygame
import math
from ui.base_screen import BaseScreen
from constants import WIDTH, UI_COLORS
from utils.theme.theme import get_ui_scale

# ★ 自動アップデート
from utils.update_checker import check_update, download_new_version


class TitleScreen(BaseScreen):
    """
    商用仕様：タイトル画面（4項目メニュー付き）
    """

    def __init__(self, manager):
        super().__init__(manager)
        self.timer = 0.0
        self.alpha = 255
        self.fade_dir = -1  # 点滅方向

        # ★ 4つの項目
        self.menu_items = [
            ("ゲームスタート", "song_select"),
            ("あそびかた", "how_to_play_screen"),
            ("オプション", "option_screen"),
            ("終了する", "exit"),
        ]
        self.menu_index = 0

        # ★ Rect キャッシュ用
        self.menu_rects = []

    def on_enter(self):
        super().on_enter()

        # ★ 自動アップデートチェック
        has_update, info = check_update()
        if has_update:
            print(f"[UPDATE] 新しいバージョンがあります: {info}")
            ok = download_new_version()
            if ok:
                print("[UPDATE] アップデート完了。再起動してください。")

        self.set_background(UI_COLORS["bg_title"])   # ★背景キャッシュ化
        self.play_se("se_move")

        # ★ Rect キャッシュ生成（高速化）
        self.scale = get_ui_scale()
        base_y = int(300 * self.scale)

        self.menu_rects.clear()
        for i in range(len(self.menu_items)):
            rect = pygame.Rect(
                WIDTH // 2 - int(160 * self.scale),
                base_y + int(i * 55 * self.scale) - int(5 * self.scale),
                int(320 * self.scale),
                int(45 * self.scale),
            )
            self.menu_rects.append(rect)

    def update(self, dt):
        self.timer += dt

        # 「PRESS ENTER」点滅アニメーション
        self.alpha += self.fade_dir * 300 * dt
        if self.alpha <= 50:
            self.alpha = 50
            self.fade_dir = 1
        elif self.alpha >= 255:
            self.alpha = 255
            self.fade_dir = -1

    def draw(self, screen):
        scale = self.scale
        screen.blit(self.bg_surface, (0, 0))   # ★高速化：背景キャッシュ

        # タイトルロゴ（揺れ）
        offset = math.sin(self.timer * 2.0) * 5 * scale
        self.center_text(
            screen,
            "ピアノリズム",
            size=52,
            y=int(150 * scale + offset),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # サブタイトル
        self.center_text(
            screen,
            "クラシックエディション",
            size=26,
            y=int(220 * scale),
            color=UI_COLORS["text_secondary"],
        )

        # ★ メニュー描画（Rect キャッシュ使用）
        base_y = int(300 * scale)
        for i, (label, _) in enumerate(self.menu_items):

            # 選択中の背景ハイライト（キャッシュした Rect を使う）
            if i == self.menu_index:
                pygame.draw.rect(
                    screen,
                    UI_COLORS["menu_highlight"],
                    self.menu_rects[i],
                    border_radius=8,
                )

            color = (
                UI_COLORS["text_primary"]
                if i == self.menu_index
                else UI_COLORS["text_secondary"]
            )
            size = 34 if i == self.menu_index else 28

            self.center_text(
                screen,
                label,
                size=size,
                y=base_y + int(i * 55 * scale),
                color=color,
                weight="bold" if i == self.menu_index else None,
            )

        # PRESS ENTER（点滅）
        bg_r, bg_g, bg_b = UI_COLORS["bg_title"]
        brightness = (bg_r + bg_g + bg_b) / 3
        text_color = (255, 255, 255) if brightness < 128 else (20, 20, 20)

        press = self.get_text("Enterで決定", 28, text_color)
        press.set_alpha(int(self.alpha))
        screen.blit(press, (WIDTH // 2 - press.get_width() // 2, int(520 * scale)))

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # 上下移動
            if event.key == pygame.K_UP:
                self.menu_index = (self.menu_index - 1) % len(self.menu_items)
                self.play_se("se_move")

            elif event.key == pygame.K_DOWN:
                self.menu_index = (self.menu_index + 1) % len(self.menu_items)
                self.play_se("se_move")

            # 決定
            elif event.key == pygame.K_RETURN:
                label, action = self.menu_items[self.menu_index]
                self.play_se("se_decide")

                if action == "exit":
                    pygame.quit()
                    exit()
                else:
                    self.request_transition(action)

            # ESC はタイトルでは無効
            elif event.key == pygame.K_ESCAPE:
                pass
