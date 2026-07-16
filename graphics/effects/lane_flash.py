"""
商用品質：レーン発光エフェクトモジュール（完全版・最終形態）

ノーツ押下時にレーン全体を一瞬発光させる。
"""

import pygame
import math


class LaneFlash:
    """
    商用品質：レーン発光エフェクトクラス
    """

    def __init__(self, lane_x: float, lane_width: int, color=(120, 200, 255)):
        self.lane_x = lane_x
        self.lane_width = lane_width
        self.color = color

        self.alpha = 0
        self.timer = 0.0
        self.active = False

        self.is_alive = True  # ★商用品質：生存判定

    # ============================================================
    # トリガー処理
    # ============================================================

    def trigger(self):
        """レーン発光を開始"""
        self.active = True
        self.alpha = 255
        self.timer = 0.0

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        """時間経過に応じて発光を更新"""
        if not self.active:
            return

        self.timer += dt * 6

        # 指数フェードアウト（自然な消失）
        fade = int(255 * math.exp(-self.timer))
        self.alpha = max(0, fade)

        if self.alpha <= 0:
            self.active = False
            self.is_alive = False

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen, lane_height, y_offset=0):
        """レーン発光を描画"""
        if not self.active or self.alpha <= 0:
            return

        flash_surface = pygame.Surface((self.lane_width, lane_height), pygame.SRCALPHA)

        # --- 多層グラデーション（商用品質） ---
        layers = 12
        for i in range(layers):
            ratio = 1 - (i / layers)
            alpha = int(self.alpha * ratio)

            pygame.draw.rect(
                flash_surface,
                (self.color[0], self.color[1], self.color[2], alpha),
                (0, i * 3, self.lane_width, lane_height - i * 6),
                border_radius=18,
            )

        # --- 加算合成による強い光 ---
        add_surface = pygame.Surface((self.lane_width, lane_height), pygame.SRCALPHA)
        pygame.draw.rect(
            add_surface,
            (255, 255, 255, int(self.alpha * 0.6)),
            (0, 0, self.lane_width, lane_height),
            border_radius=22,
        )

        flash_surface.blit(add_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        screen.blit(flash_surface, (self.lane_x, y_offset))
