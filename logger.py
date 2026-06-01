"""
ロギング設定モジュール

このモジュールは、ゲーム全体のロギングを統一管理します。
コンソールとファイルの両方にログを出力できます。

使用例:
    from logger import get_logger
    logger = get_logger(__name__)
    logger.info("ゲーム開始")
    logger.error("エラーが発生しました")
"""

import logging
import logging.handlers
import os
from datetime import datetime

# ログディレクトリを作成
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得する（シングルトンパターン）

    Args:
        name: ロガー名（通常は __name__ を使用）

    Returns:
        logging.Logger: 設定済みのロガー

    例:
        logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)

    # 既にハンドラーが追加されていれば、スキップ
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ログファイルパス
    log_file = os.path.join(LOG_DIR, f"piano_tiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    # ファイルハンドラー（DEBUG レベル以上）
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # コンソールハンドラー（INFO レベル以上）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # フォーマッター
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_formatter = logging.Formatter("[%(levelname)s] %(message)s")

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# グローバルロガー
_logger = get_logger("PianoTiles")


# 便利な関数
def debug(msg: str) -> None:
    """DEBUG レベルでログ出力"""
    _logger.debug(msg)


def info(msg: str) -> None:
    """INFO レベルでログ出力"""
    _logger.info(msg)


def warning(msg: str) -> None:
    """WARNING レベルでログ出力"""
    _logger.warning(msg)


def error(msg: str) -> None:
    """ERROR レベルでログ出力"""
    _logger.error(msg)


def critical(msg: str) -> None:
    """CRITICAL レベルでログ出力"""
    _logger.critical(msg)
