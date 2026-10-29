import pygame
import math
from constants import WIDTH
from utils.theme.theme import get_ui_scale


class RippleEffect:
    """
    商用品質：判定ライン波紋（UI_SCALE対応・完全版）
    """

    def __init__(self, y: float, color=(120, 200, 255), strength=1.0):
        self.scale = get_ui_scale()

        self.y = y
        self.color = tuple(int(channel) for channel in color[:3])
        self.strength = max(0.0, min(1.0, float(strength)))

        # ★ UI_SCALE 対応
        self.radius = 0.0
        self.alpha = int(200 * self.strength)
        self.timer = 0.0
        self.is_alive = True

        # 高さもスケール対応
        self.height = int(180 * self.scale)
        self._surface = pygame.Surface((WIDTH, self.height), pygame.SRCALPHA)

    def update(self, dt):
        self.timer += max(0.0, dt)

        # 0.25秒で広がって消える（プロセカ式）
        t = min(self.timer / 0.25, 1.0)
        ease = t**0.6

        # ★ 横方向の広がりを UI_SCALE 対応
        self.radius = (20 + ease * 260) * self.scale

        # ★ フェードアウトも UI_SCALE 対応
        self.alpha = max(0, min(255, int(220 * (1 - ease) * self.strength)))

        if self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen):
        if not self.is_alive:
            return

        surf = self._surface
        surf.fill((0, 0, 0, 0))

        color = self.color[:3]
        center_y = int(self.height * 0.5)

        # ★ UI_SCALE 対応したレイヤー構造
        for layer in range(3):
            radius = self.radius + layer * (8 * self.scale)

            rect = pygame.Rect(
                -radius * 0.15,
                center_y - radius * 0.22,
                WIDTH + radius * 0.3,
                max(1, int(radius * 0.44)),
            )

            layer_alpha = max(0, int(self.alpha * (1.0 - layer * 0.24)))
            pygame.draw.ellipse(
                surf,
                (*color, layer_alpha),
                rect,
                max(1, int((4 - layer) * self.scale)),
            )

        # コアライン
        core_alpha = max(0, int(self.alpha * 0.7))
        pygame.draw.line(
            surf,
            (*color, core_alpha),
            (0, center_y),
            (WIDTH, center_y),
            int(2 * self.scale),
        )

        screen.blit(
            surf,
            (0, self.y - int(self.height * 0.55)),
            special_flags=pygame.BLEND_ADD,
        )
