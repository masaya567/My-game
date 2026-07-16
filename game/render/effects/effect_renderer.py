"""
商用品質：エフェクト統合描画モジュール（完全版）

・Z-order（描画優先度）
・種類別管理
・高速化（remove inactive）
・商用品質エフェクトと完全連携
"""

import pygame


class EffectRenderer:
    """
    商用品質：エフェクト統合描画クラス
    """

    def __init__(self):
        # 種類別に管理（商用品質）
        self.layers = {
            "background": [],  # 背景光（Glow）
            "judge": [],  # 判定エフェクト（Ring / Beam / Burst）
            "combo": [],  # コンボ演出
            "ui": [],  # UI演出
        }

    # ============================================================
    # エフェクト追加（商用品質）
    # ============================================================

    def add(self, effect, layer="judge"):
        """任意のエフェクトを追加（商用品質）"""
        if layer not in self.layers:
            layer = "judge"
        self.layers[layer].append(effect)

    def add_glow(self, pos, color=(255, 255, 255)):
        from game.render.effects.glow_effect import GlowEffect

        glow = GlowEffect(pos, color=color)
        self.layers["background"].append(glow)

    def add_beam(self, pos, color=(255, 255, 255)):
        from game.render.effects.judge_beam import JudgeBeam

        beam = JudgeBeam(pos, color=color)
        self.layers["judge"].append(beam)

    # ============================================================
    # 更新処理（商用品質）
    # ============================================================

    def update(self, dt):
        """全エフェクトを更新し、終了したものを削除（高速化）"""
        for layer_name, effects in self.layers.items():
            for effect in effects:
                effect.update(dt)

            # 非アクティブなエフェクトを削除（高速化）
            self.layers[layer_name] = [e for e in effects if e.active]

    # ============================================================
    # 描画処理（商用品質）
    # ============================================================

    def draw(self, screen):
        """
        商用品質：描画順を保証する
        background → judge → combo → ui
        """
        # Z-order に従って描画
        for layer_name in ["background", "judge", "combo", "ui"]:
            for effect in self.layers[layer_name]:
                effect.draw(screen)

    # ============================================================
    # 全削除処理
    # ============================================================

    def clear(self):
        """全エフェクトを削除"""
        for layer in self.layers.values():
            layer.clear()
