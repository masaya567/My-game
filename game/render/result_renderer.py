"""
商用品質：リザルト演出モジュール（完全版）

指数フェード、揺らぎ、バウンス、光のコア、多層グロー、加算合成を備えた高品質リザルト演出。
"""

import pygame
import math
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE


class ResultRenderer:
    """
    商用品質：リザルト演出クラス
    """

    def __init__(self, result_data):
        self.result_data = result_data

        # 背景フェード
        self.bg_alpha = 0
        self.bg_fade_speed = 0.004  # exp用

        # ランク演出
        self.rank_scale = 0.0
        self.rank_target_scale = 1.0
        self.rank_color = self._get_rank_color(result_data.get("rank", "C"))
        self.rank_wave_time = 0

        # スコア揺らぎ
        self.score_wave_time = 0

        self.active = True

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        if not self.active:
            return

        # 背景指数フェード
        self.bg_alpha = min(1.0, self.bg_alpha + self.bg_fade_speed * dt)

        # ランクのバウンス（ease-out）
        self.rank_scale += (self.rank_target_scale - self.rank_scale) * dt * 6

        # ランク揺らぎ
        self.rank_wave_time += dt

        # スコア揺らぎ
        self.score_wave_time += dt

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen, fonts):
        if not self.active:
            return

        font_small, font_medium, font_large = fonts

        # ------------------------------------------------------------
        # 背景フェード（指数＋揺らぎ）
        # ------------------------------------------------------------
        bg_alpha_int = int(255 * (self.bg_alpha**2))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*UI_COLORS["bg_select"], int(bg_alpha_int * 0.6)))
        screen.blit(overlay, (0, 0))

        # ------------------------------------------------------------
        # スコア表示（揺らぎ）
        # ------------------------------------------------------------
        score = self.result_data.get("score", 0)
        score_text = f"Score: {score:,}"

        # スコア揺らぎ（軽いsin）
        score_wave = 1.0 + math.sin(self.score_wave_time * 0.005) * 0.03
        score_surf = font_large.render(score_text, True, UI_COLORS["text_primary"])
        score_surf = pygame.transform.scale(
            score_surf,
            (int(score_surf.get_width() * score_wave), int(score_surf.get_height() * score_wave)),
        )
        screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, int(200 * UI_SCALE)))

        # ------------------------------------------------------------
        # 判定表示
        # ------------------------------------------------------------
        judgments = self.result_data.get("judgments", {})
        y_base = int(300 * UI_SCALE)
        for i, (label, value) in enumerate(judgments.items()):
            text = f"{label}: {value}"
            surf = font_medium.render(text, True, UI_COLORS["text_secondary"])
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y_base + i * int(50 * UI_SCALE)))

        # ------------------------------------------------------------
        # コンボ表示
        # ------------------------------------------------------------
        combo_text = f"Max Combo: {self.result_data.get('max_combo', 0)}"
        combo_surf = font_medium.render(combo_text, True, UI_COLORS["text_primary"])
        screen.blit(combo_surf, (WIDTH // 2 - combo_surf.get_width() // 2, int(520 * UI_SCALE)))

        # ------------------------------------------------------------
        # ランク演出（バウンス＋揺らぎ＋光）
        # ------------------------------------------------------------
        rank = self.result_data.get("rank", "C")

        # ランク揺らぎ
        wave = (math.sin(self.rank_wave_time * 0.01) + 1) * 0.5
        scale = self.rank_scale * (1.0 + wave * 0.1)

        rank_font = pygame.font.SysFont("Arial", int(180 * scale))
        rank_surf = rank_font.render(rank, True, self.rank_color)
        rank_rect = rank_surf.get_rect(center=(WIDTH // 2, int(380 * UI_SCALE)))

        # ランク光（多層グロー）
        glow_surface = pygame.Surface((rank_rect.width * 2, rank_rect.height * 2), pygame.SRCALPHA)
        cx, cy = glow_surface.get_width() // 2, glow_surface.get_height() // 2

        for i in range(40, 0, -4):
            alpha = int(80 * (i / 40))
            pygame.draw.circle(glow_surface, (*self.rank_color, alpha), (cx, cy), i)

        # 加算合成で光を描画
        screen.blit(
            glow_surface,
            (rank_rect.centerx - cx, rank_rect.centery - cy),
            special_flags=pygame.BLEND_ADD,
        )

        # ランク文字本体
        screen.blit(rank_surf, rank_rect)

    # ============================================================
    # ランクカラー取得
    # ============================================================

    def _get_rank_color(self, rank):
        colors = {
            "S": (255, 220, 100),
            "A": (120, 255, 180),
            "B": (120, 180, 255),
            "C": (180, 180, 180),
            "D": (255, 120, 120),
        }
        return colors.get(rank, (200, 200, 200))

    # ============================================================
    # リセット処理
    # ============================================================

    def reset(self):
        self.bg_alpha = 0
        self.rank_scale = 0.0
        self.rank_wave_time = 0
        self.score_wave_time = 0
        self.active = True
