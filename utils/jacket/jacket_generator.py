"""
商用品質：ジャケット生成モジュール（完全統合版）
曲タイトル・作曲者・テーマカラー・画像を合成してジャケットを生成する。
"""

import os
import pygame
from typing import Optional, Tuple

from utils.theme.theme import get_color
from utils.common.utils import render_fit_text
from resource_manager.font_manager import FontManager

# ============================================================
# Song モデルと完全一致する関数名
# ============================================================


def make_proseka_jacket(
    title: str,
    base_color: Tuple[int, int, int],
    image_path: Optional[str] = None,
    size: Tuple[int, int] = (256, 256),
) -> Tuple[pygame.Surface, pygame.Surface]:
    """商用品質：曲ごとの色テーマ＋画像＋タイトルを合成したジャケット生成"""

    jacket = pygame.Surface(size, pygame.SRCALPHA)

    # 背景：曲ごとのテーマカラー
    jacket.fill(base_color)

    # 共通画像を合成
    if image_path and os.path.exists(image_path):
        try:
            base_img = pygame.image.load(image_path).convert_alpha()
            base_img = pygame.transform.smoothscale(base_img, size)
            jacket.blit(base_img, (0, 0))
        except Exception:
            pass

    # グラデーション
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

    # 光沢
    gloss = pygame.Surface((size[0], size[1] // 2), pygame.SRCALPHA)
    gloss.fill((255, 255, 255, 40))
    jacket.blit(gloss, (0, 0))

    # Keep Font instances local; pygame.quit() invalidates cached native fonts.
    font_title = FontManager().get(28, weight="bold")

    # タイトル描画
    title_surf = render_fit_text(title, font_title, size[0] - 40, get_color("text_primary"))
    title_rect = title_surf.get_rect(center=(size[0] // 2, int(size[1] * 0.85)))
    jacket.blit(title_surf, title_rect)

    # 枠線
    pygame.draw.rect(jacket, get_color("text_primary"), jacket.get_rect(), 4, border_radius=20)

    # 影（選曲画面用）
    shadow = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=20)

    return shadow, jacket


# ============================================================
# サムネイル生成
# ============================================================


def generate_thumbnail(
    jacket: pygame.Surface, size: Tuple[int, int] = (120, 120)
) -> pygame.Surface:
    return pygame.transform.smoothscale(jacket, size)


# ============================================================
# ジャケット読み込み（完全統合版）
# ============================================================


def load_jacket(source) -> pygame.Surface:
    """Song オブジェクトからジャケットを読み込む（完全統合版）"""

    # Song が Surface を持っている場合
    if isinstance(source, pygame.Surface):
        return source

    # Song モデル対応
    title = getattr(source, "title", "Unknown")
    composer = getattr(source, "composer", "")
    base_color = getattr(source, "base_color", (120, 120, 255))
    image_path = getattr(source, "jacket", None)

    # 外部画像がある場合
    if image_path and os.path.exists(image_path):
        try:
            img = pygame.image.load(image_path).convert_alpha()
            return pygame.transform.smoothscale(img, (256, 256))
        except Exception:
            pass

    # フォールバック：自動生成
    _, jacket = make_proseka_jacket(
        title=title,
        base_color=base_color,
        image_path=None,
        size=(256, 256),
    )
    return jacket
