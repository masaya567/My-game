"""
商用仕様：画面基盤クラス（BaseScreen）
アプリケーション化に必要な高速化（font.render キャッシュ + 背景 Surface キャッシュ）対応版
"""

import pygame
from constants import WIDTH, HEIGHT
from resource_manager.resource_manager import ResourceManager


class BaseScreen:
    """
    商用品質：全画面共通の基盤クラス
    """

    def __init__(self, manager):
        self.manager = manager
        self.active = True
        self.fade_alpha = 0

        # ResourceManager
        self.res = getattr(manager, "resources", None)
        if self.res is None:
            self.res = getattr(manager, "res", None)
        if self.res is None:
            self.res = ResourceManager()

        # ★ 高速化：font.render キャッシュ
        self.text_cache = {}

        # ★ 高速化：背景 Surface キャッシュ
        self.bg_surface = None
        self.bg_color = None

    # ============================================================
    # 背景キャッシュ化（高速化）
    # ============================================================

    def set_background(self, color):
        """
        背景 Surface をキャッシュ生成（アプリ化で最重要）
        - 毎フレーム fill() を呼ばない
        - Surface を毎回生成しない
        """
        self.bg_color = color
        self.bg_surface = pygame.Surface((WIDTH, HEIGHT))
        self.bg_surface.fill(color)

    # ============================================================
    # 高速化：文字キャッシュ
    # ============================================================

    def get_text(self, text: str, size: int, color: tuple, weight=None):
        key = (text, size, color, weight)
        if key not in self.text_cache:
            font = self.res.get_font(size, weight=weight)
            self.text_cache[key] = font.render(text, True, color)
        return self.text_cache[key]

    # ============================================================
    # 更新処理（各画面でオーバーライド）
    # ============================================================

    def update(self, dt):
        pass

    # ============================================================
    # 描画処理（各画面でオーバーライド）
    # ============================================================

    def draw(self, screen, fonts=None):
        """
        各画面の draw() 冒頭で以下を呼ぶこと：
            screen.blit(self.bg_surface, (0, 0))
        """
        pass

    # ============================================================
    # 入力処理（各画面でオーバーライド）
    # ============================================================

    def handle_event(self, event):
        pass

    def on_enter(self):
        self.active = True

        # ★ 画面切り替え時にキャッシュをクリア（メモリ節約）
        self.text_cache.clear()

    def on_exit(self):
        self.active = False

    # ============================================================
    # center_text（高速化対応版）
    # ============================================================

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
        if max_width is not None:
            text = self.fit_text(text, max_width, size=size, weight=weight)

        surf = self.get_text(text, size, color, weight)

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

    # ============================================================
    # フェード
    # ============================================================

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
        overlay = pygame.Surface(screen.get_size())
        overlay.fill(color)
        for alpha in range(255, -1, -10):
            overlay.set_alpha(alpha)
            screen.blit(overlay, (0, 0))
            pygame.display.flip()
            pygame.time.delay(duration // 25)

    def fade_out(self, screen, color=(0, 0, 0), duration=500):
        overlay = pygame.Surface(screen.get_size())
        overlay.fill(color)
        for alpha in range(0, 256, 10):
            overlay.set_alpha(alpha)
            screen.blit(overlay, (0, 0))
            pygame.display.flip()
            pygame.time.delay(duration // 25)

    def play_sound(self, sound):
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
        self.active = False
