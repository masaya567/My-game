"""
商用品質：背景描画モジュール（完全版・最終形態）

ゲームプレイ中の背景アニメーションと発光効果を統合する。
"""

import pygame
import random
from graphics.common import create_vertical_gradient


class BackgroundRenderer:
    """
    商用品質：背景描画統合クラス
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.tiles = [self._create_tile() for _ in range(14)]
        self.glow_intensity = 0.0
        self.flash = 0.0

    # ============================================================
    # 背景タイル生成
    # ============================================================

    def _create_tile(self):
        return {
            "x": random.randint(0, self.width),
            "y": random.randint(-self.height, 0),
            "w": random.randint(60, 120),
            "h": random.randint(200, 350),
            "speed": random.uniform(80, 150),
            "color": (220, 230, 255),
        }

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float, combo: int, judge_text: str):
        """背景アニメーションを更新"""

        # コンボ連動発光
        target = min(1.0, combo / 150)
        self.glow_intensity += (target - self.glow_intensity) * 0.05

        # Perfect 判定時の白光
        if judge_text == "Perfect!":
            self.flash = 1.0

        self.flash = max(0.0, self.flash - dt * 3)

        # タイル更新
        for i, tile in enumerate(self.tiles):
            tile["y"] += tile["speed"] * dt
            if tile["y"] > self.height:
                self.tiles[i] = self._create_tile()

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen: pygame.Surface):
        """背景を描画"""

        # --- グラデーション背景 ---
        gradient = create_vertical_gradient(
            self.width,
            self.height,
            (40, 60, 120),
            (10, 20, 40),
        )
        screen.blit(gradient, (0, 0))

        # --- タイル描画 ---
        for tile in self.tiles:
            pygame.draw.rect(
                screen,
                tile["color"],
                (tile["x"], tile["y"], tile["w"], tile["h"]),
                border_radius=20,
            )

        # --- コンボ発光オーバーレイ（加算合成） ---
        power = min(1.0, self.glow_intensity + self.flash)
        if power > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((80, 120, 255, int(180 * power)))
            screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
