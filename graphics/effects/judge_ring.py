"""
商用品質：判定リングエフェクトモジュール（完全版・最終形態）

ノーツ判定時にリング状の光を描画する。
"""

import pygame


class JudgeRing:
    """
    商用品質：判定リングエフェクトクラス
    """

    def __init__(self, x: float, y: float, color=(120, 200, 255)):
        self.x = x
        self.y = y
        self.color = color

        self.alpha = 255
        self.radius = 0
        self.max_radius = 90
        self.thickness = 6

        self.is_alive = True  # ★商用品質：生存判定

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
        """リングエフェクトを描画"""
        if not self.is_alive:
            return

        size = int(self.max_radius * 2)
        ring_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # --- 多層グロー（商用品質） ---
        layers = 16
        for i in range(layers):
            ratio = 1 - (i / layers)
            alpha = int(self.alpha * ratio)
            radius = int(self.radius + i * 2)

            pygame.draw.circle(
                ring_surface,
                (*self.color, alpha),
                (size // 2, size // 2),
                radius,
                self.thickness,
            )

        # --- 内側コアリング（加算合成） ---
        core_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            core_surface,
            (255, 255, 255, int(self.alpha * 0.8)),
            (size // 2, size // 2),
            int(self.radius),
            self.thickness,
        )

        ring_surface.blit(core_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        screen.blit(ring_surface, (self.x - size // 2, self.y - size // 2))
