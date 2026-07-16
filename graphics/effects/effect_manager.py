"""
商用品質：エフェクト統合管理モジュール（完全版・最終形態）

全エフェクトの生成・更新・描画を一括で管理する。
"""

import pygame
from graphics.effects.judge_ring import JudgeRing
from graphics.effects.judge_burst import JudgeBurst
from graphics.effects.ripple_effect import RippleEffect
from graphics.effects.lane_flash import LaneFlash
from graphics.effects.glow_circle import GlowCircle


class EffectManager:
    """
    商用品質：エフェクト統合管理クラス
    """

    def __init__(self):
        self.effects = []

    # ============================================================
    # エフェクト生成
    # ============================================================

    def spawn_judge_ring(self, x: float, y: float, color=(120, 200, 255)):
        self.effects.append(JudgeRing(x, y, color))

    def spawn_judge_burst(self, x: float, y: float, color=(255, 255, 255)):
        self.effects.append(JudgeBurst(x, y, color))

    def spawn_ripple(self, x: float, y: float, color=(120, 200, 255)):
        self.effects.append(RippleEffect(x, y, color))

    def spawn_lane_flash(self, lane_x: float, color=(255, 255, 255)):
        self.effects.append(LaneFlash(lane_x, color))

    def spawn_glow_circle(self, x: float, y: float, color=(255, 255, 255)):
        self.effects.append(GlowCircle(x, y, color))

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float):
        """全エフェクトを更新"""
        alive_effects = []
        for effect in self.effects:
            effect.update(dt)

            # 商用品質：エフェクトの生存判定
            if hasattr(effect, "is_alive"):
                if effect.is_alive:
                    alive_effects.append(effect)
            else:
                # alpha がある場合は alpha で判定
                if getattr(effect, "alpha", 255) > 0:
                    alive_effects.append(effect)

        self.effects = alive_effects

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen: pygame.Surface):
        for effect in self.effects:
            effect.draw(screen)

    # ============================================================
    # リセット処理
    # ============================================================

    def clear(self):
        self.effects.clear()
