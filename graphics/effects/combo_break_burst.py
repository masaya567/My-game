import pygame
import math

class ComboBreakBurst:
    """
    商用品質：コンボ切れ爆光（小規模・高速フェード）
    """

    def __init__(self, pos):
        self.x, self.y = pos
        self.timer = 0.0
        self.alpha = 255
        self.radius = 0
        self.is_alive = True

    def update(self, dt):
        self.timer += dt

        # 半径拡大（高速）
        self.radius = 20 + self.timer * 180

        # フェードアウト
        self.alpha = max(0, 255 - self.timer * 900)

        if self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen):
        if not self.is_alive:
            return

        # 透明サーフェス
        surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)

        # circle は RGB で描く
        circle_surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.circle(
            circle_surf,
            (255, 200, 120),  # ★ RGBのみ
            (self.x, self.y),
            int(self.radius)
        )

        # 透明度は set_alpha に任せる
        circle_surf.set_alpha(int(self.alpha))

        # 加算合成
        surf.blit(circle_surf, (0, 0))
        screen.blit(surf, (0, 0), special_flags=pygame.BLEND_ADD)
