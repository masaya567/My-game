#!/usr/bin/env python3
"""
Piano Tiles - 起動専用メインプログラム（商用品質版）
"""

import sys
import os
import pygame

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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

    pygame.init()
    pygame.mixer.init()

    # ★ 画面生成（必須）
    pygame.display.set_mode((WIDTH, HEIGHT))

    # ★ ScreenManager 生成
    manager = create_manager()

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
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"致命的なエラー: {e}")
        pygame.quit()
        sys.exit(1)
