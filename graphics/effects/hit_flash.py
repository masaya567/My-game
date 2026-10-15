import pygame
import math


class HitFlash:
    """
    商用品質：判定爆光エフェクト（完全安全版）
    Perfect / Great / Good の強度と色に完全対応
    """

    def __init__(self, x, y, color=(255, 255, 255), strength=1.0):
        self.x = x
        self.y = y
        self.color = tuple(int(channel) for channel in color[:3])
        self.strength = max(0.0, min(1.0, float(strength)))

        self.timer = 0.0
        self.finished = False

    def update(self, dt):
        self.timer += dt
        if self.timer > 0.18:
            self.finished = True

    def draw(self, screen):
        if self.finished:
            return

        # easing（プロセカ風）
        t = self.timer / 0.18
        ease = t**0.55

        # 半径
        base_radius = 45
        radius = base_radius + ease * 240

        # alpha
        alpha = max(0, int((1 - t) * 255 * self.strength))

        # -----------------------------
        # ① 中心コア光（安全版）
        # -----------------------------
        core_radius = int(radius * 0.45)
        core_surf = pygame.Surface((core_radius * 2, core_radius * 2), pygame.SRCALPHA)

        pygame.draw.circle(
            core_surf, (255, 255, 255), (core_radius, core_radius), core_radius  # ★ RGBのみ
        )
        core_surf.set_alpha(int(alpha * 0.9))

        screen.blit(
            core_surf, (self.x - core_radius, self.y - core_radius), special_flags=pygame.BLEND_ADD
        )

        # -----------------------------
        # ② 外側グロー（安全版）
        # -----------------------------
        for i in range(5):
            layer_radius = radius + i * 28
            layer_alpha = max(0, min(255, int(alpha * (0.75 - i * 0.15))))

            surf = pygame.Surface((int(layer_radius * 2), int(layer_radius * 2)), pygame.SRCALPHA)

            pygame.draw.circle(
                surf,
                self.color[:3],  # ★ RGBのみ
                (int(layer_radius), int(layer_radius)),
                int(layer_radius),
            )
            surf.set_alpha(layer_alpha)

            screen.blit(
                surf, (self.x - layer_radius, self.y - layer_radius), special_flags=pygame.BLEND_ADD
            )
