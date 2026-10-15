"""
商用品質：ロングノーツヘッド（統合版＋押し込み強化＋pulse同期＋AA）
"""

import pygame
import math
import pygame.gfxdraw


class LongHead:
    def __init__(self, base_color=(120, 200, 255)):
        self.base_color = tuple(base_color[:3])
        self.timer = 0.0
        self.pulse = 0.0
        self.holding = False

        # キャッシュ
        self.cached_base = None
        self.cached_color = None

    # ============================================================
    # キャッシュ生成（AA＋コア光＋外側グロー）
    # ============================================================
    def _build_cache(self, color):
        color = tuple(int(channel) for channel in color[:3])
        surf = pygame.Surface((60, 40), pygame.SRCALPHA)
        cx, cy = 30, 20

        # 外側グロー（多層）
        for i in range(15):
            alpha = int(120 * (1 - i / 15))
            pygame.gfxdraw.filled_ellipse(surf, cx, cy, 15 + i, 10 + i, (*color, alpha))
            pygame.gfxdraw.aaellipse(surf, cx, cy, 15 + i, 10 + i, (*color, alpha))

        # 中央コア光
        pygame.gfxdraw.filled_ellipse(surf, cx, cy, 10, 8, (*color, 255))
        pygame.gfxdraw.aaellipse(surf, cx, cy, 10, 8, (*color, 255))

        # 白い中心光
        pygame.gfxdraw.filled_ellipse(surf, cx, cy, 6, 6, (255, 255, 255, 255))
        pygame.gfxdraw.aaellipse(surf, cx, cy, 6, 6, (255, 255, 255, 255))

        # 縁取り
        pygame.draw.ellipse(surf, (255, 255, 255, 200), (15, 10, 30, 20), 2)

        self.cached_base = surf
        self.cached_color = color

    # ============================================================
    # update（pulse同期＋holding強化）
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
    # draw（統合版＋押し込み強化）
    # ============================================================
    def draw(self, screen, x, y, holding):
        color = self.base_color

        # キャッシュ生成
        if self.cached_base is None or self.cached_color != color:
            self._build_cache(color)

        surf = self.cached_base.copy()

        # ------------------------------------------------------------
        # wobble（縦揺れ）pulse同期
        # ------------------------------------------------------------
        wobble = math.sin(self.pulse * 3.5) * 6

        # ------------------------------------------------------------
        # ★ 押し込み強化：ぷにっと膨らむ
        # ------------------------------------------------------------
        if holding:
            scale = 1.0 + (0.12 * math.sin(self.timer * 20))
            scaled = pygame.transform.smoothscale(surf, (int(60 * scale), int(40 * scale)))
        else:
            scaled = surf

        # ------------------------------------------------------------
        # ★ holding時の追加グロー（pulse同期）
        # ------------------------------------------------------------
        if holding:
            pulse = (math.sin(self.timer) + 1) * 0.5
            glow = pygame.Surface((scaled.get_width(), scaled.get_height()), pygame.SRCALPHA)

            alpha = int(100 * pulse)

            pygame.gfxdraw.filled_ellipse(
                glow,
                scaled.get_width() // 2,
                scaled.get_height() // 2,
                int(20 * scale),
                int(14 * scale),
                (*color, alpha),
            )
            pygame.gfxdraw.aaellipse(
                glow,
                scaled.get_width() // 2,
                scaled.get_height() // 2,
                int(20 * scale),
                int(14 * scale),
                (*color, alpha),
            )

            scaled.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        # ------------------------------------------------------------
        # 描画
        # ------------------------------------------------------------
        screen.blit(
            scaled,
            (x - scaled.get_width() // 2 + wobble, y - scaled.get_height() // 2),
            special_flags=pygame.BLEND_ADD,
        )
