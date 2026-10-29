import pygame
import random
import time
import colorsys

from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, JUDGE_COLORS
from graphics.effects.judge_ring import JudgeRing
from graphics.effects.judge_burst import JudgeBurst
from graphics.effects.glow_circle import GlowCircle
from utils.color.theme_colors import SONG_COLOR_MAP
from utils.theme.theme import get_ui_scale


def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


class ResultScreen(BaseScreen):
    """
    商用品質：リザルト画面（高速化＋UIスケール対応版）
    - Rect キャッシュ化
    - font.render キャッシュ化（BaseScreen）
    - UI スケール対応
    """

    def __init__(self, manager, score, max_combo, perfect, great, good, miss, song, logic):
        super().__init__(manager)

        self.score = score
        self.score_display = 0
        self.max_combo = max_combo
        self.perfect = perfect
        self.great = great
        self.good = good
        self.miss = miss
        self.song = song

        total = perfect + great + good + miss
        self.accuracy = (perfect * 1.0 + great * 0.8 + good * 0.5) / total * 100 if total > 0 else 0

        # UI スケール
        self.scale = get_ui_scale()

        # 曲テーマカラー
        self.theme_color = SONG_COLOR_MAP.get(getattr(song, "song_id", ""), (120, 120, 255))
        self.bg_color = tuple(int(c * 0.9) for c in self.theme_color)

        # プロセカ式ランク判定
        self.logic = logic
        self.rank = self.logic.get_rank() if self.logic else "C"

        rank_colors = {
            "SS": (255, 240, 120),
            "S":  (255, 215, 0),
            "A":  JUDGE_COLORS["perfect"],
            "B":  JUDGE_COLORS["great"],
            "C":  JUDGE_COLORS["good"],
            "D":  JUDGE_COLORS["miss"],
        }

        base_rank_color = rank_colors.get(self.rank, (255, 255, 255))

        self.rank_color = (
            (base_rank_color[0] + self.theme_color[0]) // 2,
            (base_rank_color[1] + self.theme_color[1]) // 2,
            (base_rank_color[2] + self.theme_color[2]) // 2,
        )

        # ランク演出
        self.rank_scale = 0.2
        self.rank_glow = 0
        self.ring_effect = None
        self.burst_effect = None

        # 背景粒子
        self.particles = [
            GlowCircle((random.randint(0, WIDTH), random.randint(0, HEIGHT)), self.theme_color)
            for _ in range(20)
        ]

        # ジャケット
        self.jacket_shadow = getattr(song, "jacket_shadow", None)
        self.jacket_image = getattr(song, "jacket_image", None)

        # ★ 判定カード Rect キャッシュ
        self.judgment_rects = []

    def on_enter(self):
        super().on_enter()
        self.play_se("se_decide")

        # ★ Rect キャッシュ生成（UIスケール対応）
        s = self.scale
        card_width = int(158 * s)
        card_height = int(43 * s)
        gap_x = int(12 * s)
        gap_y = int(8 * s)
        start_y = int(412 * s)

        self.judgment_rects.clear()

        for i in range(4):
            col = i % 2
            row = i // 2

            x = WIDTH // 2 - card_width - gap_x // 2 + col * (card_width + gap_x)
            y = start_y + row * (card_height + gap_y)

            self.judgment_rects.append(
                pygame.Rect(x, y, card_width, card_height)
            )

    def update(self, dt):

        # スコアカウントアップ
        if self.score_display < self.score:
            diff = self.score - self.score_display
            self.score_display += int(diff * dt * 3.0)
            self.score_display = min(self.score_display, self.score)

        # ランク拡大
        if self.rank_scale < 1.0:
            self.rank_scale += dt * 2.5

        # 発光
        t = min(self.rank_scale, 1.0)
        self.rank_glow = int(255 * (t ** 0.7))

        # ★ SS 虹色演出
        if self.rank == "SS":
            hue = (time.time() * 0.5) % 1.0
            self.rank_color = hsv_to_rgb(hue, 1.0, 1.0)

            if self.ring_effect:
                self.ring_effect.color = self.rank_color
            if self.burst_effect:
                self.burst_effect.color = self.rank_color

        # 光輪・爆発
        if self.rank_scale >= 1.0 and self.ring_effect is None:
            center = (WIDTH // 2, int(HEIGHT // 2 - 70 * self.scale))
            self.ring_effect = JudgeRing(center, self.rank_color)
            self.burst_effect = JudgeBurst(center, self.rank_color)

        if self.ring_effect:
            self.ring_effect.update(dt)
        if self.burst_effect:
            self.burst_effect.update(dt)

        # 背景粒子
        for p in self.particles:
            p.update(dt)

    def draw(self, screen):
        s = self.scale

        screen.fill(self.bg_color)

        # 背景の暗いオーバーレイ
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 25, 150))
        screen.blit(overlay, (0, 0))

        # 背景粒子
        for particle in self.particles:
            particle.draw(screen)

        # タイトル（UIスケール対応）
        self.center_text(
            screen,
            "RESULT",
            size=int(20 * s),
            y=int(20 * s),
            color=(220, 235, 255),
        )
        pygame.draw.line(
            screen,
            self.theme_color,
            (int(35 * s), int(52 * s)),
            (WIDTH - int(35 * s), int(52 * s)),
            int(2 * s),
        )

        # ジャケット（UIスケール対応）
        jacket_size = int(82 * s)
        jacket_y = int(105 * s)

        if self.jacket_shadow:
            shadow = pygame.transform.smoothscale(self.jacket_shadow, (jacket_size + int(8 * s), jacket_size + int(8 * s)))
            screen.blit(shadow, shadow.get_rect(center=(WIDTH // 2, jacket_y)))

        if self.jacket_image:
            jacket = pygame.transform.smoothscale(self.jacket_image, (jacket_size, jacket_size))
            screen.blit(jacket, jacket.get_rect(center=(WIDTH // 2, jacket_y)))

        # 曲名（UIスケール対応）
        song_title = getattr(self.song, "title", "Unknown Song")
        title_surface = self.get_text(song_title, int(18 * s), (255, 255, 255), weight="bold")

        max_title_width = WIDTH - int(36 * s)
        while title_surface.get_width() > max_title_width:
            size = max(10, title_surface.get_height() - 1)
            title_surface = self.get_text(song_title, size, (255, 255, 255), weight="bold")

        screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, int(163 * s))))

        # ランク演出
        if self.ring_effect:
            self.ring_effect.draw(screen)
        if self.burst_effect:
            self.burst_effect.draw(screen)

        # ランク文字（UIスケール対応）
        rank_size = max(1, int(92 * min(self.rank_scale, 1.0) * s))
        rank_surface = self.get_text(self.rank, rank_size, self.rank_color, weight="bold")
        rank_surface.set_alpha(self.rank_glow)
        screen.blit(rank_surface, rank_surface.get_rect(center=(WIDTH // 2, int(235 * s))))

        # スコア（UIスケール対応）
        self.center_text(
            screen,
            f"{self.score_display:,}",
            size=int(32 * s),
            y=int(295 * s),
            color=(255, 255, 255),
        )
        self.center_text(
            screen,
            "SCORE",
            size=int(13 * s),
            y=int(273 * s),
            color=(170, 195, 225),
        )

        # 精度・コンボ（UIスケール対応）
        self.center_text(
            screen,
            f"精度  {self.accuracy:.2f}%",
            size=int(18 * s),
            y=int(329 * s),
            color=(100, 220, 255),
        )
        self.center_text(
            screen,
            f"MAX COMBO  {self.max_combo}",
            size=int(16 * s),
            y=int(355 * s),
            color=(255, 225, 150),
        )

        # FULL COMBO / ALL PERFECT（UIスケール対応）
        total = self.perfect + self.great + self.good + self.miss
        if total > 0 and self.perfect == total:
            badge_text = "ALL PERFECT"
            badge_color = (255, 215, 80)
        elif total > 0 and self.miss == 0:
            badge_text = "FULL COMBO"
            badge_color = (100, 235, 200)
        else:
            badge_text = None

        if badge_text:
            badge_rect = pygame.Rect(
                WIDTH // 2 - int(85 * s),
                int(377 * s),
                int(170 * s),
                int(25 * s),
            )
            pygame.draw.rect(screen, badge_color, badge_rect, width=int(1 * s), border_radius=int(12 * s))
            self.center_text(
                screen,
                badge_text,
                size=int(14 * s),
                y=badge_rect.centery,
                color=badge_color,
            )

        # ★ 判定カード（UIスケール対応）
        judgments = [
            ("PERFECT", self.perfect, JUDGE_COLORS["perfect"]),
            ("GREAT", self.great, JUDGE_COLORS["great"]),
            ("GOOD", self.good, JUDGE_COLORS["good"]),
            ("MISS", self.miss, JUDGE_COLORS["miss"]),
        ]

        for i, (label, value, color) in enumerate(judgments):
            rect = self.judgment_rects[i]
            x, y = rect.x, rect.y

            card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            card_surface.fill((15, 22, 45, 225))
            screen.blit(card_surface, rect.topleft)

            pygame.draw.rect(screen, color, rect, width=int(1 * s), border_radius=int(9 * s))

            label_surface = self.get_text(label, int(13 * s), color, weight="bold")
            screen.blit(label_surface, (x + int(10 * s), y + int(5 * s)))

            value_surface = self.get_text(f"{value:,}", int(20 * s), (255, 255, 255), weight="bold")
            value_rect = value_surface.get_rect(
                right=x + rect.width - int(10 * s),
                centery=y + rect.height // 2 + int(2 * s),
            )
            screen.blit(value_surface, value_rect)

        # 続けるボタン（UIスケール対応）
        button_rect = pygame.Rect(
            WIDTH // 2 - int(135 * s),
            HEIGHT - int(47 * s),
            int(270 * s),
            int(36 * s),
        )

        base_r, base_g, base_b = self.theme_color
        brightness = (base_r + base_g + base_b) / 3

        if brightness > 180:
            button_color = (int(base_r * 0.8), int(base_g * 0.8), int(base_b * 0.8))
            text_color = (30, 30, 30)
        else:
            button_color = (min(base_r + 40, 255), min(base_g + 40, 255), min(base_b + 40, 255))
            text_color = (255, 255, 255)

        pygame.draw.rect(screen, button_color, button_rect, border_radius=int(12 * s))
        pygame.draw.rect(screen, (230, 245, 255), button_rect, width=int(2 * s), border_radius=int(12 * s))

        text_surface = self.get_text("SPACE で続ける", int(17 * s), text_color, weight="bold")
        screen.blit(
            text_surface,
            (
                button_rect.centerx - text_surface.get_width() // 2,
                button_rect.centery - text_surface.get_height() // 2 - int(4 * s),
            ),
        )

        self.draw_fade(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.play_se("se_back")
                self.request_transition("song_select")
            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("title")
