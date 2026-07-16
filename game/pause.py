"""
商用品質：ポーズ管理モジュール（完全版）

・ポーズ状態の切り替え
・BGM 一時停止／再開
・UIオーバーレイ表示
・ログ記録
"""

import pygame
from game.logger import GameLogger


class PauseManager:
    """
    商用品質：ポーズ管理クラス
    """

    def __init__(self):
        self.paused = False
        self.logger = GameLogger()

    # ============================================================
    # ポーズ切り替え
    # ============================================================

    def toggle_pause(self):
        """ポーズ状態を切り替える"""
        self.paused = not self.paused
        state = "Paused" if self.paused else "Resumed"
        self.logger.info(f"Game {state}")

        # BGM の一時停止／再開
        try:
            if self.paused:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
        except Exception:
            # BGM 未使用でも落ちないようにする
            self.logger.debug("No music to pause/unpause")

    # ============================================================
    # ポーズ状態判定
    # ============================================================

    def is_paused(self) -> bool:
        """現在ポーズ中か判定"""
        return self.paused

    # ============================================================
    # ポーズ画面描画
    # ============================================================

    def draw_pause_overlay(self, screen, font):
        """ポーズ中のオーバーレイを描画"""
        if not self.paused:
            return

        width, height = screen.get_width(), screen.get_height()

        # 半透明グラデーションオーバーレイ
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(height):
            alpha = int(120 + (y / height) * 80)  # 上から下に少し濃くなる
            pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (width, y))

        # 中央に「PAUSED」表示
        text = font.render("PAUSED", True, (255, 255, 255))
        rect = text.get_rect(center=(width // 2, height // 2))
        overlay.blit(text, rect)

        screen.blit(overlay, (0, 0))
