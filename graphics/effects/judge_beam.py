"""
商用品質：判定ライン光帯描画モジュール（完全版＋虹色化＋RGBA安全化）
"""

import pygame
import math
import colorsys
from constants import WIDTH


class JudgeBeam:
    """
    商用品質：判定ライン光帯（EffectManager と完全同期版）
    + コンボ2000時の虹色化（色相回転）
    + RGBA を pygame.draw に渡さない完全安全版
    """

    def __init__(self, center_x: float, y: float, color, strength: float):
        self.center_x = center_x
        self.y = y
        self.color = tuple(int(channel) for channel in color[:3])
        self.strength = max(0.0, min(1.0, float(strength)))

        self.alpha = 255 * strength
        self.height = 42

        # 光の走る位置（左右に広がる）
        self.light_offset = 0
        self.light_speed = 1800

        self.is_alive = True

        # ★ 虹色モード（コンボ2000専用）
        self.rainbow = False
        self.hue = 0.0
        self._surface = None
        self._light_surface = None

    # ============================================================
    # 虹色化トリガー
    # ============================================================

    def trigger_rainbow(self):
        self.rainbow = True
        self.hue = 0.0
        self.alpha = 255  # 再度強く光らせる

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        # フェードアウト
        self.alpha -= 600 * dt
        if self.alpha <= 0:
            self.is_alive = False
            return

        # 光の移動を画面幅で循環させ、エフェクトが消失しないようにする。
        self.light_offset = (self.light_offset + self.light_speed * dt) % (WIDTH + 240)

        # 虹色モード
        if self.rainbow:
            self.hue += dt * 1.8
            if self.hue > 1.0:
                self.hue -= 1.0

            r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
            self.color = (int(r * 255), int(g * 255), int(b * 255))

            self.alpha *= 0.96
            if self.alpha < 5:
                self.rainbow = False

    # ============================================================
    # 描画処理（RGBA安全版）
    # ============================================================

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
        # ★ 上下グラデーション（RGBA安全版）
        # ============================================================
        for i in range(self.height):
            grad_alpha = max(
                0,
                min(255, int(self.alpha * (1 - abs(i - self.height / 2) / (self.height / 2)))),
            )

            pygame.draw.line(surf, (*self.color, grad_alpha), (0, i), (width - 1, i))

        # ============================================================
        # ★ 横方向に走る光（RGBA安全）
        # ============================================================
        glow_width = 120

        for dx in range(-glow_width, glow_width):
            x = int(self.center_x + dx + self.light_offset)
            if 0 <= x < width:
                dist = abs(dx)
                a = max(0, min(255, int(self.alpha * (1 - dist / glow_width))))

                pygame.draw.line(light_surface, (255, 255, 255, a), (x, 0), (x, self.height - 1))

        surf.blit(light_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        screen.blit(surf, (0, self.y - self.height // 2))
