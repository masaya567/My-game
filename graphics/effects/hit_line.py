import pygame
from utils.theme.theme import get_ui_scale


class HitLine:
    """
    商用品質：判定ライン白線＋判定色ライン（UI_SCALE対応・完全版）
    """

    def __init__(self, x, y, color, strength):
        self.scale = get_ui_scale()

        self.x = x
        self.y = y
        self.color = tuple(int(channel) for channel in color[:3])
        self.strength = max(0.0, min(1.0, float(strength)))

        self.alpha = 255 * strength
        self.timer = 0.0
        self.is_alive = True

        # ★ UI_SCALE 対応したサイズ
        white_w = int(6 * self.scale)
        white_h = int(40 * self.scale)
        color_w = int(3 * self.scale)
        color_h = int(56 * self.scale)

        # 白線
        self.white_surface = pygame.Surface((white_w, white_h), pygame.SRCALPHA)
        pygame.draw.rect(self.white_surface, (255, 255, 255), (0, 0, white_w, white_h))

        # 判定色ライン
        self.color_surface = pygame.Surface((color_w, color_h), pygame.SRCALPHA)
        pygame.draw.rect(self.color_surface, self.color, (0, 0, color_w, color_h))

        # ★ UI_SCALE 対応した描画オフセット
        self.white_offset_x = int(-white_w / 2)
        self.white_offset_y = int(-white_h / 2)
        self.color_offset_x = int(-color_w / 2)
        self.color_offset_y = int(-color_h / 2 - 8 * self.scale)

    def update(self, dt):
        self.timer += dt

        # 0.12秒で消える（プロセカ式）
        t = min(self.timer / 0.12, 1.0)
        ease = t ** 0.7

        self.alpha = max(0, int(255 * (1 - ease) * self.strength))

        if self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen):
        if not self.is_alive:
            return

        # 白線
        self.white_surface.set_alpha(int(self.alpha))
        screen.blit(
            self.white_surface,
            (self.x + self.white_offset_x, self.y + self.white_offset_y)
        )

        # 判定色ライン
        self.color_surface.set_alpha(int(self.alpha * 0.6))
        screen.blit(
            self.color_surface,
            (self.x + self.color_offset_x, self.y + self.color_offset_y)
        )
