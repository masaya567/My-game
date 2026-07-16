"""
商用品質：ロングノーツ末端描画モジュール（AA強化＋キャッシュ化・最終形態）

ロングノーツの終端部分を描画し、押下時の発光・波動・加算合成を統合する。
アンチエイリアス（AA）により光球の輪郭を滑らかにし、キャッシュ化でFPSを最適化する。
"""

import pygame
import math
import pygame.gfxdraw


class LongTail:
    """
    商用品質：ロングノーツ末端描画クラス（AA強化＋キャッシュ化）
    """

    cached_base = None  # 光球のベースレイヤー（キャッシュ）

    def __init__(self, color=(120, 200, 255), radius=20):
        self.color = color
        self.radius = radius
        self.alpha = 255
        self.active = True
        self.timer = 0.0

    # ============================================================
    # キャッシュ生成
    # ============================================================

    def _build_cache(self):
        """光球のベースレイヤーをキャッシュとして生成（AA強化）"""

        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        cx, cy = self.radius, self.radius

        # 多層グラデーション（AA）
        for r in range(self.radius, 0, -1):
            pygame.gfxdraw.filled_circle(surf, cx, cy, r, (*self.color, 255))
            pygame.gfxdraw.aacircle(surf, cx, cy, r, (*self.color, 255))

        LongTail.cached_base = surf

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float, holding: bool) -> None:
        if not self.active:
            return

        if holding:
            self.timer += dt * 4
        else:
            self.timer = 0.0

        fade_speed = 0.8
        self.alpha = max(0, self.alpha - fade_speed * dt)
        if self.alpha <= 0:
            self.active = False

    # ============================================================
    # 描画処理（キャッシュ使用）
    # ============================================================

    def draw(self, screen: pygame.Surface, x: float, y: float, holding: bool) -> None:
        if not self.active:
            return

        # キャッシュがなければ生成
        if LongTail.cached_base is None:
            self._build_cache()

        # ベースレイヤーをコピー
        surf = LongTail.cached_base.copy()

        # 押下中の発光パルス（加算合成で上書き）
        pulse = (math.sin(self.timer) + 1) * 0.5 if holding else 0

        if holding:
            glow = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            alpha = int(120 * pulse)

            pygame.gfxdraw.filled_circle(
                glow, self.radius, self.radius, self.radius, (*self.color, alpha)
            )
            pygame.gfxdraw.aacircle(
                glow, self.radius, self.radius, self.radius, (*self.color, alpha)
            )

            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        # 加算合成で描画
        screen.blit(
            surf,
            (x - self.radius, y - self.radius),
            special_flags=pygame.BLEND_ADD,
        )

    # ============================================================
    # リセット処理
    # ============================================================

    def reset(self):
        self.alpha = 255
        self.active = True
        self.timer = 0.0
