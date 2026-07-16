"""
商用品質：コンボ演出モジュール（完全版・最終形態）

コンボ数のポップアニメーションと発光エフェクトを描画する。
"""

import pygame
import math


class ComboEffect:
    """
    商用品質：コンボ演出クラス
    """

    def __init__(self, x: float, y: float, font: pygame.font.Font):
        self.x = x
        self.y = y
        self.font = font

        self.combo = 0
        self.alpha = 0
        self.scale = 1.0
        self.flash = 0.0
        self.timer = 0.0

        self.is_alive = False  # ★商用品質：生存判定

    # ============================================================
    # コンボ更新
    # ============================================================

    def trigger(self, combo: int) -> None:
        """コンボ数を更新してアニメーションを開始"""
        self.combo = combo
        self.alpha = 255
        self.scale = 1.4
        self.flash = 1.0
        self.timer = 0.0
        self.is_alive = True

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float) -> None:
        """時間経過に応じてアニメーションを更新"""
        if not self.is_alive:
            return

        self.timer += dt
        self.scale += (1.0 - self.scale) * 0.15
        self.alpha = max(0, self.alpha - 300 * dt)
        self.flash = max(0, self.flash - 2.5 * dt)

        if self.alpha <= 0:
            self.is_alive = False

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen: pygame.Surface) -> None:
        """コンボエフェクトを描画"""
        if not self.is_alive or self.combo <= 0:
            return

        # --- テキスト描画 ---
        font_scaled = pygame.font.Font(self.font, int(60 * self.scale))
        text = f"{self.combo} COMBO"

        # 白文字
        surf = font_scaled.render(text, True, (255, 255, 255))
        surf.set_alpha(int(self.alpha))

        # 黒縁取り
        outline = font_scaled.render(text, True, (0, 0, 0))
        outline.set_alpha(int(self.alpha))

        # --- 発光レイヤー（加算合成） ---
        glow_surface = pygame.Surface(
            (surf.get_width() + 80, surf.get_height() + 80), pygame.SRCALPHA
        )

        for i in range(20):
            alpha = int(150 * (1 - i / 20) * self.flash)
            pygame.draw.ellipse(
                glow_surface,
                (120, 200, 255, alpha),
                (40 - i, 40 - i, surf.get_width() + i * 2, surf.get_height() + i * 2),
            )

        # --- リングエフェクト ---
        ring_surface = pygame.Surface((300, 300), pygame.SRCALPHA)
        radius = 80 + math.sin(self.timer * 4) * 10
        pygame.draw.circle(
            ring_surface,
            (120, 200, 255, int(self.alpha * 0.6)),
            (150, 150),
            int(radius),
            3,
        )

        # --- 描画 ---
        cx = self.x - surf.get_width() // 2
        cy = self.y - surf.get_height() // 2

        screen.blit(glow_surface, (cx - 40, cy - 40), special_flags=pygame.BLEND_ADD)
        screen.blit(ring_surface, (self.x - 150, self.y - 150), special_flags=pygame.BLEND_ADD)

        # 黒縁取り
        screen.blit(outline, (cx - 2, cy))
        screen.blit(outline, (cx + 2, cy))
        screen.blit(outline, (cx, cy - 2))
        screen.blit(outline, (cx, cy + 2))

        # 本体
        screen.blit(surf, (cx, cy))
