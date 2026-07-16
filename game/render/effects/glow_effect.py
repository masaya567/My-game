"""
商用仕様：グローエフェクト（完全版）

判定時の光量アップ、揺らぎ、コア光、指数フェード、加算合成を備えた高品質グロー。
"""

import pygame
import math


class GlowEffect:
    """
    商用仕様：グローエフェクト（完全版）
    """

    def __init__(self, pos, color=(255, 255, 255), base_radius=60, duration=300):
        self.pos = pos
        self.color = color
        self.base_radius = base_radius
        self.duration = duration

        self.elapsed = 0
        self.active = True

        # 判定時の光量アップ
        self.kick_strength = 0.0

    # ============================================================
    # 判定時の光量アップ
    # ============================================================

    def kick(self, power=1.0):
        """Perfect なら 1.0、Great なら 0.7 など"""
        self.kick_strength = min(1.0, self.kick_strength + power)

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        """指数フェード＋揺らぎ＋kick減衰"""
        if not self.active:
            return

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False

        # kick の指数減衰
        self.kick_strength *= 0.85

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen):
        if not self.active:
            return

        # 指数フェード
        fade = math.exp(-self.elapsed / self.duration * 3)
        alpha = int(255 * fade)

        # sin波揺らぎ
        wave = (math.sin(self.elapsed * 0.03) + 1) * 0.5
        wave_strength = 0.2 + wave * 0.3

        # kick による光量アップ
        alpha = int(alpha * (1.0 + self.kick_strength * 0.8))

        # 非線形拡散
        current_radius = int(self.base_radius * (1 + (1 - fade) * 0.6 + self.kick_strength * 0.4))

        # 描画用Surface
        glow_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)

        # 多層グロー
        for i in range(current_radius, 0, -3):
            intensity = alpha * (i / current_radius) * wave_strength
            pygame.draw.circle(
                glow_surface, (*self.color, int(intensity)), (current_radius, current_radius), i
            )

        # コア光
        core_alpha = int(alpha * 0.9)
        pygame.draw.circle(
            glow_surface,
            (255, 255, 255, core_alpha),
            (current_radius, current_radius),
            int(current_radius * 0.35),
        )

        # ★ 加算合成（BLEND_ADD） ← 商用品質の決定打
        screen.blit(
            glow_surface,
            (self.pos[0] - current_radius, self.pos[1] - current_radius),
            special_flags=pygame.BLEND_ADD,
        )

    # ============================================================
    # リセット処理
    # ============================================================

    def reset(self):
        self.elapsed = 0
        self.active = True
        self.kick_strength = 0.0
