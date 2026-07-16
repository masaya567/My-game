"""
商用品質：グラフィック共通処理モジュール（完全版・最終形態）

描画モジュール間で共通して使用する関数群。
"""

import pygame
import math

# ============================================================
# 色補間（Color Lerp）
# ============================================================


def lerp_color(color_a, color_b, t: float) -> tuple[int, int, int]:
    """2色間を補間して中間色を返す"""
    t = max(0.0, min(1.0, t))
    return (
        int(color_a[0] + (color_b[0] - color_a[0]) * t),
        int(color_a[1] + (color_b[1] - color_a[1]) * t),
        int(color_a[2] + (color_b[2] - color_a[2]) * t),
    )


# ============================================================
# アルファフェード
# ============================================================


def fade_alpha(surface: pygame.Surface, alpha: int) -> pygame.Surface:
    """指定アルファ値でフェードしたサーフェスを返す"""
    faded = surface.copy()
    faded.set_alpha(alpha)
    return faded


# ============================================================
# グラデーション生成
# ============================================================


def create_vertical_gradient(width: int, height: int, color_top, color_bottom) -> pygame.Surface:
    """縦方向のグラデーションサーフェスを生成"""
    gradient = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        t = y / height
        color = lerp_color(color_top, color_bottom, t)
        pygame.draw.line(gradient, color, (0, y), (width, y))
    return gradient


# ============================================================
# 発光エフェクト生成（高速化版）
# ============================================================


def create_glow(radius: int, color=(120, 200, 255), intensity: int = 120) -> pygame.Surface:
    """円形の発光エフェクトを生成（高速化版）"""
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    layers = 12
    for i in range(layers):
        ratio = 1 - (i / layers)
        alpha = int(intensity * ratio)
        pygame.draw.circle(
            glow,
            (*color, alpha),
            (radius, radius),
            int(radius * ratio),
        )
    return glow


# ============================================================
# 加算合成（BLEND_ADD）補助
# ============================================================


def blit_add(base: pygame.Surface, overlay: pygame.Surface, pos: tuple[int, int]):
    """加算合成で描画する"""
    base.blit(overlay, pos, special_flags=pygame.BLEND_ADD)


# ============================================================
# 波動関数（sin波）
# ============================================================


def wave(t: float, speed: float = 1.0, amplitude: float = 1.0) -> float:
    """sin波を返す（発光や動きの周期に使用）"""
    return math.sin(t * speed) * amplitude


# ============================================================
# イージング波動（商用品質）
# ============================================================


def ease_wave(t: float, speed: float = 1.0, amplitude: float = 1.0) -> float:
    """ease-in-out の波動（商用ゲームでよく使う）"""
    return (math.sin(t * speed) * 0.5 + 0.5) * amplitude
