"""
商用品質：ロングノーツ光帯描画モジュール（AA強化版・最終形態）
"""

import pygame
import math
import pygame.gfxdraw


class LongBeam:
    def __init__(self, base_color=(120, 200, 255), width: int = 60):
        self.base_color = base_color
        self.timer = 0.0
        self.width = width
        self.is_alive = True

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
        judge_color: tuple[int, int, int] | None = None,
    ) -> None:

        if not holding or height <= 0:
            return

        color = judge_color if judge_color is not None else self.base_color
        beam_surface = pygame.Surface((self.width, int(height)), pygame.SRCALPHA)
        center_x = self.width // 2

        # 中央の強い光（縦波動）
        for i in range(int(height)):
            wave = math.sin((i / 40.0) + self.timer) * 0.5 + 0.5
            intensity = 150 + int(80 * wave)
            alpha = int(90 + 80 * wave)

            pygame.draw.line(
                beam_surface,
                (intensity, intensity, 255, alpha),
                (center_x - 2, i),
                (center_x + 2, i),
                3,
            )

        # 外側の柔らかい光（AA強化）
        for i in range(8):
            alpha = int(70 * (1 - i / 8))
            width = 24 + i * 4

            rect = pygame.Rect(
                center_x - width // 2,
                0,
                width,
                int(height),
            )

            # アンチエイリアス矩形
            pygame.gfxdraw.box(beam_surface, rect, (*color, alpha))

        # 横揺れ（高さに応じて自然に）
        wobble = math.sin(self.timer * 3.5) * (3 + height * 0.002)

        screen.blit(
            beam_surface,
            (x + wobble - self.width // 2, y),
            special_flags=pygame.BLEND_ADD,
        )
