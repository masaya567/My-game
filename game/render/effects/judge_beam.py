"""
商用仕様：判定ビームエフェクト（完全版）

指数フェード、揺らぎ、kick、コア光、多層構造、加算合成を備えた高品質ビーム。
"""

import pygame
import math


class JudgeBeam:
    """
    商用仕様：判定ビーム（完全版）
    """

    def __init__(self, pos, color=(255, 255, 255), length=320, width=14, duration=260):
        self.pos = pos
        self.color = color
        self.length = length
        self.width = width
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
        wave = (math.sin(self.elapsed * 0.04) + 1) * 0.5
        wave_strength = 0.7 + wave * 0.3

        # kick による光量アップ
        alpha = int(alpha * (1.0 + self.kick_strength * 0.9))

        # 非線形縮小
        current_length = int(self.length * fade * (1.0 + self.kick_strength * 0.4))

        # 描画用 Surface
        beam_surface = pygame.Surface((current_length, self.width), pygame.SRCALPHA)

        # 多層ビーム（外側の柔らかい光）
        layers = 6
        for i in range(layers):
            layer_alpha = int(alpha * (1 - i / layers) * wave_strength)
            pygame.draw.rect(
                beam_surface,
                (*self.color, layer_alpha),
                (0, i, current_length, self.width - i * 2),
            )

        # コア光（中心の強い白光）
        core_alpha = int(alpha * 0.9)
        pygame.draw.rect(
            beam_surface,
            (255, 255, 255, core_alpha),
            (0, self.width // 3, current_length, self.width // 3),
        )

        # ★ 加算合成（BLEND_ADD） ← 商用品質の決定打
        beam_rect = beam_surface.get_rect(center=self.pos)
        screen.blit(beam_surface, beam_rect, special_flags=pygame.BLEND_ADD)

    # ============================================================
    # リセット処理
    # ============================================================

    def reset(self):
        self.elapsed = 0
        self.active = True
        self.kick_strength = 0.0
