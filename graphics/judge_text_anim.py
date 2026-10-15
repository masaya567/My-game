"""
商用品質：判定テキスト演出モジュール（完全版・最終形態）

Perfect / Great / Good / Miss の文字エフェクトを描画する。
"""

import pygame
import math


class JudgeTextAnim:
    """
    商用品質：判定文字アニメーション（最終形態）
    """

    def __init__(self, res):
        self.res = res
        self.active = False
        self.timer = 0.0
        self.judge = ""
        self.x = 0
        self.y = 0

        # ★ 商用品質：判定ごとの色変化（完全版）
        self.colors = {
            "perfect": (255, 230, 120),  # 金色
            "great": (120, 180, 255),  # 青
            "good": (120, 255, 160),  # 緑
            "miss": (255, 80, 80),  # 赤
        }

    def trigger(self, judge, x, y):
        self.active = True
        self.timer = 0.0
        self.judge = judge.lower()
        self.x = x
        self.y = y

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt
        if self.timer > 0.45:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        t = self.timer
        color = self.colors.get(self.judge, (255, 255, 255))

        font = self.res.get_font(48, weight="bold")
        text = self.judge.upper()

        # プロセカ風: 大きく出て、少し行き過ぎてから基準位置へ戻す。
        intro = min(1.0, t / 0.16)
        overshoot = 1.0 + 0.16 * math.sin(intro * math.pi)
        scale = (1.55 - 0.55 * intro) * overshoot
        if t >= 0.16:
            settle = min(1.0, (t - 0.16) / 0.22)
            scale = 1.0 + (1.0 - settle) * 0.06 * math.sin(settle * math.pi)

        # --- アルファ ---
        alpha = max(0, min(255, int(255 * (1.0 - t / 0.45))))
        rise = 34 * min(1.0, t / 0.16)
        bounce = 10 * math.sin(min(1.0, t / 0.28) * math.pi)
        draw_y = self.y - rise - bounce

        surf = font.render(text, True, color)
        surf = pygame.transform.rotozoom(surf, 0, scale)
        surf.set_alpha(alpha)

        rect = surf.get_rect(center=(self.x, draw_y))

        # --- PERFECT の残像（薄めに調整） ---
        if self.judge == "perfect":
            for i in range(3):
                ghost = pygame.transform.rotozoom(surf, 0, scale - 0.1 * (i + 1))
                ghost.set_alpha(alpha // (i + 3))
                ghost_rect = ghost.get_rect(center=(self.x, draw_y - (i * 5)))
                screen.blit(ghost, ghost_rect)

        screen.blit(surf, rect)
