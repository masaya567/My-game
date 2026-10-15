import pygame
import math


class JudgeGlow:
    def __init__(self, x, y, color, strength=1.0):
        self.x = x
        self.y = y
        self.color = tuple(int(channel) for channel in color[:3])
        self.alpha = 255
        self.timer = 0.0
        self.finished = False
        self.strength = strength  # perfect=1.0, great=0.8, good=0.6

    def update(self, dt):
        self.timer += dt

        # 0.25秒で消える
        self.alpha = max(0, 255 - int(self.timer * 900))

        if self.alpha <= 0:
            self.finished = True

    def draw(self, screen):
        if self.finished:
            return

        # 時間で膨張する（プロセカ風）
        base_radius = 70
        radius = base_radius + self.timer * 40

        # 光輪のぼかし層（3層）
        for i in range(3):
            layer_alpha = max(0, min(255, int(self.alpha * (0.6 - i * 0.18) * self.strength)))
            layer_radius = int(radius + i * 18)

            surf = pygame.Surface((layer_radius * 2, layer_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                surf, (*self.color[:3], layer_alpha), (layer_radius, layer_radius), layer_radius
            )
            screen.blit(surf, (self.x - layer_radius, self.y - layer_radius))
