"""
グラフィックス・画像処理モジュール

ゲーム内で使う画像生成やレンダリング処理を担当します。
"""

import random

import pygame

from constants import JACKET_SIZE


def make_jacket(color: tuple = None) -> pygame.Surface:
    """ジャケット画像を生成

    Args:
        color: RGB色 (デフォルト: ランダム)

    Returns:
        ジャケット画像（Surface）
    """
    if color is None:
        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
        )

    surf = pygame.Surface((JACKET_SIZE, JACKET_SIZE), pygame.SRCALPHA)
    surf.fill(color)
    return surf
