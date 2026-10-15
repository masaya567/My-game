"""
商用品質：エフェクト統合管理モジュール（完全版・最終形態＋虹色化統合＋爆光統合）
"""

import pygame

from graphics.effects.judge_ring import JudgeRing
from graphics.effects.judge_burst import JudgeBurst
from graphics.effects.ripple_effect import RippleEffect
from graphics.effects.lane_flash import LaneFlash
from graphics.effects.glow_circle import GlowCircle
from graphics.effects.judge_text_effect import JudgeTextEffect
from graphics.effects.judge_beam import JudgeBeam
from graphics.effects.hit_line import HitLine

# ★ コンボ切れ演出
from graphics.effects.combo_break_burst import ComboBreakBurst

from constants import JUDGE_COLORS, LANE_WIDTH, JUDGE_LINE, WIDTH, HEIGHT


class EffectManager:
    """
    商用品質：判定演出フルセット統合クラス（最終形態）
    + コンボ切れ演出
    + Perfect 爆光（spawn_hit_flash）
    + コンボ2000時の虹色化
    """

    def __init__(self):
        self.effects = []
        self.logic = None  # ★ GameplayScreen から combo を参照するため

        # ★ Perfect 爆光（白い円形フラッシュ）
        self.hit_flashes = []  # {x, alpha, radius}
        self._hit_flash_base = pygame.Surface((240, 240), pygame.SRCALPHA)
        pygame.draw.circle(self._hit_flash_base, (255, 255, 255), (120, 120), 120)
        self._hit_flash_surfaces = {240: self._hit_flash_base}

    # ============================================================
    # 判定演出フルセット
    # ============================================================

    def spawn_hit_effect(self, lane_x, judge_text, font, strength):
        jt = judge_text.lower()

        color = tuple(int(c) for c in JUDGE_COLORS.get(jt, (255, 255, 255))[:3])
        strength = max(0.0, min(1.0, float(strength)))

        center_x = lane_x
        judge_y = JUDGE_LINE

        # 判定ライン光
        self.effects.append(JudgeBeam(center_x, judge_y, color, strength))
        self.effects.append(HitLine(center_x, judge_y, color, strength))

        # 波紋
        self.effects.append(RippleEffect(judge_y, color, strength))

        # 爆光・光輪
        self.effects.append(JudgeBurst((center_x, judge_y), color))
        self.effects.append(JudgeRing((center_x, judge_y), color))

        # レーン光（位置修正）
        lf = LaneFlash(lane_x, LANE_WIDTH, strength)
        lf.trigger()
        self.effects.append(lf)

        # 円形発光
        self.effects.append(GlowCircle((center_x, judge_y), color))

        # 判定文字
        self.effects.append(
            JudgeTextEffect(
                center_x,
                judge_y - 40,
                judge_text.upper(),
                color,
                font,
                strength=strength,
            )
        )

    def spawn_combo_ring(self, x, y):
        self.effects.append(JudgeRing(x, y, (255, 255, 255)))

    # ============================================================
    # ★ Perfect 爆光（プロセカ式）
    # ============================================================

    def spawn_hit_flash(self, x):
        """
        Perfect の瞬間に白い爆光を出す演出。
        effects.py の spawn_hit_effect() から呼ばれる。
        """
        self.hit_flashes.append(
            {
                "x": x,
                "alpha": 255,
                "radius": 120,
            }
        )

    # ============================================================
    # ★ コンボ切れ演出（MISS時）
    # ============================================================

    def spawn_combo_break(self, lane_x):
        center_x = lane_x + LANE_WIDTH // 2
        self.effects.append(ComboBreakBurst((center_x, JUDGE_LINE)))

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

        # ★ Perfect 爆光の減衰処理
        for flash in self.hit_flashes[:]:
            flash["alpha"] *= 0.88
            flash["radius"] *= 0.92

            if flash["alpha"] < 5:
                self.hit_flashes.remove(flash)

        # ★ コンボ2000で判定ライン虹色化
        if self.logic is not None:
            combo = getattr(self.logic, "combo", 0)
            if combo == 2000:
                for e in self.effects:
                    if isinstance(e, JudgeBeam):
                        e.trigger_rainbow()

    # ============================================================
    # 描画（dt を使わない設計に統一）
    # ============================================================

    def draw(self, screen):
        # 通常エフェクト
        for e in self.effects:
            e.draw(screen)

        # ★ Perfect 爆光描画
        for flash in self.hit_flashes:
            radius = max(1, int(flash["radius"]))
            diameter = radius * 2
            surf = self._hit_flash_surfaces.get(diameter)
            if surf is None:
                surf = pygame.transform.smoothscale(self._hit_flash_base, (diameter, diameter))
                self._hit_flash_surfaces[diameter] = surf
            surf.set_alpha(int(flash["alpha"]))
            screen.blit(
                surf,
                (int(flash["x"] - radius), JUDGE_LINE - radius),
                special_flags=pygame.BLEND_ADD,
            )

    # ============================================================
    # リセット
    # ============================================================

    def clear(self):
        self.effects.clear()
        self.hit_flashes.clear()
