"""
run_game.py - 商用品質：画面遷移とゲーム起動のメインコントローラ
"""

import pygame
import sys

from logger import get_logger

# 画面管理（正しい場所）
from manager.screen_manager import ScreenManager

# 曲データ・解析
from songs import get_songs_as_dict
from songs.analysis.audio.audio_analyzer import analyze_songs
from songs.chart.chart_loader import load_chart

# 画面
from ui.song_select_screen import SongSelectScreen
from ui.gameplay_screen import GameplayScreen
from ui.result_screen import ResultScreen

# ロジック
from game.game_logic import GameLogic

logger = get_logger(__name__)


def run_game():
    """
    商用品質：ゲーム全体の流れを管理するメイン関数
    """

    pygame.init()

    # ------------------------------------------------------------
    # 1. 画面管理（ScreenManager）
    # ------------------------------------------------------------
    manager = ScreenManager()

    # ------------------------------------------------------------
    # 2. 曲データ読み込み（BPM解析など）
    # ------------------------------------------------------------
    songs = get_songs_as_dict()
    songs = analyze_songs(songs)

    # ------------------------------------------------------------
    # 3. 初期画面：曲選択
    # ------------------------------------------------------------
    manager.change_screen(
        SongSelectScreen(
            manager,
            songs=songs,
            difficulty="NORMAL",
            speed_level=3,
        )
    )

    # ------------------------------------------------------------
    # 4. メインループ
    # ------------------------------------------------------------
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0

        screen = manager.current_screen

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            screen.handle_event(event)

        # 更新
        screen.update(dt)

        # 画面遷移要求があれば処理
        if manager.has_transition():
            target, payload = manager.pop_transition()

            # ----------------------------------------------------
            # 曲選択 → ゲームプレイ
            # ----------------------------------------------------
            if target == "gameplay":
                song = payload["song"]

                # 譜面読み込み（Note クラス生成もここで行われる）
                load_chart(song, song.chart_mode)

                # GameLogic 生成
                logic = GameLogic(
                    notes=song.notes,
                    bpm_events=song.bpm_events,
                    song_bpm=song.bpm,
                )

                manager.change_screen(GameplayScreen(manager, song, logic, speed=song.speed))

            # ----------------------------------------------------
            # ゲームプレイ → リザルト
            # ----------------------------------------------------
            elif target == "result":
                manager.change_screen(ResultScreen(manager, **payload))

            # ----------------------------------------------------
            # タイトルへ戻る
            # ----------------------------------------------------
            elif target == "title":
                manager.change_screen(
                    SongSelectScreen(
                        manager,
                        songs=songs,
                        difficulty="NORMAL",
                        speed_level=3,
                    )
                )

        # 描画
        manager.current_screen.draw(manager.surface)
        pygame.display.flip()
