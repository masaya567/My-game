"""
商用品質：発光エフェクトモジュール（完全版・最終形態）

ノーツ判定・コンボ・背景などで使用される汎用発光エフェクト。
"""

import pygame
import math


class GlowEffect:
    """
    商用品質：発光エフェクトクラス
    """

    def __init__(self, x: float, y: float, color=(120, 200, 255), radius: int = 80):
        self.x = x
        self.y = y
        self.color = color

        self.base_radius = radius
        self.radius = radius * 0.6  # 初期は少し小さく
        self.max_radius = radius * 1.4

        self.alpha = 255
        self.timer = 0.0

        self.wave_speed = 4.0
        self.fade_speed = 400.0

        self.is_alive = True  # ★商用品質：生存判定

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float) -> None:
        """時間経過に応じて発光を更新"""
        self.timer += dt

        # 波動による半径変化
        wave = (math.sin(self.timer * self.wave_speed) + 1) * 0.5
        self.radius = self.base_radius * (0.6 + wave * 0.4)

        # フェードアウト
        self.alpha = max(0, self.alpha - self.fade_speed * dt)

        if self.alpha <= 0:
            self.is_alive = False

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen: pygame.Surface) -> None:
        """発光エフェクトを描画"""
        if not self.is_alive:
            return

        size = int(self.max_radius * 2)
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # 波動による光の強度変化
        wave = (math.sin(self.timer * self.wave_speed) + 1) * 0.5
        intensity = 150 + int(80 * wave)

        # 多層グロー（高速化版）
        layers = 12
        for i in range(layers):
            ratio = 1 - (i / layers)
            alpha = int(self.alpha * ratio)
            radius = int(self.radius * ratio)

            pygame.draw.circle(
                glow_surface,
                (self.color[0], self.color[1], self.color[2], alpha),
                (size // 2, size // 2),
                radius,
            )

        # コア部分（強い光）
        pygame.draw.circle(
            glow_surface,
            (255, 255, 255, int(self.alpha * 0.8)),
            (size // 2, size // 2),
            int(self.radius * 0.4),
        )

        screen.blit(glow_surface, (self.x - size // 2, self.y - size // 2))
