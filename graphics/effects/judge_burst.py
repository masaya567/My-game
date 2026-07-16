"""
商用品質：判定爆発エフェクトモジュール（完全版・最終形態）

ノーツ判定時に発生する爆発光エフェクトを描画する。
"""

import pygame
import random
import math


class JudgeBurst:
    """
    商用品質：判定爆発エフェクトクラス
    """

    def __init__(self, x: float, y: float, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.color = color

        self.alpha = 255
        self.radius = 0
        self.max_radius = 90

        self.timer = 0.0
        self.is_alive = True  # ★商用品質：生存判定

        # スパーク粒子（速度・寿命付き）
        self.sparks = []
        for _ in range(18):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(200, 450)
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
        """時間経過に応じて爆発エフェクトを更新"""
        self.timer += dt

        # 爆発の広がり
        self.radius += 450 * dt

        # フェードアウト
        self.alpha = max(0, 255 - int(self.timer * 900))

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
        """爆発エフェクトを描画"""
        if not self.is_alive:
            return

        size = int(self.max_radius * 2)
        burst_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # --- グロー層（加算合成） ---
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (255, 255, 255, int(self.alpha * 0.8)),
            (size // 2, size // 2),
            int(self.radius * 0.6),
        )
        burst_surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        # --- 外側リング ---
        ring_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            ring_surface,
            (*self.color, int(self.alpha)),
            (size // 2, size // 2),
            int(self.radius),
            4,
        )
        burst_surface.blit(ring_surface, (0, 0))

        # --- スパーク粒子 ---
        for s in self.sparks:
            if s["life"] > 0:
                sx = self.x + s["vx"] * 0.015
                sy = self.y + s["vy"] * 0.015
                pygame.draw.circle(
                    burst_surface,
                    (*self.color, int(self.alpha)),
                    (int(sx - self.x + size // 2), int(sy - self.y + size // 2)),
                    s["radius"],
                )

        screen.blit(burst_surface, (self.x - size // 2, self.y - size // 2))
