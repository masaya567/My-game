import pygame
import pygame.gfxdraw
import math


class LineGlow:
    """
    商用品質：判定ライン常時発光（pulse同期＋brightness対応＋BLEND_ADD）
    """

    def __init__(self, x, y, width, height=12):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.brightness = 1.0
        self.pulse = 0.0
        self.holding = False

        # キャッシュ
        self.cached = None
        self.cached_size = None

    # ------------------------------------------------------------
    # キャッシュ生成（横長の光帯）
    # ------------------------------------------------------------
    def _build_cache(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        center = self.height / 2
        for i in range(self.height):
            ratio = abs(i - center) / center
            alpha = int(255 * (1 - ratio))
            pygame.draw.line(surf, (255, 255, 255, alpha), (0, i), (self.width, i))

        self.cached = surf
        self.cached_size = (self.width, self.height)

    # ------------------------------------------------------------
    # update（pulse同期＋brightness）
    # ------------------------------------------------------------
    def update(self, dt, pulse, brightness, holding):
        self.pulse = pulse
        self.brightness = brightness
        self.holding = holding

    # ------------------------------------------------------------
    # draw（商用品質：pulse同期＋BLEND_ADD）
    # ------------------------------------------------------------
    def draw(self, screen):
        if self.cached is None or self.cached_size != (self.width, self.height):
            self._build_cache()

        # pulse による光量変化
        pulse_light = 0.25 + 0.25 * math.sin(self.pulse * 2.0)

        # holding 中は光量アップ
        hold_boost = 0.35 if self.holding else 0.0

        alpha = int(180 * (pulse_light + hold_boost) * self.brightness)

        surf = self.cached.copy()
        surf.set_alpha(alpha)

        screen.blit(
            surf,
            (self.x - self.width // 2, self.y - self.height // 2),
            special_flags=pygame.BLEND_ADD
        )
