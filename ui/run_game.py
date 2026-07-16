import pygame
import sys

from game.logger import get_logger
from game.init_display import initialize_display
from songs import get_songs_as_dict
from songs.analysis.audio.audio_analyzer import analyze_songs
from songs.chart.chart_loader import load_chart
from game.game_logic import build_notes_from_chart

# 画面クラス
from manager.screen_manager import ScreenManager
from ui.title_screen import TitleScreen
from ui.song_select_screen import SongSelectScreen
from ui.gameplay_screen import GameplayScreen
from ui.result_screen import ResultScreen

logger = get_logger(__name__)


def run_game():
    """商用品質：画面遷移統括"""

    # 画面初期化
    screen, clock, fonts = initialize_display()

    # 曲データ読み込み
    songs = get_songs_as_dict()
    songs = analyze_songs(songs)

    # 画面管理
    manager = ScreenManager(screen, clock, fonts)

    # 最初の画面
    manager.change_screen(TitleScreen(manager))

    # メインループ
    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            manager.handle_event(event)

        manager.update(dt)
        manager.draw()
