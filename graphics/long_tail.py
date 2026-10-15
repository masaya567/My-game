"""
商用品質：ロングノーツ末端描画モジュール
AA強化＋キャッシュ化＋押し込み強化・最終形態
"""

import pygame
import math
import pygame.gfxdraw
from typing import Optional


class LongTail:
    """
    商用品質：ロングノーツ末端描画クラス（AA＋キャッシュ＋押し込み強化）
    """

    def __init__(self, color=(120, 200, 255), radius=20):
        self.color = tuple(color[:3])
        self.radius = radius
        self.alpha = 255
        self.active = True
        self.timer = 0.0
        self.cached_base = None

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

        self.cached_base = surf

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float, holding: bool, pulse: Optional[float] = None) -> None:
        if not self.active:
            return

        if pulse is not None:
            self.timer = float(pulse)
        elif holding:
            self.timer += dt * 4
        else:
            self.timer = 0.0

        # フェードアウト
        fade_speed = 0.8
        self.alpha = max(0, self.alpha - fade_speed * dt)
        if self.alpha <= 0:
            self.active = False

    # ============================================================
    # 描画処理（キャッシュ使用＋押し込み強化）
    # ============================================================

    def draw(self, screen: pygame.Surface, x: float, y: float, holding: bool) -> None:
        if not self.active:
            return

        # キャッシュがなければ生成
        if self.cached_base is None:
            self._build_cache()

        # ------------------------------------------------------------
        # ★ 押し込み強化：ぷにっと膨らむ scale
        # ------------------------------------------------------------
        if holding:
            scale = 1.0 + (0.12 * math.sin(self.timer * 20))
        else:
            scale = 1.0

        scaled_size = int(self.radius * 2 * scale)
        surf = pygame.transform.smoothscale(self.cached_base, (scaled_size, scaled_size))
        surf.set_alpha(max(0, min(255, int(self.alpha))))

        # ------------------------------------------------------------
        # ★ 押し込み強化：光量アップ（pulse）
        # ------------------------------------------------------------
        pulse = (math.sin(self.timer) + 1) * 0.5 if holding else 0

        if holding:
            glow = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
            alpha = int(140 * pulse)

            pygame.gfxdraw.filled_circle(
                glow,
                scaled_size // 2,
                scaled_size // 2,
                int(self.radius * scale),
                (*self.color, alpha),
            )
            pygame.gfxdraw.aacircle(
                glow,
                scaled_size // 2,
                scaled_size // 2,
                int(self.radius * scale),
                (*self.color, alpha),
            )

            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        # ------------------------------------------------------------
        # 描画
        # ------------------------------------------------------------
        screen.blit(
            surf,
            (x - scaled_size // 2, y - scaled_size // 2),
            special_flags=pygame.BLEND_ADD,
        )

    # ============================================================
    # リセット処理
    # ============================================================

    def reset(self):
        self.alpha = 255
        self.active = True
        self.timer = 0.0
