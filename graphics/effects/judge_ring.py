"""
商用品質：判定リングエフェクトモジュール（UI_SCALE対応・完全版）

Perfect / Great / Good / Miss で色を変えて描画する。
"""

import pygame
from utils.theme.theme import get_ui_scale


class JudgeRing:
    """
    商用品質：判定リングエフェクトクラス（色変化＋UI_SCALE対応）
    """

    def __init__(self, x: float, y: float, color=(120, 200, 255)):
        if isinstance(x, (tuple, list)):
            x, y = x
        self.x = x
        self.y = y
        self.color = tuple(color[:3])  # RGBのみ

        # ★ UI_SCALE 対応
        self.scale = get_ui_scale()

        # ★ スケール対応したパラメータ
        self.alpha = 255
        self.radius = 0
        self.max_radius = int(90 * self.scale)
        self.thickness = int(6 * self.scale)

        self.is_alive = True

        size = self.max_radius * 2
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float) -> None:
        """時間経過に応じてリングを更新（UI_SCALE対応）"""

        # ★ スケール対応した速度
        self.radius += 420 * self.scale * dt
        self.alpha = max(0, self.alpha - 520 * self.scale * dt)

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

        # --- 多層グロー（UI_SCALE対応） ---
        layers = 16
        for i in range(layers):
            ratio = 1 - (i / layers)
            alpha = int(self.alpha * ratio)
            radius = int(self.radius + i * (2 * self.scale))

            pygame.draw.circle(
                ring_surface,
                (*self.color, alpha),
                center,
                radius,
                self.thickness,
            )

        # --- 内側コアリング ---
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
