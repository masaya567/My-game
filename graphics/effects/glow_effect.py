"""
商用品質：発光エフェクトモジュール（完全版・最終形態）

ノーツ判定・コンボ・背景などで使用される汎用発光エフェクト。
"""

import pygame
import math


class GlowEffect:
    def __init__(self, x: float, y: float, color=(120, 200, 255), radius: int = 80):
        self.x = x
        self.y = y
        self.color = tuple(int(channel) for channel in color[:3])

        self.base_radius = radius
        self.radius = radius * 0.6
        self.max_radius = radius * 1.4

        self.alpha = 255
        self.timer = 0.0

        self.wave_speed = 4.0
        self.fade_speed = 400.0

        self.is_alive = True
        self._surface = pygame.Surface(
            (int(self.max_radius * 2), int(self.max_radius * 2)), pygame.SRCALPHA
        )

    def update(self, dt: float):
        self.timer += dt

        wave = (math.sin(self.timer * self.wave_speed) + 1) * 0.5
        self.radius = self.base_radius * (0.6 + wave * 0.4)

        self.alpha = max(0, self.alpha - self.fade_speed * dt)

        if self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen: pygame.Surface):
        if not self.is_alive:
            return

        size = int(self.max_radius * 2)
        glow_surface = self._surface
        glow_surface.fill((0, 0, 0, 0))
        center = (size // 2, size // 2)

        layers = 12
        for i in range(layers):
            ratio = 1 - (i / layers)
            alpha = int(self.alpha * ratio)
            radius = int(self.radius * ratio)
            pygame.draw.circle(
                glow_surface,
                (*self.color, alpha),
                center,
                radius,
            )

        pygame.draw.circle(
            glow_surface,
            (255, 255, 255, int(self.alpha * 0.8)),
            center,
            int(self.radius * 0.4),
        )

        screen.blit(
            glow_surface,
            (self.x - size // 2, self.y - size // 2),
            special_flags=pygame.BLEND_ADD,
        )
