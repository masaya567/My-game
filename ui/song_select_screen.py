import pygame
import random
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS
from utils.theme.theme import get_ui_scale
from songs.loader.song_loader import load_all_songs


class SongSelectScreen(BaseScreen):
    """
    商用品質：曲選択カード UI（最終統合版）
    - ジャケット＋曲情報カード
    - 選択中カードは拡大＋影＋発光
    - スライドアニメーション（曲数に応じて自動調整）
    - 背景光粒子
    """

    def __init__(self, manager):
        super().__init__(manager)

        self.songs = load_all_songs()
        self.index = 0

        self.slide_offset = 0
        self.target_slide_offset = 0

        self.card_gap = 125
        self.scale = get_ui_scale()

        self.particles = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 1.0)]
            for _ in range(40)
        ]

    def update(self, dt):
        # スライドアニメーション
        self.slide_offset += (self.target_slide_offset - self.slide_offset) * dt * 10

        # 背景粒子
        for p in self.particles:
            p[1] += p[2] * 20 * dt
            if p[1] > HEIGHT:
                p[0] = random.randint(0, WIDTH)
                p[1] = -10

    def draw(self, screen):
        scale = self.scale

        screen.fill(UI_COLORS["bg_select"])

        # 背景光粒子
        for x, y, s in self.particles:
            pygame.draw.circle(screen, (255, 255, 255, 40), (int(x), int(y)), int(3 * s))

        # タイトル
        self.center_text(
            screen,
            "曲を選択",
            size=40,
            y=int(40 * scale),
            color=UI_COLORS["title_glow"],
            weight="bold",
            max_width=WIDTH - 40,
        )

        base_y = int(160 * scale)

        for i, song in enumerate(self.songs):
            is_selected = i == self.index

            # カードサイズ
            card_w = int(WIDTH * 0.86)
            card_h = int(105 * scale)

            # 拡大処理
            if is_selected:
                card_w = int(card_w * 1.06)
                card_h = int(card_h * 1.06)

            x = WIDTH // 2 - card_w // 2
            y = base_y + i * int(self.card_gap * scale) + int(self.slide_offset)

            rect = pygame.Rect(x, y, card_w, card_h)

            # 影
            if is_selected:
                shadow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=16)
                screen.blit(shadow, (x + 6, y + 6))

            # カード本体
            pygame.draw.rect(screen, (245, 245, 245), rect, border_radius=16)

            # 発光（角丸と完全一致）
            if is_selected:
                glow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255, 255, 255, 180), glow.get_rect(), 4, border_radius=16)
                screen.blit(glow, rect)

            # ジャケット
            jacket = getattr(song, "jacket", None)
            if jacket:
                jacket_size = int(100 * scale)
                jacket_img = pygame.transform.smoothscale(jacket, (jacket_size, jacket_size))
                screen.blit(jacket_img, (x + 20, y + 15))

            # 曲名
            font_title = self.res.get_font(24, weight="bold")
            title_text = self.fit_text(
                song.title, max_width=int(card_w - 165), size=24, weight="bold"
            )
            title_surf = font_title.render(title_text, True, (30, 30, 30))
            screen.blit(title_surf, (x + 125, y + 12))

            # BPM / Length
            font_info = self.res.get_font(18)
            info = f"BPM {song.bpm}  長さ {song.length:.1f}秒"
            info_surf = font_info.render(info, True, (70, 70, 70))
            screen.blit(info_surf, (x + 125, y + 46))

            # 難易度
            diff_surf = font_info.render("難易度: ノーマル", True, (90, 90, 90))
            screen.blit(diff_surf, (x + 125, y + 72))

        # フッター
        self.center_text(
            screen,
            "Enter: 決定   Esc: 戻る",
            size=20,
            y=int(HEIGHT - 70 * scale),
            color=UI_COLORS["text_secondary"],
        )

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.songs)
                self.target_slide_offset = -self.index * int(self.card_gap * self.scale)
                self.play_se("se_move")

            elif event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.songs)
                self.target_slide_offset = -self.index * int(self.card_gap * self.scale)
                self.play_se("se_move")

            elif event.key == pygame.K_RETURN:
                selected_song = self.songs[self.index]
                self.play_se("se_decide")
                self.request_transition(("difficulty", selected_song))

            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("title")
