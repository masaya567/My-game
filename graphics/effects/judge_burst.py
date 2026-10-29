"""
商用品質：判定爆発エフェクトモジュール（UI_SCALE対応・完全版）
"""

import pygame
import random
import math
from utils.theme.theme import get_ui_scale


class JudgeBurst:
    def __init__(self, x: float, y: float, color=(255, 255, 255)):
        if isinstance(x, (tuple, list)):
            x, y = x
        self.x = x
        self.y = y
        self.color = tuple(color[:3])

        # ★ UI_SCALE 対応
        self.scale = get_ui_scale()

        self.alpha = 255
        self.radius = 0
        self.max_radius = int(90 * self.scale)

        self.timer = 0.0
        self.is_alive = True

        size = self.max_radius * 2
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # ★ スパーク粒子（UI_SCALE対応）
        self.sparks = []
        for _ in range(18):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(200, 450) * self.scale     # ★速度スケール
            lifetime = random.uniform(0.25, 0.45)
            self.sparks.append(
                {
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": lifetime,
                    "radius": int(random.randint(3, 6) * self.scale),  # ★粒子サイズスケール
                }
            )

    def update(self, dt: float):
        self.timer += dt

        # ★ UI_SCALE 対応した速度
        self.radius += 450 * self.scale * dt
        self.alpha = max(0, 255 - int(self.timer * 900 * self.scale))

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

        # --- グロー層（UI_SCALE対応） ---
        pygame.draw.circle(
            burst_surface,
            (255, 255, 255, int(self.alpha * 0.8)),
            center,
            int(self.radius * 0.6),
        )

        # --- 外側リング（UI_SCALE対応） ---
        pygame.draw.circle(
            burst_surface,
            (*self.color, int(self.alpha)),
            center,
            int(self.radius),
            int(4 * self.scale),   # ★リングの太さもスケール
        )

        # --- スパーク粒子（UI_SCALE対応） ---
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
