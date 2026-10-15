"""
商用仕様：画面基盤クラス（BaseScreen）

全てのUI画面が継承する共通クラス。
"""

import pygame
from resource_manager.resource_manager import ResourceManager


class BaseScreen:
    """
    商用仕様：全画面共通の基盤クラス
    """

    def __init__(self, manager):
        self.manager = manager
        self.active = True
        self.fade_alpha = 0

        self.res = getattr(manager, "resources", None)
        if self.res is None:
            self.res = getattr(manager, "res", None)
        if self.res is None:
            self.res = ResourceManager()

    # ============================================================
    # 更新処理（各画面でオーバーライド）
    # ============================================================

    def update(self, dt):
        """毎フレーム更新処理"""
        pass

    # ============================================================
    # 描画処理（各画面でオーバーライド）
    # ============================================================

    def draw(self, screen, fonts=None):
        """画面描画処理"""
        pass

    # ============================================================
    # 入力処理（各画面でオーバーライド）
    # ============================================================

    def handle_event(self, event):
        """入力イベント処理"""
        pass

    def on_enter(self):
        self.active = True

    def on_exit(self):
        self.active = False

    def center_text(
        self,
        screen,
        text,
        size=24,
        y=0,
        color=(255, 255, 255),
        weight="regular",
        x=None,
        max_width=None,
    ):
        font = self.res.get_font(size, weight=weight)
        if max_width is not None:
            text_to_render = self.fit_text(text, max_width, size=size, weight=weight)
            surf = font.render(text_to_render, True, color)
        else:
            surf = font.render(text, True, color)
        if x is None:
            x = screen.get_width() // 2 - surf.get_width() // 2
        screen.blit(surf, (x, y))
        return surf

    def fit_text(self, text, max_width, size=24, weight="regular"):
        if text is None:
            return ""
        font = self.res.get_font(size, weight=weight)
        if font.size(text)[0] <= max_width:
            return text

        ellipsis = "…"
        clipped = text
        while clipped and font.size(clipped + ellipsis)[0] > max_width:
            clipped = clipped[:-1]
        return clipped + ellipsis

    def draw_fade(self, screen, color=(0, 0, 0)):
        if self.fade_alpha <= 0:
            return
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((color[0], color[1], color[2], int(self.fade_alpha)))
        screen.blit(overlay, (0, 0))

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

    def play_se(self, sound_name):
        try:
            sound = self.res.get_sound(sound_name)
            if sound:
                sound.play()
        except Exception:
            pass

    def request_transition(self, target):
        if self.manager is None:
            return
        if hasattr(self.manager, "request_transition"):
            self.manager.request_transition(target)
        elif hasattr(self.manager, "set"):
            self.manager.set(target)

    def deactivate(self):
        """画面を非アクティブ化"""
        self.active = False
