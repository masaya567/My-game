"""
商用仕様：入力処理モジュール（完全版）

キーボード・マウス・タッチ入力を統一的に管理する。
"""

import pygame


class InputHandler:
    """
    商用仕様：入力処理クラス
    """

    def __init__(self):
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = (False, False, False)
        self.quit_requested = False

    # ============================================================
    # イベント処理
    # ============================================================

    def process_events(self):
        """pygameイベントを処理して入力状態を更新"""
        self.keys_pressed.clear()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True

            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons = pygame.mouse.get_pressed()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons = pygame.mouse.get_pressed()

    # ============================================================
    # キー入力判定
    # ============================================================

    def is_key_pressed(self, key):
        """指定キーが押されているか判定"""
        return key in self.keys_pressed

    def is_any_key_pressed(self, keys):
        """複数キーのいずれかが押されているか判定"""
        return any(k in self.keys_pressed for k in keys)

    # ============================================================
    # マウス入力判定
    # ============================================================

    def get_mouse_position(self):
        """マウス座標を取得"""
        return self.mouse_pos

    def is_mouse_button_pressed(self, button_index):
        """指定マウスボタンが押されているか判定"""
        if 0 <= button_index < len(self.mouse_buttons):
            return self.mouse_buttons[button_index]
        return False

    # ============================================================
    # 終了判定
    # ============================================================

    def should_quit(self):
        """終了要求があるか判定"""
        return self.quit_requested
