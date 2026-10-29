"""
商用品質：判定ライン光帯（UI_SCALE対応・完全版）
"""

import pygame
import math
import colorsys
from constants import WIDTH
from utils.theme.theme import get_ui_scale


class JudgeBeam:
    def __init__(self, center_x: float, y: float, color, strength: float):
        self.scale = get_ui_scale()

        self.center_x = center_x
        self.y = y
        self.color = tuple(int(channel) for channel in color[:3])
        self.strength = max(0.0, min(1.0, float(strength)))

        # ★ UI_SCALE 対応
        self.alpha = 255 * strength
        self.height = int(42 * self.scale)

        # 光の走る位置（左右に広がる）
        self.light_offset = 0
        self.light_speed = 1800 * self.scale   # ★ スケール対応

        self.is_alive = True

        # 虹色モード
        self.rainbow = False
        self.hue = 0.0

        self._surface = None
        self._light_surface = None

    def trigger_rainbow(self):
        self.rainbow = True
        self.hue = 0.0
        self.alpha = 255

    def update(self, dt):
        # ★ UI_SCALE 対応したフェード速度
        self.alpha -= 600 * self.scale * dt
        if self.alpha <= 0:
            self.is_alive = False
            return

        # ★ UI_SCALE 対応した光の移動速度
        self.light_offset = (self.light_offset + self.light_speed * dt) % (WIDTH + int(240 * self.scale))

        if self.rainbow:
            self.hue += dt * 1.8
            if self.hue > 1.0:
                self.hue -= 1.0

            r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
            self.color = (int(r * 255), int(g * 255), int(b * 255))

            self.alpha *= 0.96
            if self.alpha < 5:
                self.rainbow = False

    def draw(self, screen):
        if not self.is_alive:
            return

        width = screen.get_width()

        if self._surface is None or self._surface.get_width() != width:
            self._surface = pygame.Surface((width, self.height), pygame.SRCALPHA)
            self._light_surface = pygame.Surface((width, self.height), pygame.SRCALPHA)

        surf = self._surface
        light_surface = self._light_surface
        surf.fill((0, 0, 0, 0))
        light_surface.fill((0, 0, 0, 0))

        # ============================================================
        # ★ 上下グラデーション（UI_SCALE対応）
        # ============================================================
        for i in range(self.height):
            grad_alpha = max(
                0,
                min(255, int(self.alpha * (1 - abs(i - self.height / 2) / (self.height / 2)))),
            )
            pygame.draw.line(surf, (*self.color, grad_alpha), (0, i), (width - 1, i))

        # ============================================================
        # ★ 横方向に走る光（UI_SCALE対応）
        # ============================================================
        glow_width = int(120 * self.scale)

        for dx in range(-glow_width, glow_width):
            x = int(self.center_x + dx + self.light_offset)
            if 0 <= x < width:
                dist = abs(dx)
                a = max(0, min(255, int(self.alpha * (1 - dist / glow_width))))
                pygame.draw.line(light_surface, (255, 255, 255, a), (x, 0), (x, self.height - 1))

        surf.blit(light_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        screen.blit(surf, (0, self.y - self.height // 2))
