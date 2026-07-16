"""
商用品質：判定ライン光帯描画モジュール（完全版）

ノーツ判定時にライン上を走る光の帯を描画する。
"""

import pygame
import math


class JudgeBeam:
    """
    商用品質：判定ライン光帯描画クラス
    """

    def __init__(self, width: int, y: float):
        self.width = width
        self.y = y

        self.alpha = 0
        self.height = 42  # 商用ゲームの光帯高さ

        # 横方向に走る光
        self.light_x = 0
        self.light_speed = 1800

        self.active = False

    # ============================================================
    # トリガー処理
    # ============================================================

    def trigger(self):
        """光帯を発光状態にする"""
        self.active = True
        self.alpha = 255
        self.light_x = -self.width  # 左端から走らせる

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        """時間経過に応じて光帯を更新"""
        if not self.active:
            return

        # フェードアウト
        self.alpha = max(0, self.alpha - 600 * dt)

        # 横方向の光を移動
        self.light_x += self.light_speed * dt

        if self.alpha <= 0:
            self.active = False

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen):
        """判定ライン光帯を描画"""
        if self.alpha <= 0:
            return

        beam_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # --- 上下グラデーション（商用品質） ---
        for i in range(self.height):
            grad_alpha = int(self.alpha * (1 - abs(i - self.height / 2) / (self.height / 2)))
            color = (120, 180, 255, grad_alpha)
            pygame.draw.line(beam_surface, color, (0, i), (self.width, i))

        # --- 横方向に走る光（加算合成） ---
        light_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        glow_width = 120  # 光の幅

        for x in range(int(self.light_x - glow_width), int(self.light_x + glow_width)):
            if 0 <= x < self.width:
                dist = abs(x - self.light_x)
                a = int(self.alpha * (1 - dist / glow_width))
                pygame.draw.line(light_surface, (255, 255, 255, a), (x, 0), (x, self.height))

        # 加算合成
        beam_surface.blit(light_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        screen.blit(beam_surface, (0, self.y - self.height // 2))
