"""
商用品質：ロングノーツ影（統合版＋pulse同期＋wobble＋AA＋キャッシュ）
"""

import pygame
import math
import pygame.gfxdraw


class LongShadow:
    def __init__(self, base_color=(120, 200, 255), alpha=70, width=60):
        self.base_color = tuple(base_color[:3])
        self.alpha = alpha
        self.width = width
        self.timer = 0.0
        self.pulse = 0.0
        self.holding = False

        # キャッシュ
        self.cached_shadow = None
        self.cached_height = None
        self.cached_color = None

    # ============================================================
    # キャッシュ生成（高さ依存＋色依存）
    # ============================================================
    def _build_cache(self, height, color):
        surf = pygame.Surface((self.width, height), pygame.SRCALPHA)

        # 影色（base_color の暗色）
        r, g, b = color
        shadow_color = (int(r * 0.05), int(g * 0.05), int(b * 0.05))
        
        # 多層影（AA＋グラデ）
        for i in range(height):
            ratio = i / height
            alpha = int(self.alpha * (1 - ratio))

            pygame.gfxdraw.box(
                surf,
                pygame.Rect(0, i, self.width, 1),
                (*shadow_color, alpha),
            )

        self.cached_shadow = surf
        self.cached_height = height
        self.cached_color = color

    # ============================================================
    # update（pulse同期）
    # ============================================================
    def update(self, dt, holding, pulse):
        self.holding = holding
        self.pulse = pulse

        if pulse is not None:
            self.timer = float(pulse)
        elif holding:
            self.timer += dt * 4
        else:
            self.timer = 0.0

    # ============================================================
    # draw（統合版＋pulse同期＋wobble）
    # ============================================================
    def draw(self, screen, x, y, height, holding):
        height = max(1, int(height))
        color = self.base_color

        # キャッシュ生成（高さ or 色が変わったら再生成）
        if (
            self.cached_shadow is None
            or self.cached_height != height
            or self.cached_color != color
        ):
            self._build_cache(height, color)

        # wobble（pulse同期）
        wobble = math.sin(self.pulse * 3.2) * 4

        # 描画
        screen.blit(
            self.cached_shadow,
            (x + wobble - self.width // 2, y),
        )
