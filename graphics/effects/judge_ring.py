"""
商用品質：判定リングエフェクトモジュール（完全版・色変化対応）

Perfect / Great / Good / Miss で色を変えて描画する。
"""

import pygame


class JudgeRing:
    """
    商用品質：判定リングエフェクトクラス（色変化対応）
    """

    def __init__(self, x: float, y: float, color=(120, 200, 255)):
        if isinstance(x, (tuple, list)):
            x, y = x
        self.x = x
        self.y = y
        self.color = tuple(color[:3])  # ★ Perfect / Great / Good / Miss の色を受け取る

        self.alpha = 255
        self.radius = 0
        self.max_radius = 90
        self.thickness = 6

        self.is_alive = True
        size = self.max_radius * 2
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float) -> None:
        """時間経過に応じてリングを更新"""
        self.radius += 420 * dt
        self.alpha = max(0, self.alpha - 520 * dt)

        if self.alpha <= 0 or self.radius >= self.max_radius:
            self.is_alive = False

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_alive:
            return

        size = int(self.max_radius * 2)
        ring_surface = self.surface
        ring_surface.fill((0, 0, 0, 0))
        center = (size // 2, size // 2)

        # --- 多層グロー（安全版） ---
        layers = 16
        for i in range(layers):
            ratio = 1 - (i / layers)
            alpha = int(self.alpha * ratio)
            radius = int(self.radius + i * 2)

            pygame.draw.circle(
                ring_surface,
                (*self.color, alpha),
                center,
                radius,
                self.thickness,
            )

        pygame.draw.circle(
            ring_surface,
            (255, 255, 255, int(self.alpha * 0.8)),
            center,
            int(self.radius),
            self.thickness,
        )

        screen.blit(
            ring_surface,
            (self.x - size // 2, self.y - size // 2),
            special_flags=pygame.BLEND_ADD,
        )
