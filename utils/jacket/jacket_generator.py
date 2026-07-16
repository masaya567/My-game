"""
商用仕様：ジャケット生成モジュール（完全統合版）

曲タイトル・作曲者・テーマカラーをもとに自動ジャケット画像を生成する。
"""

import pygame
from typing import Tuple

from utils.theme.theme import get_color
from utils.common.utils import render_fit_text
from resource_manager.font_manager import FontManager

# ============================================================
# ジャケット生成
# ============================================================


def generate_jacket(
    title: str,
    composer: str,
    size: Tuple[int, int] = (300, 300),
) -> pygame.Surface:
    """ジャケット画像を生成する（商用品質）"""

    # ベース
    jacket = pygame.Surface(size, pygame.SRCALPHA)
    jacket.fill(get_color("bg_select"))

    # グラデーション背景（縦方向）
    gradient = pygame.Surface(size, pygame.SRCALPHA)
    for y in range(size[1]):
        alpha = int(180 * (y / size[1]))
        pygame.draw.line(
            gradient,
            (*get_color("title_glow"), alpha),
            (0, y),
            (size[0], y),
        )
    jacket.blit(gradient, (0, 0))

    # 光沢（上半分）
    gloss = pygame.Surface((size[0], size[1] // 2), pygame.SRCALPHA)
    gloss.fill((255, 255, 255, 40))
    jacket.blit(gloss, (0, 0))

    # フォント
    font_title = FontManager.get(28, bold=True)
    font_composer = FontManager.get(18)

    # タイトル（長い場合は自動縮小）
    title_surf = render_fit_text(title, font_title, size[0] - 40, get_color("text_primary"))
    title_rect = title_surf.get_rect(center=(size[0] // 2, int(size[1] * 0.55)))
    jacket.blit(title_surf, title_rect)

    # 作曲者
    composer_surf = font_composer.render(f"by {composer}", True, get_color("text_secondary"))
    composer_rect = composer_surf.get_rect(center=(size[0] // 2, int(size[1] * 0.75)))
    jacket.blit(composer_surf, composer_rect)

    # 枠線
    pygame.draw.rect(jacket, get_color("text_primary"), jacket.get_rect(), 4, border_radius=20)

    return jacket


# ============================================================
# サムネイル生成
# ============================================================


def generate_thumbnail(
    jacket: pygame.Surface, size: Tuple[int, int] = (120, 120)
) -> pygame.Surface:
    """ジャケット画像からサムネイルを生成"""
    return pygame.transform.smoothscale(jacket, size)
