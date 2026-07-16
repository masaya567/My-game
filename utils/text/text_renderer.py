"""
商用仕様：テキスト描画モジュール（完全版・プロジェクト統合）

影付き文字・中央揃え・フェード演出・自動折り返しを統合。
"""

import pygame
from typing import Tuple, List
from utils.common.utils import wrap_text
from utils.theme.theme import get_color

# ============================================================
# 基本描画
# ============================================================


def draw_text(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    pos: Tuple[int, int],
    center: bool = False,
) -> None:
    """テキスト描画（中央揃え対応）"""
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    screen.blit(surf, rect)


# ============================================================
# 影付き描画
# ============================================================


def draw_shadow_text(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    shadow_color: Tuple[int, int, int],
    pos: Tuple[int, int],
    offset: Tuple[int, int] = (2, 2),
    center: bool = False,
) -> None:
    """影付きテキスト描画（商用品質）"""

    # 影
    shadow_surf = font.render(text, True, shadow_color)
    shadow_rect = shadow_surf.get_rect()
    if center:
        shadow_rect.center = (pos[0] + offset[0], pos[1] + offset[1])
    else:
        shadow_rect.topleft = (pos[0] + offset[0], pos[1] + offset[1])
    screen.blit(shadow_surf, shadow_rect)

    # 本体
    main_surf = font.render(text, True, color)
    main_rect = main_surf.get_rect()
    if center:
        main_rect.center = pos
    else:
        main_rect.topleft = pos
    screen.blit(main_surf, main_rect)


# ============================================================
# フェード演出付き描画
# ============================================================


def draw_fade_text(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    pos: Tuple[int, int],
    alpha: int,
    center: bool = False,
) -> None:
    """フェード演出付きテキスト描画（商用品質）"""
    surf = font.render(text, True, color)
    surf.set_alpha(alpha)

    rect = surf.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    screen.blit(surf, rect)


# ============================================================
# 折り返し描画
# ============================================================


def draw_wrapped_text(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    pos: Tuple[int, int],
    max_width: int,
    line_spacing: int = 5,
    center: bool = False,
) -> None:
    """自動折り返しテキスト描画（日本語対応・中央揃え対応）"""

    lines: List[str] = wrap_text(text, font, max_width)
    x, y = pos

    for line in lines:
        surf = font.render(line, True, color)
        rect = surf.get_rect()

        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)

        screen.blit(surf, rect)
        y += surf.get_height() + line_spacing


# ============================================================
# テーマカラー対応の簡易描画
# ============================================================


def draw_theme_text(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    pos: Tuple[int, int],
    key: str = "text_primary",
    center: bool = False,
):
    """テーマカラーを使ったテキスト描画"""
    color = get_color(key)
    draw_text(screen, text, font, color, pos, center)
