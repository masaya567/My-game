"""
商用品質：円形発光エフェクトモジュール（完全版・最終形態）

ノーツ判定やコンボ演出時に使用される円形発光を描画する。
"""

import pygame

_GLOW_SURFACES = {}
_SCALED_GLOW_SURFACES = {}


class GlowCircle:
    def __init__(self, x: float, y: float, color=(120, 200, 255)):
        if isinstance(x, (tuple, list)):
            x, y = x
        self.x = x
        self.y = y
        self.color = tuple(color[:3])

        self.alpha = 255
        self.radius = 0
        self.max_radius = 80
        self.is_alive = True

    def update(self, dt: float):
        self.radius += 300 * dt
        self.alpha = max(0, self.alpha - 500 * dt)
        if self.radius >= self.max_radius or self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen: pygame.Surface):
        if not self.is_alive:
            return

        base_key = (self.color, self.max_radius)
        base_surface = _GLOW_SURFACES.get(base_key)
        if base_surface is None:
            base_size = self.max_radius * 2
            base_surface = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
            center = (self.max_radius, self.max_radius)
            for layer_index in range(20):
                layer = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
                pygame.draw.circle(
                    layer,
                    self.color,
                    center,
                    int(self.max_radius * (1 - layer_index / 25)),
                )
                layer.set_alpha(int(255 * (1 - layer_index / 20)))
                base_surface.blit(layer, (0, 0))

            core = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
            pygame.draw.circle(core, (255, 255, 255), center, int(self.max_radius * 0.4))
            core.set_alpha(204)
            base_surface.blit(core, (0, 0))
            _GLOW_SURFACES[base_key] = base_surface

        diameter = max(1, int(self.radius * 2))
        scaled_key = (base_key, diameter)
        glow_surface = _SCALED_GLOW_SURFACES.get(scaled_key)
        if glow_surface is None:
            glow_surface = pygame.transform.smoothscale(base_surface, (diameter, diameter))
            _SCALED_GLOW_SURFACES[scaled_key] = glow_surface

        glow_surface.set_alpha(self.alpha)
        screen.blit(
            glow_surface,
            (self.x - diameter // 2, self.y - diameter // 2),
            special_flags=pygame.BLEND_ADD,
        )
