"""
商用仕様：ヒットエフェクト更新モジュール（完全版）

GlowEffect と同じ商用品質方式：
指数フェード / 揺らぎ / kick / 非線形拡散 / 多層グロー / コア光 / 加算合成
"""

import pygame
import math
from typing import List, Dict, Any

LANE_X = [200, 350, 500, 650]
HIT_Y = 780

effects: List[Dict[str, Any]] = []


# ============================================================
# エフェクト生成（商用品質）
# ============================================================


def spawn_hit_effect(lane: int, result: str):
    color_map = {
        "perfect": (255, 240, 120),
        "great": (120, 200, 255),
        "good": (120, 255, 120),
        "miss": (255, 80, 80),
    }

    power_map = {
        "perfect": 1.0,
        "great": 0.7,
        "good": 0.4,
        "miss": 0.0,
    }

    effects.append(
        {
            "lane": lane,
            "x": LANE_X[lane],
            "y": HIT_Y,
            "color": color_map.get(result, (255, 255, 255)),
            "base_radius": 40,
            "elapsed": 0.0,
            "duration": 0.25,
            "kick": power_map.get(result, 0.0),
            "active": True,
        }
    )


# ============================================================
# 更新処理（商用品質）
# ============================================================


def update_effects(dt: float):
    remove_list = []

    for e in effects:
        e["elapsed"] += dt
        if e["elapsed"] >= e["duration"]:
            e["active"] = False
            remove_list.append(e)

        # kick の指数減衰
        e["kick"] *= 0.85

    for e in remove_list:
        effects.remove(e)


# ============================================================
# 描画処理（商用品質）
# ============================================================


def draw_effects(screen: pygame.Surface):
    for e in effects:
        elapsed = e["elapsed"]
        duration = e["duration"]

        # 指数フェード
        fade = math.exp(-elapsed / duration * 3)
        alpha = int(255 * fade)

        # 揺らぎ（光の呼吸）
        wave = (math.sin(elapsed * 20) + 1) * 0.5
        wave_strength = 0.2 + wave * 0.3

        # kick による光量アップ
        alpha = int(alpha * (1.0 + e["kick"] * 0.8))

        # 非線形拡散
        radius = int(e["base_radius"] * (1 + (1 - fade) * 0.6 + e["kick"] * 0.4))

        # 描画用Surface
        glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        cx, cy = radius, radius

        # 多層グロー
        for i in range(radius, 0, -3):
            intensity = alpha * (i / radius) * wave_strength
            pygame.draw.circle(glow_surface, (*e["color"], int(intensity)), (cx, cy), i)

        # コア光
        core_alpha = int(alpha * 0.9)
        pygame.draw.circle(glow_surface, (255, 255, 255, core_alpha), (cx, cy), int(radius * 0.35))

        # 加算合成（BLEND_ADD）
        screen.blit(
            glow_surface, (e["x"] - radius, e["y"] - radius), special_flags=pygame.BLEND_ADD
        )
