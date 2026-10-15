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

_SHORT_NOTE_SURFACE_CACHE = {}


def _get_short_note_surfaces(width, height):
    key = (width, height)
    surfaces = _SHORT_NOTE_SURFACE_CACHE.get(key)
    if surfaces is not None:
        return surfaces

    body = pygame.Surface((width, height), pygame.SRCALPHA)
    for row in range(height):
        ratio = row / max(1, height)
        channel = int(255 * (0.85 + 0.15 * (1 - ratio)))
        pygame.draw.line(body, (255, channel, channel), (0, row), (width - 1, row))

    glow = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
    center = (glow.get_width() // 2, glow.get_height() // 2)
    radii = (glow.get_width() // 2, glow.get_height() // 2)
    pygame.gfxdraw.filled_ellipse(glow, *center, *radii, (255, 255, 255, 255))
    pygame.gfxdraw.aaellipse(glow, *center, *radii, (255, 255, 255, 255))

    surfaces = body, glow
    _SHORT_NOTE_SURFACE_CACHE[key] = surfaces
    return surfaces


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

        if is_long:
            self.long_head = LongHead()
            self.long_body = LongBody()
            self.long_tail = LongTail()
            self.long_shadow = LongShadow()
            self.long_beam = LongBeam(width=LANE_WIDTH, y=NOTE_START_Y, lane_x=LANE_X[lane])
        else:
            self.long_head = None
            self.long_body = None
            self.long_tail = None
            self.long_shadow = None
            self.long_beam = None

        self.hit_flash = None
        self.spark_particles = []

    # ============================================================
    # ショートノーツ描画（描画位置を head_y と完全一致）
    # ============================================================

    def draw_short(self, screen, x, y, alpha=255):
        w = LANE_WIDTH
        h = self.short_height
        body, glow = _get_short_note_surfaces(w, h)
        glow.set_alpha(int(alpha * 0.35))
        body.set_alpha(alpha)

        screen.blit(glow, (x - w // 2 - 10, y - h // 2 - 10))
        screen.blit(body, (x - w // 2, y - h // 2))

    # ============================================================
    # ロングノーツ描画（head_y / tail_y と完全同期）
    # ============================================================

    def draw_long(self, screen, x, head_y, height, holding):
        # 描画順
        self.long_shadow.draw(screen, x, head_y, height, holding)
        self.long_body.draw(screen, x, head_y, height, holding)
        self.long_head.draw(screen, x, head_y, holding)

        # ★ 修正：tail の描画位置を内部判定と完全一致
        self.long_tail.draw(screen, x, head_y + height, holding)

        self.long_beam.draw(screen, x=x, head_y=head_y, height=height, holding=holding)

        self.draw_particles(screen)

    def update(self, dt, holding=False, pulse=None):
        pulse = self.pulse_timer if pulse is None else pulse
        if self.is_long:
            self.long_shadow.update(dt, holding, pulse)
            self.long_body.update(dt, holding, pulse)
            self.long_head.update(dt, holding, pulse)
            self.long_tail.update(dt, holding, pulse)
            self.long_beam.update(dt, holding, pulse)

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
