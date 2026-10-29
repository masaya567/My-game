#!/usr/bin/env python3
"""
Piano Tiles - 起動専用メインプログラム（商用品質版・完全版）
"""

import sys
import os
import pygame

# PyInstaller 対応：BASE_DIR を統一
def get_base_dir():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.abspath(os.path.dirname(__file__))

BASE_DIR = get_base_dir()

# プロジェクトルートをパスに追加
sys.path.insert(0, BASE_DIR)
sys.dont_write_bytecode = True

from game.logger import GameLogger
from manager.screen_manager import create_manager
from constants import WIDTH, HEIGHT


def main():
    print("=" * 50)
    print("Piano Tiles - ゲーム起動")
    print("=" * 50)
    print("← → キーで曲を選択")
    print("SPACE キーでゲーム開始")
    print("ESC キーで終了")
    print("=" * 50)

    logger = GameLogger()
    logger.info("ゲーム起動開始")

    # pygame 初期化（例外対策）
    try:
        pygame.init()
        pygame.mixer.init()
    except Exception as e:
        logger.error(f"pygame 初期化失敗: {e}")
        sys.exit(1)

    # ★ 画面生成（必須）
    pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Piano Tiles - Classic Edition")

    # ★ ScreenManager 生成
    manager = create_manager()

    # ★ 起動高速化：全リソースプリロード（完全版）
    try:
        manager.resources.preload_all()
        logger.info("全リソースプリロード完了")
    except Exception as e:
        logger.error(f"プリロード失敗: {e}")

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("ゲーム終了（QUIT）")
                pygame.quit()
                sys.exit()

            manager.handle_event(event)

        # ★ 画面の更新（内部で song_time を増やす必要あり）
        manager.update(dt)

        screen = pygame.display.get_surface()
        manager.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"致命的なエラー: {e}")
        pygame.quit()
        sys.exit(1)
