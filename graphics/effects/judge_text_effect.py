"""
商用品質：判定テキスト演出モジュール（跳ねるアニメ・最終形態）
"""

import pygame
import random
import math


class JudgeTextEffect:
    def __init__(self, x, y, text, color, font, strength=1.0):
        self.x = x
        self.y = y
        self.text = text
        self.color = tuple(int(channel) for channel in color[:3])
        self.font = font
        self.strength = max(0.0, min(1.0, float(strength)))

        self.timer = 0.0
        self.alpha = 255
        self.scale = 1.0
        self.is_alive = True

        # 残光リング
        self.ring_radius = 0
        self.ring_alpha = int(200 * self.strength)

        # スパーク粒子
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

    def update(self, dt):
        self.timer += max(0.0, dt)

        # ---------------------------
        # ★ 跳ねるアニメ（4段階）
        # ---------------------------

        # 大きく出てから少し縮み、基準サイズへ戻すプロセカ風の跳ね。
        if self.timer < 0.16:
            t = self.timer / 0.16
            self.scale = 1.0 + (0.52 * self.strength) * math.sin(t * math.pi / 2)
        else:
            t = min(1.0, (self.timer - 0.16) / 0.18)
            self.scale = 1.0 + (0.10 * self.strength) * (1.0 - t) * math.sin(t * math.pi)

        if self.timer >= 0.28:
            fade_t = min(1.0, (self.timer - 0.28) / 0.25)
            self.alpha = max(0, int(255 * (1 - fade_t)))

        # ---------------------------
        # 残光リング
        # ---------------------------
        self.ring_radius += dt * 480
        self.ring_alpha = max(0, int(self.ring_alpha - dt * 480))

        # ---------------------------
        # スパーク粒子
        # ---------------------------
        for s in self.sparks:
            s["life"] -= dt
            s["vx"] *= 0.96
            s["vy"] *= 0.96

        if self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen, dt=0.0):
        if not self.is_alive:
            return

        # フォントスケール
        size = int(48 * self.scale)
        font_scaled = pygame.font.SysFont(None, size)

        surf = font_scaled.render(self.text, True, self.color)
        surf.set_alpha(self.alpha)

        outline = font_scaled.render(self.text, True, (0, 0, 0))
        outline.set_alpha(self.alpha)

        cx = self.x - surf.get_width() // 2
        cy = self.y - surf.get_height() // 2

        # 上方向へ跳ね上がり、着地時だけ小さく揺らす。
        rise = 34 * min(1.0, self.timer / 0.16) * self.strength
        settle = min(1.0, max(0.0, (self.timer - 0.16) / 0.18))
        bounce = math.sin(settle * math.pi) * 8 * self.strength

        # 黒縁取り
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            screen.blit(outline, (cx + dx, cy + dy - bounce - rise))

        screen.blit(surf, (cx, cy - bounce - rise))

        # ---------------------------
        # ★ 残光リング（加算合成）
        # ---------------------------
        if self.ring_alpha > 0:
            r = int(self.ring_radius)
            ring = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            ring_color = (*self.color, int(max(0, min(255, self.ring_alpha))))
            pygame.draw.circle(ring, ring_color, (r, r), r, 3)
            screen.blit(ring, (self.x - r, self.y - r), special_flags=pygame.BLEND_ADD)

        # ---------------------------
        # スパーク粒子
        # ---------------------------
        for s in self.sparks:
            if s["life"] > 0:
                sx = self.x + s["vx"] * dt
                sy = self.y + s["vy"] * dt

                pygame.draw.circle(
                    screen,
                    (*self.color, int(max(0, min(255, self.alpha)))),
                    (int(sx), int(sy)),
                    s["radius"],
                )
