"""
商用品質：ゲーム状態管理モジュール（完全版・最終形態）

タイトル・プレイ・ポーズ・リザルトなどの状態を統一的に管理する。
"""

from enum import Enum, auto
from game.logger import GameLogger


class GameState(Enum):
    TITLE = auto()
    PLAYING = auto()
    PAUSED = auto()
    RESULT = auto()
    EXIT = auto()


class StateManager:
    """
    商用品質：ゲーム状態管理クラス
    """

    def __init__(self):
        self.current_state = GameState.TITLE
        self.previous_state = None
        self.transition_requested = False
        self.logger = GameLogger()

    # ============================================================
    # 状態遷移
    # ============================================================

    def change_state(self, new_state):
        """状態を変更（安全な遷移チェック付き）"""
        if not isinstance(new_state, GameState):
            raise ValueError("Invalid game state type.")

        # 禁止遷移チェック
        if self.current_state == GameState.EXIT:
            self.logger.warning("Cannot transition from EXIT state.")
            return False

        self.previous_state = self.current_state
        self.current_state = new_state
        self.transition_requested = True

        self.logger.info(
            f"[StateManager] Transition: {self.previous_state.name} → {self.current_state.name}"
        )
        return True

    # ============================================================
    # 状態確認
    # ============================================================

    def is_state(self, state):
        return self.current_state == state

    def get_state(self):
        return self.current_state

    def get_previous_state(self):
        return self.previous_state

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self):
        """状態遷移フラグをリセット"""
        if self.transition_requested:
            self.transition_requested = False

    # ============================================================
    # 終了処理
    # ============================================================

    def request_exit(self):
        """ゲーム終了を要求"""
        self.change_state(GameState.EXIT)

    def should_exit(self):
        return self.current_state == GameState.EXIT
