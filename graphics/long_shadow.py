"""
商用品質：ロングノーツ影描画モジュール（AA強化＋キャッシュ化・最終形態）

ロングノーツの下層に半透明の影を描画し、立体感を演出する。
アンチエイリアスにより影の輪郭を滑らかにし、キャッシュ化でFPSを最適化する。
"""

import pygame
import math
import pygame.gfxdraw


class LongShadow:
    """
    商用品質：ロングノーツ影描画クラス（AA強化＋キャッシュ化）
    """

    # キャッシュされた影レイヤー
    cached_shadow = None
    cached_height = None

    def __init__(self, alpha: int = 70, width: int = 60):
        self.alpha = alpha
        self.width = width
        self.timer = 0.0

    # ============================================================
    # キャッシュ生成
    # ============================================================

    def _build_cache(self, height: int):
        """影の多層レイヤーをキャッシュとして生成（高さ依存）"""

        surf = pygame.Surface((self.width, height + 40), pygame.SRCALPHA)

        for i in range(12):
            alpha = int(self.alpha * (1 - i / 12))

            rect = pygame.Rect(
                10 - i,
                20 - i,
                self.width - 20 + i * 2,
                height + i * 2,
            )

            pygame.gfxdraw.box(surf, rect, (0, 0, 0, alpha))

        LongShadow.cached_shadow = surf
        LongShadow.cached_height = height

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
        height: float,
        holding: bool,
    ) -> None:

        height = int(height)

        # キャッシュがない or 高さが変わったら再生成
        if LongShadow.cached_shadow is None or LongShadow.cached_height != height:
            self._build_cache(height)

        wobble = math.sin(self.timer * 3.5) * 2 if holding else 0

        # キャッシュされた影を描画
        screen.blit(LongShadow.cached_shadow, (x + wobble - self.width // 2, y - 20))
