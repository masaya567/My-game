import pygame
import pygame.gfxdraw
import math
from constants import (
    NOTE_HEIGHT,
    NOTE_START_Y,
    LANE_WIDTH,
    LANE_X,
)

from graphics.long_head import LongHead
from graphics.long_body import LongBody
from graphics.long_tail import LongTail
from graphics.long_shadow import LongShadow
from graphics.long_beam import LongBeam

from graphics.effects.hit_flash import HitFlash
from graphics.effects.spark_particle import SparkParticle
from utils.theme.theme import get_ui_scale


# ============================================================
# 商用品質：短ノーツ専用レンダラー（UI_SCALE＋pulse＋押し込み＋AA）
# ============================================================

class ShortNoteRenderer:
    def __init__(self, color=(255, 180, 180)):
        self.scale = get_ui_scale()
        self.base_color = tuple(color[:3])
        self.radius = int(22 * self.scale)
        self.timer = 0.0
        self.pulse = 0.0
        self.holding = False
        self.alpha = 255

        self.cached_base = None
        self.cached_color = None

    def _build_cache(self, color):
        color = tuple(int(c) for c in color[:3])
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        cx, cy = self.radius, self.radius

        # 外側グロー（多層）
        for i in range(14):
            a = int(140 * (1 - i / 14))
            pygame.gfxdraw.filled_circle(surf, cx, cy, self.radius + i, (*color, a))
            pygame.gfxdraw.aacircle(surf, cx, cy, self.radius + i, (*color, a))

        # コア光
        pygame.gfxdraw.filled_circle(surf, cx, cy, int(self.radius * 0.75), (*color, 255))
        pygame.gfxdraw.aacircle(surf, cx, cy, int(self.radius * 0.75), (*color, 255))

        # 白い中心光
        pygame.gfxdraw.filled_circle(surf, cx, cy, int(self.radius * 0.45), (255, 255, 255, 255))
        pygame.gfxdraw.aacircle(surf, cx, cy, int(self.radius * 0.45), (255, 255, 255, 255))

        self.cached_base = surf
        self.cached_color = color

    def update(self, dt, holding, pulse):
        self.holding = holding
        self.pulse = pulse

        if pulse is not None:
            self.timer = float(pulse)
        elif holding:
            self.timer += dt * 4
        else:
            self.timer = 0.0

    def draw(self, screen, x, y):
        color = self.base_color

        if self.cached_base is None or self.cached_color != color:
            self._build_cache(color)

        surf = self.cached_base.copy()

        wobble = math.sin(self.pulse * 3.5) * 4 * self.scale

        if self.holding:
            scale = 1.0 + (0.12 * math.sin(self.timer * 20))
            size = int(self.radius * 2 * scale)
            surf = pygame.transform.smoothscale(surf, (size, size))
        else:
            scale = 1.0
            size = self.radius * 2

        if self.holding:
            pulse = (math.sin(self.timer) + 1) * 0.5
            glow = pygame.Surface((size, size), pygame.SRCALPHA)
            alpha = int(120 * pulse)

            pygame.gfxdraw.filled_circle(
                glow,
                size // 2,
                size // 2,
                int(self.radius * scale),
                (*color, alpha),
            )
            pygame.gfxdraw.aacircle(
                glow,
                size // 2,
                size // 2,
                int(self.radius * scale),
                (*color, alpha),
            )

            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        surf.set_alpha(self.alpha)

        screen.blit(
            surf,
            (x - size // 2 + wobble, y - size // 2),
            special_flags=pygame.BLEND_ADD,
        )


class NoteRenderer:
    """
    商用品質：判定位置と描画位置が完全一致する最終統合版
    - ショート／ロングノーツ
    - pulse 完全同期
    - StartFlash / EndSpark
    - 描画ズレゼロ（反応改善版）
    """

    def __init__(self, lane: int, is_long=False):
        self.lane = lane
        self.is_long = is_long
        self.short_height = NOTE_HEIGHT

        self.pulse_timer = 0.0

        # 商用品質短ノーツレンダラー
        self.short_renderer = ShortNoteRenderer()

        if is_long:
            self.long_head = LongHead()
            self.long_body = LongBody()
            self.long_tail = LongTail()
            self.long_shadow = LongShadow()
            self.long_beam = LongBeam(width=LANE_WIDTH)
        else:
            self.long_head = None
            self.long_body = None
            self.long_tail = None
            self.long_shadow = None
            self.long_beam = None

        self.hit_flash = None
        self.spark_particles = []

    # ============================================================
    # ショートノーツ描画（商用品質版）
    # ============================================================

    def draw_short(self, screen, x, y, alpha=255, holding=False, pulse=None):
        self.short_renderer.alpha = alpha
        self.short_renderer.update(0.0, holding, pulse if pulse is not None else self.pulse_timer)
        self.short_renderer.draw(screen, x, y)

    # ============================================================
    # ロングノーツ描画（head_y / tail_y と完全同期）
    # ============================================================

    def draw_long(self, screen, x, head_y, height, holding):
        self.long_shadow.draw(screen, x, head_y, height, holding)
        self.long_body.draw(screen, x, head_y, height, holding)
        self.long_head.draw(screen, x, head_y, holding)
        self.long_tail.draw(screen, x, head_y + height, holding)
        self.long_beam.draw(screen, x=x, head_y=head_y, height=height, holding=holding)
        self.draw_particles(screen)

    def update(self, dt, holding=False, pulse=None):
        pulse = self.pulse_timer if pulse is None else pulse

        if self.is_long:
            brightness = 1.0 if holding else 0.0
            
            self.long_shadow.update(dt, holding, pulse)
            self.long_body.update(dt, holding, pulse)
            self.long_head.update(dt, holding, pulse)
            self.long_tail.update(dt, holding, pulse)
            self.long_beam.update(dt, holding, pulse, brightness)

        # 短ノーツ側の pulse も同期させたい場合はここで更新してもいい
        self.short_renderer.update(dt, holding, pulse)

        if self.hit_flash:
            self.hit_flash.update(dt)
            if self.hit_flash.finished:
                self.hit_flash = None

        for p in self.spark_particles:
            p.update(dt)
        self.spark_particles = [p for p in self.spark_particles if not p.finished]

    def draw_particles(self, screen):
        if self.hit_flash:
            self.hit_flash.draw(screen)
        for particle in self.spark_particles:
            particle.draw(screen)

    # ============================================================
    # StartFlash
    # ============================================================

    def trigger_head_flash(self, x, y, color, strength):
        self.hit_flash = HitFlash(x, y, color, strength)

    # ============================================================
    # EndSpark
    # ============================================================

    def trigger_tail_spark(self, x, y, color, strength):
        self.spark_particles.append(SparkParticle(x, y, color, strength))
