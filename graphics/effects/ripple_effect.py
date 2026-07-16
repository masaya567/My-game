"""
商用仕様：波紋エフェクトモジュール（完全版）

ノーツ判定時に水面のような光の波紋を描画する。
"""

import pygame
import math


class RippleEffect:
    """
    商用仕様：波紋エフェクトクラス
    """

    def __init__(self, x: float, y: float, color=(120, 200, 255)):
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.radius = 0
        self.max_radius = 120
        self.timer = 0.0

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float) -> None:
        """時間経過に応じて波紋を更新"""
        self.timer += dt
        self.radius += 250 * dt
        self.alpha = max(0, 255 - int(self.timer * 600))

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen: pygame.Surface) -> None:
        """波紋エフェクトを描画"""
        if self.alpha <= 0:
            return

        ripple_surface = pygame.Surface((300, 300), pygame.SRCALPHA)

        # 波動パターン（sin波で揺らぎを表現）
        wave = (math.sin(self.timer * 6) + 1) * 0.5
        intensity = int(150 + 80 * wave)

        # 外側リング
        pygame.draw.circle(
            ripple_surface,
            (self.color[0], self.color[1], self.color[2], int(self.alpha * 0.8)),
            (150, 150),
            int(self.radius),
            3,
        )

        # 内側グロー
        for i in range(10):
            alpha = int(self.alpha * (1 - i / 10))
            pygame.draw.circle(
                ripple_surface,
                (self.color[0], self.color[1], self.color[2], alpha),
                (150, 150),
                int(self.radius * (1 - i / 15)),
                2,
            )

        # コア部分（中心の光）
        pygame.draw.circle(
            ripple_surface,
            (255, 255, 255, int(self.alpha * 0.6)),
            (150, 150),
            int(self.radius * 0.3),
        )

        screen.blit(ripple_surface, (self.x - 150, self.y - 150))
