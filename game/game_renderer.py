"""
商用品質：game_renderer モジュール（完全版）

ノーツ・背景・UI・エフェクトを統合して描画する。
"""

import pygame
from game.render.effects.effect_renderer import EffectRenderer
from constants import WIDTH, HEIGHT, UI_COLORS, FPS


class GameRenderer:
    """
    商用品質：ゲーム描画統括クラス
    """

    def __init__(self, manager):
        self.manager = manager
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("MY RHYTHM GAME")
        self.clock = pygame.time.Clock()
        self.effect_renderer = EffectRenderer()
        self.background_color = UI_COLORS["bg_select"]

    # ============================================================
    # メイン描画ループ
    # ============================================================

    def render_frame(self, notes, judge_line, ui_elements, dt):
        """1フレーム分の描画処理"""
        self.screen.fill(self.background_color)

        self._draw_background()
        self._draw_notes(notes)
        self._draw_judge_line(judge_line)
        self._draw_ui(ui_elements)

        self.effect_renderer.draw(self.screen)

        pygame.display.flip()
        self.clock.tick(FPS)

    # ============================================================
    # 背景描画
    # ============================================================

    def _draw_background(self):
        """背景描画（グラデーション）"""
        gradient = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            color_value = int(20 + (y / HEIGHT) * 40)
            pygame.draw.line(
                gradient, (color_value, color_value, color_value + 10), (0, y), (WIDTH, y)
            )
        self.screen.blit(gradient, (0, 0))

    # ============================================================
    # ノーツ描画
    # ============================================================

    def _draw_notes(self, notes):
        """ノーツ描画"""
        for note in notes:
            pygame.draw.circle(self.screen, note.color, (note.x, note.y), note.radius)

    # ============================================================
    # 判定ライン描画
    # ============================================================

    def _draw_judge_line(self, judge_line):
        """判定ライン描画"""
        pygame.draw.line(
            self.screen,
            UI_COLORS["accent"],
            (0, judge_line.y),
            (WIDTH, judge_line.y),
            3,
        )

    # ============================================================
    # UI描画
    # ============================================================

    def _draw_ui(self, ui_elements):
        """スコア・コンボ・判定などのUI描画"""
        for element in ui_elements:
            surf = element.font.render(element.text, True, element.color)
            self.screen.blit(surf, element.pos)

    # ============================================================
    # エフェクト追加
    # ============================================================

    def add_effect(self, pos, color=(255, 255, 255), type="glow"):
        """エフェクトを追加"""
        if type == "glow":
            self.effect_renderer.add_glow(pos, color)
        elif type == "beam":
            self.effect_renderer.add_beam(pos, color)

    # ============================================================
    # 終了処理
    # ============================================================

    def cleanup(self):
        """描画終了処理"""
        pygame.quit()
