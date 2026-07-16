"""
商用品質：ロングノーツヘッド描画モジュール（AA強化＋キャッシュ化・最終形態）

ロングノーツの開始部分を描画し、押下時の発光を演出する。
アンチエイリアス（AA）で輪郭を滑らかにし、キャッシュ化でFPSを最適化する。
"""

import pygame
import math
import pygame.gfxdraw


class LongHead:
    """
    商用品質：ロングノーツヘッド描画クラス（AA強化＋キャッシュ化）
    """

    cached_base = None  # グロー＋コアのベースレイヤー（キャッシュ）

    def __init__(self, glow_strength: int = 120):
        self.glow_strength = glow_strength
        self.timer = 0.0

    # ============================================================
    # キャッシュ生成
    # ============================================================

    def _build_cache(self, color):
        """ヘッドのベースレイヤーをキャッシュとして生成（AA強化）"""

        surf = pygame.Surface((60, 40), pygame.SRCALPHA)

        cx, cy = 30, 20

        # 外側グロー（多層）
        for i in range(15):
            alpha = int(self.glow_strength * (1 - i / 15))
            pygame.gfxdraw.filled_ellipse(surf, cx, cy, 15 + i, 10 + i, (*color, alpha))
            pygame.gfxdraw.aaellipse(surf, cx, cy, 15 + i, 10 + i, (*color, alpha))

        # 内側コア
        pygame.gfxdraw.filled_ellipse(surf, cx, cy, 10, 8, (*color, 255))
        pygame.gfxdraw.aaellipse(surf, cx, cy, 10, 8, (*color, 255))

        # 白い中心光
        pygame.gfxdraw.filled_ellipse(surf, cx, cy, 6, 6, (255, 255, 255, 255))
        pygame.gfxdraw.aaellipse(surf, cx, cy, 6, 6, (255, 255, 255, 255))

        # 縁取り（線はAA不要）
        pygame.draw.ellipse(surf, (255, 255, 255, 200), (15, 10, 30, 20), 2)

        LongHead.cached_base = surf

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float, holding: bool) -> None:
        if holding:
            self.timer += dt * 4
        else:
            self.timer = 0.0

    # ============================================================
    # 描画処理（キャッシュ使用）
    # ============================================================

    def draw(
        self,
        screen: pygame.Surface,
        x: float,
        y: float,
        color=(120, 200, 255),
        holding: bool = False,
    ) -> None:

        # キャッシュがなければ生成
        if LongHead.cached_base is None:
            self._build_cache(color)

        # ベースレイヤーをコピー
        surf = LongHead.cached_base.copy()

        # 押下中の発光パルス（加算合成で上書き）
        pulse = (math.sin(self.timer) + 1) * 0.5 if holding else 0

        if holding:
            glow = pygame.Surface((60, 40), pygame.SRCALPHA)
            alpha = int(80 * pulse)

            pygame.gfxdraw.filled_ellipse(glow, 30, 20, 20, 14, (*color, alpha))
            pygame.gfxdraw.aaellipse(glow, 30, 20, 20, 14, (*color, alpha))

            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        # 加算合成で描画
        screen.blit(surf, (x, y - 10), special_flags=pygame.BLEND_ADD)
