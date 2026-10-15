import pygame
import math
from constants import HEIGHT


class LaneFlash:
    def __init__(self, lane_x: float, lane_width: int, strength: float = 1.0):
        self.lane_x = lane_x
        self.lane_width = lane_width
        self.strength = strength

        self.alpha = 0
        self.timer = 0.0
        self.active = False
        self.is_alive = True
        self._flash_surface = None
        self._add_surface = None
        self._surface_size = None

    def trigger(self):
        self.active = True
        self.alpha = 255 * self.strength
        self.timer = 0.0
        self.is_alive = self.alpha > 0

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt * 6
        fade = int(self.alpha * math.exp(-self.timer))
        self.alpha = max(0, fade)

        if self.alpha <= 0:
            self.active = False
            self.is_alive = False

    def draw(self, screen, lane_height=None, y_offset=0):
        if not self.active or self.alpha <= 0:
            return

        lane_height = lane_height or HEIGHT

        surface_size = (self.lane_width, lane_height)
        if self._surface_size != surface_size:
            self._flash_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
            self._add_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
            self._add_surface.fill((255, 255, 255))
            self._surface_size = surface_size

        flash_surface = self._flash_surface
        flash_surface.fill((0, 0, 0, 0))

        layers = 12
        for i in range(layers):
            ratio = 1 - (i / layers)
            alpha = max(0, min(255, int(self.alpha * ratio * 0.28)))

            top = int(i * lane_height / (layers * 2))
            height = max(1, lane_height - top * 2)

            pygame.draw.rect(
                flash_surface,
                (255, 255, 255, alpha),
                (0, top, self.lane_width, height),
            )

        # --- 加算合成 ---
        add_surface = self._add_surface
        add_surface.set_alpha(int(self.alpha * 0.22))

        flash_surface.blit(add_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        screen.blit(flash_surface, (self.lane_x, y_offset))
