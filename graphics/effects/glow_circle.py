"""
商用品質：円形発光エフェクトモジュール（完全版・最終形態）

ノーツ判定やコンボ演出時に使用される円形発光を描画する。
"""

import pygame


class GlowCircle:
    """
    商用品質：円形発光エフェクトクラス
    """

    def __init__(self, x: float, y: float, color=(120, 200, 255)):
        self.x = x
        self.y = y
        self.color = color

        self.alpha = 255
        self.radius = 0
        self.max_radius = 80

        self.is_alive = True  # ★商用品質：生存判定

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float) -> None:
        """時間経過に応じて発光を更新"""
        self.radius += 300 * dt
        self.alpha = max(0, self.alpha - 500 * dt)

        if self.radius >= self.max_radius or self.alpha <= 0:
            self.is_alive = False

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen: pygame.Surface) -> None:
        """円形発光を描画"""
        if not self.is_alive:
            return

        size = int(self.max_radius * 2)
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # 外側グロー（多層）
        for i in range(20):
            alpha = int(self.alpha * (1 - i / 20))
            pygame.draw.circle(
                glow_surface,
                (*self.color, alpha),
                (size // 2, size // 2),
                int(self.radius * (1 - i / 25)),
            )

        # 内側コア
        pygame.draw.circle(
            glow_surface,
            (255, 255, 255, int(self.alpha * 0.8)),
            (size // 2, size // 2),
            int(self.radius * 0.4),
        )

        screen.blit(glow_surface, (self.x - size // 2, self.y - size // 2))
