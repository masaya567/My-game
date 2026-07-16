"""
商用品質：画面初期化モジュール（完全版）

・pygame 初期化の例外処理
・フォント読み込みの例外処理
・ログ強化（成功・警告・失敗）
・戻り値で screen / clock / fonts を返す
・グローバル変数を排除して安全化
"""

import pygame
from utils.common.utils import get_system_font
from logger import get_logger
from constants import WIDTH, HEIGHT

logger = get_logger(__name__)


def initialize_display():
    """
    商用品質：画面初期化処理
    screen, clock, fonts を返す
    """

    # ------------------------------------------------------------
    # pygame 初期化
    # ------------------------------------------------------------
    try:
        pygame.init()
        pygame.mixer.init()
        logger.info("pygame initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize pygame: {e}")
        raise RuntimeError("pygame initialization failed") from e

    # ------------------------------------------------------------
    # 画面作成
    # ------------------------------------------------------------
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Piano Tiles")
        clock = pygame.time.Clock()
        logger.info("Display surface created")

    except Exception as e:
        logger.error(f"Failed to create display surface: {e}")
        raise RuntimeError("Display creation failed") from e

    # ------------------------------------------------------------
    # フォント読み込み
    # ------------------------------------------------------------
    font_path = get_system_font()
    fonts = {}

    try:
        if font_path:
            fonts["default"] = pygame.font.Font(font_path, 48)
            fonts["small"] = pygame.font.Font(font_path, 32)
            fonts["medium"] = pygame.font.Font(font_path, 40)
            fonts["large"] = pygame.font.Font(font_path, 64)
            logger.info(f"Loaded system font: {font_path}")
        else:
            logger.warning("System font not found. Falling back to Arial.")
            fonts["default"] = pygame.font.SysFont("arial", 48)
            fonts["small"] = pygame.font.SysFont("arial", 32)
            fonts["medium"] = pygame.font.SysFont("arial", 40)
            fonts["large"] = pygame.font.SysFont("arial", 64)

    except Exception as e:
        logger.error(f"Failed to load fonts: {e}")
        raise RuntimeError("Font loading failed") from e

    logger.info("Display initialized successfully")

    # ------------------------------------------------------------
    # 商用品質：戻り値で返す
    # ------------------------------------------------------------
    return screen, clock, fonts
