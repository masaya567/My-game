"""
商用仕様：ログ管理モジュール（完全版）

ゲーム全体の動作・エラー・イベントを記録する。
"""

import logging
import os
from datetime import datetime


class GameLogger:
    """
    商用仕様：ゲーム用ロガークラス
    """

    def __init__(self, log_dir="logs", log_file="game.log"):
        # ログディレクトリ作成
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, log_file)

        # ロガー設定
        self.logger = logging.getLogger("GameLogger")
        self.logger.setLevel(logging.DEBUG)

        # フォーマット設定
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )

        # ファイル出力
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        # コンソール出力
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # ハンドラ登録
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info("=== Game Logger Initialized ===")

    # ============================================================
    # ログ出力メソッド
    # ============================================================

    def info(self, message):
        """情報ログ"""
        self.logger.info(message)

    def warning(self, message):
        """警告ログ"""
        self.logger.warning(message)

    def error(self, message):
        """エラーログ"""
        self.logger.error(message)

    def debug(self, message):
        """デバッグログ"""
        self.logger.debug(message)

    # ============================================================
    # 特殊ログ
    # ============================================================

    def log_event(self, event_name, details=None):
        """ゲームイベントを記録"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[EVENT] {event_name} @ {timestamp}"
        if details:
            msg += f" | Details: {details}"
        self.logger.info(msg)

    def log_exception(self, e):
        """例外を記録"""
        self.logger.exception(f"Exception occurred: {e}")

    # ============================================================
    # 終了処理
    # ============================================================

    def close(self):
        """ロガー終了処理"""
        self.logger.info("=== Game Logger Closed ===")
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
