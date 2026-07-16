import pygame
import random
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS
from utils.theme.theme import get_ui_scale
from songs.loader.song_loader import load_all_songs


class SongSelectScreen(BaseScreen):
    """
    商用品質：曲選択カード UI（完全統合版）
    - ジャケット＋曲情報をカード化
    - 選択中カードは拡大＋影＋発光
    - 上下スライドアニメーション
    - 背景光粒子
    - 難易度選択カード UI と統一デザイン
    """


    def __init__(self, manager):
        super().__init__(manager)

        self.songs = load_all_songs()
        self.index = 0

        self.slide_offset = 0
        self.target_slide_offset = 0

        self.particles = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 1.0)]
            for _ in range(40)
        ]

    def update(self, dt):
        self.slide_offset += (self.target_slide_offset - self.slide_offset) * dt * 10

        for p in self.particles:
            p[1] += p[2] * 20 * dt
            if p[1] > HEIGHT:
                p[0] = random.randint(0, WIDTH)
                p[1] = -10

    def draw(self, screen):
        scale = get_ui_scale()

        screen.fill(UI_COLORS["bg_select"])

        # 背景光粒子
        for x, y, s in self.particles:
            pygame.draw.circle(screen, (255, 255, 255, 40), (int(x), int(y)), int(3 * s))

        # タイトル
        self.center_text(
            screen,
            "SELECT SONG",
            size=48,
            y=int(60 * scale),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        base_y = int(180 * scale)

        for i, song in enumerate(self.songs):
            is_selected = i == self.index

            card_w = int(600 * scale)
            card_h = int(160 * scale)
            x = WIDTH // 2 - card_w // 2 + int(self.slide_offset)
            y = base_y + i * int(200 * scale)

            if is_selected:
                card_w = int(card_w * 1.08)
                card_h = int(card_h * 1.08)
                x = WIDTH // 2 - card_w // 2

            rect = pygame.Rect(x, y, card_w, card_h)

            if is_selected:
                shadow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=12)
                screen.blit(shadow, (x + 6, y + 6))

            pygame.draw.rect(screen, (240, 240, 240), rect, border_radius=12)

            if is_selected:
                glow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255, 255, 255, 180), glow.get_rect(), 4, border_radius=12)
                screen.blit(glow, rect)

            jacket = getattr(song, "jacket", None)
            if jacket:
                jacket_size = int(140 * scale)
                jacket_img = pygame.transform.smoothscale(jacket, (jacket_size, jacket_size))
                screen.blit(jacket_img, (x + 20, y + 10))

            font_title = self.res.get_font(36, weight="bold")
            title_surf = font_title.render(song.title, True, (30, 30, 30))
            screen.blit(title_surf, (x + 180, y + 20))

            font_info = self.res.get_font(24)
            info = f"BPM: {song.bpm}   Length: {song.length:.1f}s"
            info_surf = font_info.render(info, True, (60, 60, 60))
            screen.blit(info_surf, (x + 180, y + 70))

            diff_surf = font_info.render("Difficulty: NORMAL", True, (80, 80, 80))
            screen.blit(diff_surf, (x + 180, y + 110))

        self.center_text(
            screen,
            "Enter: 決定   Esc: 戻る",
            size=24,
            y=int(HEIGHT - 80 * scale),
            color=UI_COLORS["text_secondary"],
        )

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.songs)
                self.target_slide_offset = -self.index * int(200 * get_ui_scale())
                self.play_se("se_move")

            elif event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.songs)
                self.target_slide_offset = -self.index * int(200 * get_ui_scale())
                self.play_se("se_move")

            elif event.key == pygame.K_RETURN:
                selected_song = self.songs[self.index]
                self.play_se("se_decide")
                self.request_transition(("difficulty", selected_song))

            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("title")
