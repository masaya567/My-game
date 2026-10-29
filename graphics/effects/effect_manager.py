"""
商用品質：エフェクト統合管理モジュール（UI_SCALE対応・完全版）
"""

import pygame
from constants import JUDGE_COLORS, LANE_WIDTH, JUDGE_LINE, WIDTH, HEIGHT
from utils.theme.theme import get_ui_scale

from graphics.effects.judge_ring import JudgeRing
from graphics.effects.judge_burst import JudgeBurst
from graphics.effects.ripple_effect import RippleEffect
from graphics.effects.lane_flash import LaneFlash
from graphics.effects.glow_circle import GlowCircle
from graphics.effects.judge_text_effect import JudgeTextEffect
from graphics.effects.judge_beam import JudgeBeam
from graphics.effects.hit_line import HitLine
from graphics.effects.combo_break_burst import ComboBreakBurst


class EffectManager:
    def __init__(self):
        self.effects = []
        self.logic = None

        # ★ UI_SCALE 対応
        self.scale = get_ui_scale()

        # ============================================================
        # Perfect 爆光キャッシュ（UI_SCALE対応）
        # ============================================================
        base_size = int(240 * self.scale)
        self.hit_flashes = []  # {x, alpha, radius}

        self._hit_flash_base = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
        pygame.draw.circle(
            self._hit_flash_base,
            (255, 255, 255),
            (base_size // 2, base_size // 2),
            base_size // 2,
        )

        self._hit_flash_cache = {base_size: self._hit_flash_base}

    # ============================================================
    # 判定演出フルセット（UI_SCALE対応）
    # ============================================================

    def spawn_hit_effect(self, lane_x, judge_text, font, strength):
        jt = judge_text.lower()
        color = tuple(int(c) for c in JUDGE_COLORS.get(jt, (255, 255, 255))[:3])
        strength = max(0.0, min(1.0, float(strength)))

        cx = lane_x
        cy = JUDGE_LINE

        # 判定ライン光（UI_SCALE対応）
        self.effects.append(JudgeBeam(cx, cy, color, strength))
        self.effects.append(HitLine(cx, cy, color, strength))

        # 波紋（UI_SCALE対応）
        self.effects.append(RippleEffect(cy, color, strength))

        # 爆光・光輪（UI_SCALE対応済み）
        self.effects.append(JudgeBurst((cx, cy), color))
        self.effects.append(JudgeRing((cx, cy), color))

        # レーン光（UI_SCALE対応）
        lf = LaneFlash(lane_x, int(LANE_WIDTH * self.scale), strength)
        lf.trigger()
        self.effects.append(lf)

        # 円形発光（UI_SCALE対応済み）
        self.effects.append(GlowCircle((cx, cy), color))

        # 判定文字（UI_SCALE対応）
        self.effects.append(
            JudgeTextEffect(
                cx,
                cy - int(40 * self.scale),
                judge_text.upper(),
                color,
                font,
                strength=strength,
            )
        )

    # ============================================================
    # Perfect 爆光（プロセカ式・UI_SCALE対応）
    # ============================================================

    def spawn_hit_flash(self, x):
        self.hit_flashes.append(
            {
                "x": x,
                "alpha": 255,
                "radius": int(120 * self.scale),
            }
        )

    # ============================================================
    # コンボ切れ演出（UI_SCALE対応）
    # ============================================================

    def spawn_combo_break(self, lane_x):
        cx = lane_x + int(LANE_WIDTH * self.scale) // 2
        self.effects.append(ComboBreakBurst((cx, JUDGE_LINE)))

    # ============================================================
    # 更新
    # ============================================================

    def update(self, dt):
        alive = []
        for e in self.effects:
            e.update(dt)

            if hasattr(e, "is_alive"):
                if e.is_alive:
                    alive.append(e)
            else:
                if getattr(e, "alpha", 255) > 0:
                    alive.append(e)

        self.effects = alive

        # Perfect 爆光の減衰（UI_SCALE対応）
        for flash in self.hit_flashes[:]:
            flash["alpha"] *= 0.88
            flash["radius"] *= 0.92

            if flash["alpha"] < 5:
                self.hit_flashes.remove(flash)

        # コンボ2000で虹色化
        if self.logic is not None:
            combo = getattr(self.logic, "combo", 0)
            if combo == 2000:
                for e in self.effects:
                    if isinstance(e, JudgeBeam):
                        e.trigger_rainbow()

    # ============================================================
    # 描画（UI_SCALE対応）
    # ============================================================

    def draw(self, screen):
        for e in self.effects:
            e.draw(screen)

        # Perfect 爆光
        for flash in self.hit_flashes:
            radius = max(1, int(flash["radius"]))
            diameter = radius * 2

            surf = self._hit_flash_cache.get(diameter)
            if surf is None:
                surf = pygame.transform.smoothscale(self._hit_flash_base, (diameter, diameter))
                self._hit_flash_cache[diameter] = surf

            surf.set_alpha(int(flash["alpha"]))
            screen.blit(
                surf,
                (int(flash["x"] - radius), JUDGE_LINE - radius),
                special_flags=pygame.BLEND_ADD,
            )

    def clear(self):
        self.effects.clear()
        self.hit_flashes.clear()
