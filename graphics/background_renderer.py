"""
商用品質：背景描画統合モジュール（完全版・最終形態）

背景アニメーション・発光・タイル描画を統合して管理する。
"""

import pygame
from graphics.background import BackgroundRenderer


class BackgroundManager:
    """
    商用品質：背景描画統合クラス
    """

    def __init__(self, width: int, height: int):
        self.renderer = BackgroundRenderer(width, height)
        self.width = width
        self.height = height

        # 背景テーマ（コンボ色など）
        self.combo_color = (120, 200, 255)
        self.diff_color = (255, 120, 120)

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt: float, combo: int, judge_text: str) -> None:
        """背景の状態を更新"""
        self.renderer.update(dt, combo, judge_text)

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen: pygame.Surface) -> None:
        """背景を描画"""
        self.renderer.draw(screen)

    # ============================================================
    # テーマ設定
    # ============================================================

    def set_combo_color(self, color: tuple) -> None:
        """コンボ色テーマを設定"""
        self.combo_color = color

    def set_diff_color(self, color: tuple) -> None:
        """難易度色テーマを設定"""
        self.diff_color = color

    # ============================================================
    # 情報取得
    # ============================================================

    def get_state(self) -> dict:
        """背景の状態を取得（デバッグ用）"""
        return {
            "combo_color": self.combo_color,
            "diff_color": self.diff_color,
        }

    # ============================================================
    # リセット処理
    # ============================================================

    def reset(self) -> None:
        """背景をリセット"""
        self.renderer = BackgroundRenderer(self.width, self.height)
