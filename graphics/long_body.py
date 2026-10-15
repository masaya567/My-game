"""
商用品質：ロングノーツ本体（統合版＋押し込み強化＋pulse同期＋AA）
"""

import pygame
import math
import pygame.gfxdraw
from constants import LANE_WIDTH


class LongBody:
    def __init__(self, base_color=(120, 200, 255), base_width=60):
        self.base_color = tuple(int(channel) for channel in base_color[:3])
        self.base_width = base_width
        self.timer = 0.0
        self.pulse = 0.0
        self.holding = False

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
    def draw(self, screen, x, head_y, height, holding):
        height = max(1, int(height))
        color = self.base_color[:3]

        # ------------------------------------------------------------
        # wobble（縦揺れ）pulse同期
        # ------------------------------------------------------------
        wobble = math.sin(self.pulse * 3.2) * 4

        # ------------------------------------------------------------
        # ★ 押し込み強化：太さアップ
        # ------------------------------------------------------------
        width = self.base_width + (8 if holding else 0)

        surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # ------------------------------------------------------------
        # ★ グラデーション（head→tail）
        # ------------------------------------------------------------
        for i in range(height):
            ratio = i / height
            factor = 0.8 + 0.2 * (1 - ratio)
            r, g, b = color
            col = (int(r * factor), int(g * factor), int(b * factor), 200)

            line = pygame.Surface((width, 1), pygame.SRCALPHA)
            line.fill(col)
            surf.blit(line, (0, i))

        # ------------------------------------------------------------
        # ★ 中央コア光（pulse同期）
        # ------------------------------------------------------------
        for i in range(height):
            t = abs(i - height / 2) / (height / 2)
            a = int(255 * (1 - t))
            core = pygame.Surface((width // 2, 1), pygame.SRCALPHA)
            core.fill((*color, a))
            surf.blit(core, (width // 4, i))

        # ------------------------------------------------------------
        # ★ 外側グロー（BLEND_ADD）
        # ------------------------------------------------------------
        glow = pygame.Surface((width, height), pygame.SRCALPHA)
        glow.fill((*color, 80))
        surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        # ------------------------------------------------------------
        # ★ 押し込み強化：中央beam（holding時のみ）
        # ------------------------------------------------------------
        if holding:
            beam_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pulse = (math.sin(self.timer) + 1) * 0.5
            beam_width = 4 + int(3 * pulse)

            for i in range(height):
                intensity = int(150 + 100 * pulse)
                alpha_beam = int(90 + 120 * pulse)

                pygame.draw.line(
                    beam_surface,
                    (intensity, intensity, 255, alpha_beam),
                    (width // 2 - beam_width // 2, i),
                    (width // 2 + beam_width // 2, i),
                    beam_width,
                )

            surf.blit(beam_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        # ------------------------------------------------------------
        # AA強化：縁取り
        # ------------------------------------------------------------
        rect = pygame.Rect(0, 0, width, height)

        pygame.gfxdraw.box(surf, rect, (255, 255, 255, 40))
        pygame.gfxdraw.rectangle(surf, rect, (255, 255, 255, 200))

        # ------------------------------------------------------------
        # 描画
        # ------------------------------------------------------------
        screen.blit(surf, (x - width // 2 + wobble, head_y))
