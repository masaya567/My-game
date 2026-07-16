"""
商用仕様：画面基盤クラス（BaseScreen）

全てのUI画面が継承する共通クラス。
"""

import pygame


class BaseScreen:
    """
    商用仕様：全画面共通の基盤クラス
    """

    def __init__(self, manager):
        self.manager = manager  # ScreenManager への参照
        self.active = True  # 画面がアクティブかどうか

    # ============================================================
    # 更新処理（各画面でオーバーライド）
    # ============================================================

    def update(self, dt):
        """毎フレーム更新処理"""
        pass

    # ============================================================
    # 描画処理（各画面でオーバーライド）
    # ============================================================

    def draw(self, screen, fonts):
        """画面描画処理"""
        pass

    # ============================================================
    # 入力処理（各画面でオーバーライド）
    # ============================================================

    def handle_event(self, event):
        """入力イベント処理"""
        pass

    # ============================================================
    # 共通ユーティリティ
    # ============================================================

    def fade_in(self, screen, color=(0, 0, 0), duration=500):
        """フェードイン演出"""
        overlay = pygame.Surface(screen.get_size())
        overlay.fill(color)
        for alpha in range(255, -1, -10):
            overlay.set_alpha(alpha)
            screen.blit(overlay, (0, 0))
            pygame.display.flip()
            pygame.time.delay(duration // 25)

    def fade_out(self, screen, color=(0, 0, 0), duration=500):
        """フェードアウト演出"""
        overlay = pygame.Surface(screen.get_size())
        overlay.fill(color)
        for alpha in range(0, 256, 10):
            overlay.set_alpha(alpha)
            screen.blit(overlay, (0, 0))
            pygame.display.flip()
            pygame.time.delay(duration // 25)

    def play_sound(self, sound):
        """効果音再生（pygame.mixer.Sound対応）"""
        if sound:
            sound.play()

    def deactivate(self):
        """画面を非アクティブ化"""
        self.active = False
