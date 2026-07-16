"""
商用品質：ロングノーツ本体描画モジュール（AA強化版・最終形態）
"""

import pygame
import math
import pygame.gfxdraw


class LongBody:
    """
    商用品質：ロングノーツ本体描画クラス（AA強化版）
    """

    def __init__(self, base_color=(120, 200, 255), width: int = 60):
        self.base_color = base_color
        self.width = width
        self.timer = 0.0

    def update(self, dt: float, holding: bool) -> None:
        if holding:
            self.timer += dt * 4
        else:
            self.timer = 0.0

    def draw(
        self,
        screen: pygame.Surface,
        x: float,
        y: float,
        height: float,
        holding: bool,
        color: tuple[int, int, int] | None = None,
    ) -> None:

        color = color or self.base_color
        body_surface = pygame.Surface((self.width, int(height)), pygame.SRCALPHA)

        pulse = (math.sin(self.timer) + 1) * 0.5 if holding else 0

        # グラデーションボディ
        for i in range(int(height)):
            c = 170 + int(60 * (i / max(1, height)))
            alpha = 180 + int(60 * pulse)
            pygame.draw.line(
                body_surface,
                (color[0], c, color[2], alpha),
                (0, i),
                (self.width, i),
            )

        # 発光帯（押下中のみ）
        if holding:
            beam_surface = pygame.Surface((self.width, int(height)), pygame.SRCALPHA)
            for i in range(int(height)):
                intensity = 150 + int(80 * pulse)
                alpha = int(90 + 80 * pulse)
                pygame.draw.line(
                    beam_surface,
                    (intensity, intensity, 255, alpha),
                    (self.width // 2 - 2, i),
                    (self.width // 2 + 2, i),
                    3,
                )
            body_surface.blit(beam_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        # ============================================================
        # AA強化：縁取りをアンチエイリアス化
        # ============================================================

        rect = pygame.Rect(0, 0, self.width, int(height))

        # 内側の薄い白枠（柔らかい光）
        pygame.gfxdraw.box(body_surface, rect, (255, 255, 255, 40))

        # 外側の白い縁取り（AA）
        pygame.gfxdraw.rectangle(body_surface, rect, (255, 255, 255, 200))

        # ============================================================

        screen.blit(body_surface, (x, y))
