"""
商用仕様：ログ管理モジュール（完全版・統合版）

ゲーム全体の動作・エラー・イベントを記録する。
日付ごとにログファイルを自動分割し、複数生成を防ぐ。
"""

import logging
import os
from datetime import datetime


class GameLogger:
    """
    商用仕様：ゲーム用ロガークラス（完全統合版）
    - 日付ごとにログファイルを自動生成
    - 多重生成を防ぐ（Singleton）
    - ファイル出力 + コンソール出力
    """

    _instance = None  # ★ 多重生成防止（Singleton）

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GameLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_dir="logs"):
        # ★ すでに初期化済みなら何もしない（多重初期化防止）
        if hasattr(self, "_initialized") and self._initialized:
            return

        # ログディレクトリ作成
        os.makedirs(log_dir, exist_ok=True)

        # ★ 日付ごとにログファイルを分割（商用品質）
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = f"game_{today}.log"
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

        # ハンドラ登録（多重登録防止）
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        self.logger.info("=== Game Logger Initialized ===")

        self._initialized = True

    # ============================================================
    # ログ出力メソッド
    # ============================================================

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
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
        """例外を記録（トレースバック付き）"""
        self.logger.exception(f"Exception occurred: {e}")

    # ============================================================
    # 終了処理
    # ============================================================

    def close(self):
        """ロガー終了処理（商用品質）"""
        self.logger.info("=== Game Logger Closed ===")
        for handler in list(self.logger.handlers):
            handler.close()
            self.logger.removeHandler(handler)


def get_logger(name=None):
    return GameLogger()

# ============================================================
# ロングノーツ専用ログ（1ファイルにまとめる）
# ============================================================

LONG_LOG_FILE = os.path.join("logs", "long_notes.log")

long_logger = logging.getLogger("LongLogger")
long_logger.setLevel(logging.INFO)

long_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
)

long_handler = logging.FileHandler(LONG_LOG_FILE, encoding="utf-8")
long_handler.setFormatter(long_formatter)
long_handler.setLevel(logging.INFO)

if not long_logger.handlers:
    long_logger.addHandler(long_handler)
