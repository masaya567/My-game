import pygame


class HitLine:
    """
    商用品質：判定ライン白線＋判定色ライン（完全安全版）
    """

    def __init__(self, x, y, color, strength):
        self.x = x
        self.y = y
        self.color = tuple(int(channel) for channel in color[:3])
        self.strength = max(0.0, min(1.0, float(strength)))

        self.alpha = 255 * strength
        self.timer = 0.0
        self.is_alive = True
        self.white_surface = pygame.Surface((6, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.white_surface, (255, 255, 255), (0, 0, 6, 40))
        self.color_surface = pygame.Surface((3, 56), pygame.SRCALPHA)
        pygame.draw.rect(self.color_surface, self.color, (0, 0, 3, 56))

    def update(self, dt):
        self.timer += dt

        # 0.12秒で消える（プロセカ式）
        t = min(self.timer / 0.12, 1.0)
        ease = t**0.7

        self.alpha = max(0, int(255 * (1 - ease) * self.strength))

        if self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen):
        if not self.is_alive:
            return

        # -----------------------------
        # 白線（中央）安全版
        # -----------------------------
        self.white_surface.set_alpha(int(self.alpha))
        screen.blit(self.white_surface, (self.x - 3, self.y - 20))

        # -----------------------------
        # 判定色ライン（薄め）安全版
        # -----------------------------
        self.color_surface.set_alpha(int(self.alpha * 0.6))
        screen.blit(self.color_surface, (self.x - 1, self.y - 28))
