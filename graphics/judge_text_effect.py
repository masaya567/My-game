"""
商用品質：判定テキスト演出モジュール（完全版・最終形態）

Perfect / Great / Good / Miss の文字エフェクトを描画する。
"""

import pygame
import random
import math


class JudgeTextEffect:
    """
    商用品質：判定テキスト演出クラス
    """

    def __init__(
        self, x: float, y: float, text: str, color: tuple[int, int, int], font: pygame.font.Font
    ):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font

        self.alpha = 255
        self.scale = 1.4
        self.timer = 0.0
        self.ring_radius = 0.0

        self.is_alive = True  # ★商用品質：生存判定

        # スパーク粒子（速度・寿命付き）
        self.sparks = []
        for _ in range(14):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(120, 260)
            lifetime = random.uniform(0.25, 0.45)
            self.sparks.append(
                {
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": lifetime,
                    "radius": random.randint(3, 6),
                }
            )

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float) -> None:
        """時間経過に応じてエフェクトを更新"""
        self.timer += dt

        # スケール変化（ポップ → 収束）
        self.scale += (1.0 - self.scale) * 0.18

        # アルファフェード
        self.alpha = max(0, 255 - int(self.timer * 700))

        # リング拡大
        self.ring_radius += 300 * dt

        # スパーク更新
        for s in self.sparks:
            s["life"] -= dt
            s["vx"] *= 0.96
            s["vy"] *= 0.96

        # 生存判定
        if self.alpha <= 0:
            self.is_alive = False

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen: pygame.Surface) -> None:
        """判定テキストエフェクトを描画"""
        if not self.is_alive:
            return

        # --- テキスト描画 ---
        font_scaled = pygame.font.Font(self.font, int(48 * self.scale))

        surf = font_scaled.render(self.text, True, self.color)
        surf.set_alpha(self.alpha)

        outline = font_scaled.render(self.text, True, (0, 0, 0))
        outline.set_alpha(self.alpha)

        cx = self.x - surf.get_width() // 2
        cy = self.y - surf.get_height() // 2

        # 黒縁取り
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            screen.blit(outline, (cx + dx, cy + dy))

        # 本体
        screen.blit(surf, (cx, cy))

        # --- 多層リング（加算合成） ---
        if self.ring_radius < 60:
            ring_surface = pygame.Surface((300, 300), pygame.SRCALPHA)
            layers = 12
            for i in range(layers):
                ratio = 1 - (i / layers)
                alpha = int(self.alpha * ratio)
                radius = int(self.ring_radius + i * 2)

                pygame.draw.circle(
                    ring_surface,
                    (*self.color, alpha),
                    (150, 150),
                    radius,
                    3,
                )

            screen.blit(ring_surface, (self.x - 150, self.y - 150), special_flags=pygame.BLEND_ADD)

        # --- スパーク粒子 ---
        for s in self.sparks:
            if s["life"] > 0:
                sx = self.x + s["vx"] * 0.015
                sy = self.y + s["vy"] * 0.015

                pygame.draw.circle(
                    screen,
                    (*self.color, int(self.alpha)),
                    (int(sx), int(sy)),
                    s["radius"],
                )
