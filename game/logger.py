"""
商用仕様：ログ管理モジュール（完全版・統合版）
PyInstaller 対応済み（EXE でも確実に動作）
"""

import logging
import os
import sys
from datetime import datetime


# ============================================================
# PyInstaller 対応：BASE_DIR を統一
# ============================================================
def get_base_dir():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.abspath(os.path.dirname(__file__))

BASE_DIR = get_base_dir()

# dist/logs にログを出力する
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)


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

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        # ★ 日付ごとにログファイルを分割（商用品質）
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = f"game_{today}.log"
        self.log_path = os.path.join(LOG_DIR, log_file)

        # ロガー設定
        self.logger = logging.getLogger("GameLogger")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        # ファイル出力
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        # コンソール出力
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

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
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[EVENT] {event_name} @ {timestamp}"
        if details:
            msg += f" | Details: {details}"
        self.logger.info(msg)

    def log_exception(self, e):
        self.logger.exception(f"Exception occurred: {e}")

    # ============================================================
    # 終了処理
    # ============================================================

    def close(self):
        self.logger.info("=== Game Logger Closed ===")
        for handler in list(self.logger.handlers):
            handler.close()
            self.logger.removeHandler(handler)


def get_logger(name=None):
    return GameLogger()


# ============================================================
# ロングノーツ専用ログ（PyInstaller 対応）
# ============================================================

LONG_LOG_FILE = os.path.join(LOG_DIR, "long_notes.log")

long_logger = logging.getLogger("LongLogger")
long_logger.setLevel(logging.INFO)

long_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    "%Y-%m-%d %H:%M:%S"
)

long_handler = logging.FileHandler(LONG_LOG_FILE, encoding="utf-8")
long_handler.setFormatter(long_formatter)
long_handler.setLevel(logging.INFO)

if not long_logger.handlers:
    long_logger.addHandler(long_handler)
