import pygame
import math
from constants import HEIGHT
from utils.theme.theme import get_ui_scale


class LaneFlash:
    def __init__(self, lane_x: float, lane_width: int, strength: float = 1.0):
        self.scale = get_ui_scale()

        self.lane_x = lane_x
        self.lane_width = int(lane_width * self.scale)   # ★ UI_SCALE 対応
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

        # ★ UI_SCALE 対応した減衰速度
        self.timer += dt * (6 * self.scale)

        fade = int(self.alpha * math.exp(-self.timer))
        self.alpha = max(0, fade)

        if self.alpha <= 0:
            self.active = False
            self.is_alive = False

    def draw(self, screen, lane_height=None, y_offset=0):
        if not self.active or self.alpha <= 0:
            return

        lane_height = int((lane_height or HEIGHT) * self.scale)  # ★ UI_SCALE 対応

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

            # ★ UI_SCALE 対応した層のアルファ
            alpha = max(0, min(255, int(self.alpha * ratio * 0.28)))

            # ★ UI_SCALE 対応した層の位置と高さ
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
