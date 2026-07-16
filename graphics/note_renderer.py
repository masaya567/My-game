"""
商用品質：ノーツ描画統合モジュール（完全版・最終形態）

ショートノーツとロングノーツを統合して描画する。
"""

import pygame
from graphics.long_head import LongHead
from graphics.long_body import LongBody
from graphics.long_tail import LongTail
from graphics.long_shadow import LongShadow
from graphics.long_beam import LongBeam


class NoteRenderer:
    """
    商用品質：ノーツ描画統合クラス
    """

    def __init__(self):
        self.long_head = LongHead()
        self.long_body = LongBody()
        self.long_tail = LongTail()
        self.long_shadow = LongShadow()
        self.long_beam = LongBeam()  # ★追加：光帯

    # ============================================================
    # 更新処理（ロングノーツの波動を同期）
    # ============================================================

    def update_long(self, dt: float, holding: bool):
        """ロングノーツの各パーツを同期更新"""
        self.long_head.update(dt, holding)
        self.long_body.update(dt, holding)
        self.long_tail.update(dt, holding)
        self.long_shadow.update(dt, holding)
        self.long_beam.update(dt, holding)

    # ============================================================
    # ショートノーツ描画
    # ============================================================

    def draw_short(self, screen, x, y, color=(120, 200, 255)):
        glow = pygame.Surface((80, 80), pygame.SRCALPHA)
        for i in range(15):
            alpha = int(120 * (1 - i / 15))
            pygame.draw.ellipse(glow, (*color, alpha), (15 - i, 15 - i, 50 + i * 2, 50 + i * 2))
        screen.blit(glow, (x - 15, y - 15))

        body = pygame.Surface((50, 50), pygame.SRCALPHA)
        for i in range(50):
            c = 170 + int(60 * (i / 50))
            pygame.draw.line(body, (0, c, 255), (0, i), (50, i))
        screen.blit(body, (x, y))

        pygame.draw.ellipse(screen, (255, 255, 255), (x, y, 50, 50), 3)

    # ============================================================
    # ロングノーツ描画（完全版）
    # ============================================================

    def draw_long(self, screen, x, head_y, tail_y, holding=False, color=(120, 200, 255)):
        height = tail_y - head_y

        # --- 影 ---
        self.long_shadow.draw(screen, x, head_y, height, holding)

        # --- ボディ ---
        self.long_body.draw(screen, x, head_y, height, holding, color)

        # --- 光帯（LongBeam） ---
        self.long_beam.draw(screen, x, head_y, height, holding, color)

        # --- ヘッド ---
        self.long_head.draw(screen, x, head_y, color, holding)

        # --- テール ---
        self.long_tail.draw(screen, x, tail_y, holding)
