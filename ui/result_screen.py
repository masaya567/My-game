import pygame
import random
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE
from graphics.effects.judge_ring import JudgeRing
from graphics.effects.judge_burst import JudgeBurst
from graphics.effects.glow_circle import GlowCircle
from utils.jacket.jacket_generator import load_jacket


class ResultScreen(BaseScreen):
    """
    商用品質：リザルト画面（全部入り）
    - ランク演出（拡大 → 発光 → 光輪 → 爆発）
    - スコアカウントアップ
    - 背景光粒子
    - 判定カードUI
    - 曲ジャケット表示
    """

    def __init__(self, manager, score, max_combo, perfect, great, good, miss, song):
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

        # ランク判定
        if self.accuracy >= 97:
            self.rank = "S"
            self.rank_color = (255, 215, 0)
        elif self.accuracy >= 90:
            self.rank = "A"
            self.rank_color = (120, 200, 255)
        elif self.accuracy >= 80:
            self.rank = "B"
            self.rank_color = (120, 255, 180)
        elif self.accuracy >= 70:
            self.rank = "C"
            self.rank_color = (255, 180, 120)
        else:
            self.rank = "D"
            self.rank_color = (200, 100, 100)

        # ランク演出
        self.rank_scale = 0.2
        self.rank_glow = 0
        self.ring_effect = None
        self.burst_effect = None

        # 背景光粒子
        self.particles = [
            GlowCircle(
                (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                (80, 120, 255),
                random.randint(10, 25),
            )
            for _ in range(25)
        ]

        # 曲ジャケット
        self.jacket = load_jacket(song["file"])

    # ============================================================
    # 画面開始時
    # ============================================================

    def on_enter(self):
        super().on_enter()
        self.play_se("se_decide")

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):

        # スコアカウントアップ（ease-out）
        if self.score_display < self.score:
            diff = self.score - self.score_display
            self.score_display += int(diff * dt * 4)
            if self.score_display > self.score:
                self.score_display = self.score

        # ランク拡大
        if self.rank_scale < 1.0:
            self.rank_scale += dt * 2.5

        # ランク発光
        self.rank_glow = min(255, self.rank_glow + dt * 300)

        # 光輪・爆発演出
        if self.rank_scale >= 1.0 and self.ring_effect is None:
            self.ring_effect = JudgeRing((WIDTH // 2, 180), self.rank_color)
            self.burst_effect = JudgeBurst((WIDTH // 2, 180), self.rank_color)

        if self.ring_effect:
            self.ring_effect.update(dt)
        if self.burst_effect:
            self.burst_effect.update(dt)

        # 背景粒子
        for p in self.particles:
            p.update(dt)

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen):

        # 背景
        screen.fill((230, 235, 255))

        # 光粒子
        for p in self.particles:
            p.draw(screen)

        # 曲ジャケット
        if self.jacket:
            jacket_surf = pygame.transform.smoothscale(self.jacket, (180, 180))
            screen.blit(jacket_surf, (WIDTH // 2 - 90, 40))

        # ランク
        font_rank = self.res.get_font(int(160 * self.rank_scale), weight="bold")
        rank_surf = font_rank.render(self.rank, True, self.rank_color)
        rank_surf.set_alpha(int(self.rank_glow))
        rank_rect = rank_surf.get_rect(center=(WIDTH // 2, 180))
        screen.blit(rank_surf, rank_rect)

        # 光輪・爆発
        if self.ring_effect:
            self.ring_effect.draw(screen)
        if self.burst_effect:
            self.burst_effect.draw(screen)

        # スコア
        self.center_text(
            screen, f"Score: {self.score_display}", size=48, y=340, color=(60, 120, 255)
        )

        # 精度
        self.center_text(
            screen, f"Accuracy: {self.accuracy:.2f}%", size=36, y=400, color=(60, 120, 255)
        )

        # 判定カードUI
        card_y = 460
        for label, value, color in [
            ("Perfect", self.perfect, UI_COLORS["judge_perfect"]),
            ("Great", self.great, UI_COLORS["judge_great"]),
            ("Good", self.good, UI_COLORS["judge_good"]),
            ("Miss", self.miss, UI_COLORS["judge_miss"]),
        ]:
            pygame.draw.rect(
                screen, (255, 255, 255), (WIDTH // 2 - 150, card_y, 300, 40), border_radius=10
            )
            self.center_text(screen, f"{label}: {value}", size=26, y=card_y + 20, color=color)
            card_y += 50

        # 続行ボタン
        pygame.draw.rect(screen, (80, 120, 255), (WIDTH // 2 - 150, 620, 300, 50), border_radius=20)
        self.center_text(screen, "SPACE → Continue", size=24, y=645, color=(255, 255, 255))

        # フェード
        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.play_se("se_back")
                self.request_transition("song_select")

            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("title")
