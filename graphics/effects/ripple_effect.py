import pygame
import math
from constants import WIDTH


class RippleEffect:
    """
    商用品質：判定ライン波紋（プロセカ完全版・最終形態）
    - 横長楕円で判定ラインに沿って広がる
    - Perfect / Great / Good の色と強度に完全同期
    """

    def __init__(self, y: float, color=(120, 200, 255), strength=1.0):
        self.y = y
        self.color = tuple(int(channel) for channel in color[:3])
        self.strength = max(0.0, min(1.0, float(strength)))

        self.radius = 0.0
        self.alpha = int(200 * self.strength)
        self.timer = 0.0
        self.is_alive = True
        self._surface = pygame.Surface((WIDTH, 180), pygame.SRCALPHA)

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        self.timer += max(0.0, dt)

        # 0.25秒で広がって消える（プロセカ式）
        t = min(self.timer / 0.25, 1.0)
        ease = t**0.6  # 水面のような広がり

        # 横方向に強く広がる
        self.radius = 20 + ease * 260

        # フェードアウト
        self.alpha = max(0, min(255, int(220 * (1 - ease) * self.strength)))

        if self.alpha <= 0:
            self.is_alive = False

    # ============================================================
    # 描画処理（横長楕円）
    # ============================================================

    def draw(self, screen):
        if not self.is_alive:
            return

        surf = self._surface
        surf.fill((0, 0, 0, 0))

        color = self.color[:3]
        center_y = 90

        # 複数の細い輪郭を重ね、判定ラインに沿う柔らかい波紋にする。
        for layer in range(3):
            radius = self.radius + layer * 8
            rect = pygame.Rect(
                -radius * 0.15,
                center_y - radius * 0.22,
                WIDTH + radius * 0.3,
                max(1, int(radius * 0.44)),
            )
            layer_alpha = max(0, int(self.alpha * (1.0 - layer * 0.24)))
            pygame.draw.ellipse(surf, (*color, layer_alpha), rect, max(1, 4 - layer))

        core_alpha = max(0, int(self.alpha * 0.7))
        pygame.draw.line(surf, (*color, core_alpha), (0, center_y), (WIDTH, center_y), 2)

        screen.blit(surf, (0, self.y - 100), special_flags=pygame.BLEND_ADD)
