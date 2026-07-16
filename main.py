#!/usr/bin/env python3
"""
Piano Tiles - 起動専用メインプログラム（商用品質版）
"""

import sys
import os
import pygame

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.logger import GameLogger
from manager.screen_manager import create_manager


def main():
    """ゲーム起動処理（起動専用）"""

    print("=" * 50)
    print("Piano Tiles - ゲーム起動")
    print("=" * 50)
    print("← → キーで曲を選択")
    print("SPACE キーでゲーム開始")
    print("ESC キーで終了")
    print("=" * 50)

    # ロガー初期化
    logger = GameLogger()
    logger.info("ゲーム起動開始")

    # pygame 初期化
    pygame.init()
    pygame.mixer.init()

    # ScreenManager 生成（画面初期化も内部で行われる）
    manager = create_manager()

    clock = pygame.time.Clock()

    # メインループ
    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("ゲーム終了（QUIT）")
                pygame.quit()
                sys.exit()

            manager.handle_event(event)

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
