import pygame
import random
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS
from utils.theme.theme import get_ui_scale
from songs.loader.song_loader import load_all_songs


class SongSelectScreen(BaseScreen):
    """
    商用品質：曲選択カード UI（高速化対応版 + PyInstaller安全化 + 画面サイズ変更完全対応）
    """

    def __init__(self, manager):
        super().__init__(manager)

        self.songs = load_all_songs()
        self.index = 0

        self.slide_offset = 0
        self.target_slide_offset = 0

        self.card_gap = 125
        self.scale = get_ui_scale()

        # Rect キャッシュ
        self.card_rects = []

        # 背景粒子
        self.particles = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 1.0)]
            for _ in range(40)
        ]

    def on_enter(self):
        super().on_enter()

        # ★ 画面サイズ変更後の UI_SCALE 再計算（最重要）
        self.scale = get_ui_scale()

        self.set_background(UI_COLORS["bg_select"])

        # ★ Rect キャッシュ再生成（画面サイズ変更時のズレ防止）
        self.card_rects.clear()
        base_y = int(160 * self.scale)

        for i, song in enumerate(self.songs):
            card_w = int(WIDTH * 0.86)
            card_h = int(105 * self.scale)

            x = WIDTH // 2 - card_w // 2
            y = base_y + i * int(self.card_gap * self.scale)

            self.card_rects.append(pygame.Rect(x, y, card_w, card_h))

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

        screen.blit(self.bg_surface, (0, 0))

        # 背景光粒子
        for x, y, s in self.particles:
            pygame.draw.circle(screen, (255, 255, 255, 40), (int(x), int(y)), int(3 * s))

        # タイトル
        self.center_text(
            screen,
            "曲を選択",
            size=int(40 * scale),
            y=int(40 * scale),
            color=UI_COLORS["title_glow"],
            weight="bold",
            max_width=WIDTH - 40,
        )

        base_y = int(160 * scale)

        for i, song in enumerate(self.songs):
            is_selected = i == self.index

            # Rect キャッシュ使用
            rect = self.card_rects[i].copy()
            rect.y += int(self.slide_offset)

            card_w, card_h = rect.width, rect.height

            # 拡大処理
            if is_selected:
                card_w = int(card_w * 1.06)
                card_h = int(card_h * 1.06)
                rect = pygame.Rect(
                    rect.centerx - card_w // 2,
                    rect.centery - card_h // 2,
                    card_w,
                    card_h
                )

            x, y = rect.x, rect.y

            # 影
            if is_selected:
                shadow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=16)
                screen.blit(shadow, (x + 6, y + 6))

            # カード本体
            pygame.draw.rect(screen, (245, 245, 245), rect, border_radius=16)

            # 発光
            if is_selected:
                glow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255, 255, 255, 180), glow.get_rect(), 4, border_radius=16)
                screen.blit(glow, rect)

            # ★ ジャケット安全化（None でも描画落ちしない）
            jacket = getattr(song, "jacket", None)
            if jacket is not None:
                jacket_size = int(100 * scale)
                jacket_img = pygame.transform.smoothscale(jacket, (jacket_size, jacket_size))
                screen.blit(jacket_img, (x + 20, y + 15))
            else:
                pygame.draw.rect(
                    screen,
                    (180, 180, 180),
                    (x + 20, y + 15, int(100 * scale), int(100 * scale)),
                    border_radius=12
                )

            # 曲名
            title_text = self.fit_text(song.title, max_width=int(card_w - 165), size=int(24 * scale), weight="bold")
            title_surf = self.get_text(title_text, int(24 * scale), (30, 30, 30), weight="bold")
            screen.blit(title_surf, (x + 125, y + 12))

            # BPM / Length
            info = f"BPM {round(song.bpm)}  長さ {song.length:.1f}秒"
            info_surf = self.get_text(info, int(18 * scale), (70, 70, 70))
            screen.blit(info_surf, (x + 125, y + 46))

            # 難易度
            diff_surf = self.get_text("難易度: ノーマル", int(18 * scale), (90, 90, 90))
            screen.blit(diff_surf, (x + 125, y + 72))

        # フッター
        self.center_text(
            screen,
            "Enter: 決定   Esc: 戻る",
            size=int(20 * scale),
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
