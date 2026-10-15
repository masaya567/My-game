"""
商用品質：判定爆発エフェクトモジュール（完全版・最終形態）

ノーツ判定時に発生する爆発光エフェクトを描画する。
"""

import pygame
import random
import math


class JudgeBurst:
    def __init__(self, x: float, y: float, color=(255, 255, 255)):
        if isinstance(x, (tuple, list)):
            x, y = x
        self.x = x
        self.y = y
        self.color = tuple(color[:3])

        self.alpha = 255
        self.radius = 0
        self.max_radius = 90

        self.timer = 0.0
        self.is_alive = True
        size = self.max_radius * 2
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # スパーク粒子
        self.sparks = []
        for _ in range(18):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(200, 450)
            lifetime = random.uniform(0.25, 0.45)
            self.sparks.append(
                {
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": lifetime,
                    "radius": random.randint(3, 6),
                }
            )

    def update(self, dt: float):
        self.timer += dt
        self.radius += 450 * dt
        self.alpha = max(0, 255 - int(self.timer * 900))

        for s in self.sparks:
            s["life"] -= dt
            s["vx"] *= 0.96
            s["vy"] *= 0.96

        if self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen: pygame.Surface):
        if not self.is_alive:
            return

        size = int(self.max_radius * 2)
        burst_surface = self.surface
        burst_surface.fill((0, 0, 0, 0))
        center = (size // 2, size // 2)

        pygame.draw.circle(
            burst_surface,
            (255, 255, 255, int(self.alpha * 0.8)),
            center,
            int(self.radius * 0.6),
        )

        pygame.draw.circle(
            burst_surface,
            (*self.color, int(self.alpha)),
            center,
            int(self.radius),
            4,
        )

        for s in self.sparks:
            if s["life"] > 0:
                sx = self.x + s["vx"] * 0.015
                sy = self.y + s["vy"] * 0.015
                pygame.draw.circle(
                    burst_surface,
                    (*self.color, int(self.alpha)),
                    (int(sx - self.x + size // 2), int(sy - self.y + size // 2)),
                    s["radius"],
                )

        screen.blit(
            burst_surface,
            (self.x - size // 2, self.y - size // 2),
            special_flags=pygame.BLEND_ADD,
        )
