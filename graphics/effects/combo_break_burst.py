import pygame
from utils.theme.theme import get_ui_scale


class ComboBreakBurst:
    """
    商用品質：コンボ切れ爆光（UI_SCALE対応・完全版）
    - 小規模・高速フェード
    - 加算合成の爆光
    """

    def __init__(self, pos):
        self.scale = get_ui_scale()

        self.x, self.y = pos
        self.timer = 0.0
        self.alpha = 255
        self.radius = 0
        self.is_alive = True

        # 画面全体に描く（加算合成用）
        self._w = None
        self._h = None
        self._surf = None
        self._circle = None

    def update(self, dt):
        self.timer += dt

        # ★ 半径拡大（高速）UI_SCALE 対応
        self.radius = (20 + self.timer * 180) * self.scale

        # ★ フェードアウト（高速）UI_SCALE 対応
        self.alpha = max(0, 255 - self.timer * (900 * self.scale))

        if self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen):
        if not self.is_alive:
            return

        w = screen.get_width()
        h = screen.get_height()

        # 必要ならサーフェスを作り直す
        if self._w != w or self._h != h:
            self._surf = pygame.Surface((w, h), pygame.SRCALPHA)
            self._circle = pygame.Surface((w, h), pygame.SRCALPHA)
            self._w, self._h = w, h

        surf = self._surf
        circle = self._circle

        surf.fill((0, 0, 0, 0))
        circle.fill((0, 0, 0, 0))

        # ★ RGBのみで描く（RGBA安全）
        pygame.draw.circle(
            circle,
            (255, 200, 120),
            (self.x, self.y),
            int(self.radius)
        )

        # ★ 透明度は set_alpha に任せる
        circle.set_alpha(int(self.alpha))

        # ★ 加算合成
        surf.blit(circle, (0, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(surf, (0, 0), special_flags=pygame.BLEND_ADD)
