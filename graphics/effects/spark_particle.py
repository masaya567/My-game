import pygame
import random
import math


class SparkParticle:
    def __init__(self, x, y, color, strength=1.0):
        self.x = x
        self.y = y

        # ランダム方向（360度）に飛ばす
        angle = random.uniform(0, math.pi * 2)

        # Perfect / Great / Good で強度差
        speed = random.uniform(180, 320) * strength

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.color = tuple(int(channel) for channel in color[:3])
        self.alpha = 255
        self.timer = 0.0
        self.finished = False

        # 粒子サイズ（Perfect は少し大きい）
        self.size = random.randint(4, 6)

    def update(self, dt):
        self.timer += dt

        # easing（速度が自然に落ちる）
        slow = 1.0 - self.timer * 2.2
        slow = max(0.0, slow)

        self.x += self.vx * dt * slow
        self.y += self.vy * dt * slow

        # alpha 減衰（0.25秒で消える）
        self.alpha = max(0, 255 - int(self.timer * 900))

        if self.alpha <= 0:
            self.finished = True

    def draw(self, screen):
        if self.finished:
            return

        # 加算合成（BLEND_ADD）で光が綺麗に混ざる
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            surf,
            (*self.color[:3], int(max(0, min(255, self.alpha)))),
            (self.size, self.size),
            self.size,
        )
        screen.blit(surf, (self.x - self.size, self.y - self.size), special_flags=pygame.BLEND_ADD)
