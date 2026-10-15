import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pygame

from ui.gameplay.event import handle_gameplay_event
from ui.gameplay.screen import GameplayScreen
from game.game_logic import GameLogic


class GameplayInputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_screen(self, logic, song_time=0.4, key_pressed=None):
        return SimpleNamespace(
            lane_keys=[[pygame.K_d], [pygame.K_f], [pygame.K_j], [pygame.K_k]],
            key_pressed=key_pressed or [False, False, False, False],
            music_start_time=10.0,
            start_time=10.0,
            song_time=song_time,
            logic=logic,
            spawn_hit_effect=Mock(),
            play_se=Mock(),
            request_transition=Mock(),
        )

    def test_gameplay_screen_has_clock_when_audio_file_is_missing(self):
        manager = SimpleNamespace(
            settings={"note_speed": 1.25},
            resources=object(),
        )
        song = SimpleNamespace(
            difficulty="hard",
            notes=[],
            bpm_events=[],
            bpm=120,
            audio_file=None,
        )

        screen = GameplayScreen(manager, song)

        self.assertGreaterEqual(screen.get_song_time(), 0.0)
        self.assertEqual(screen.difficulty, "HARD")
        self.assertEqual(screen.logic.base_speed, 1.25)

    def test_gameplay_screen_initializes_fallback_clock_and_song_difficulty(self):
        manager = SimpleNamespace(
            settings={"note_speed": 1.25},
            resources=object(),
        )
        song = SimpleNamespace(
            difficulty="expert",
            notes=[],
            bpm_events=[],
            bpm=120,
            audio_file=None,
        )

        screen = GameplayScreen(manager, song)

        self.assertEqual(screen.difficulty, "EXPERT")
        self.assertEqual(screen.logic.difficulty, "EXPERT")
        self.assertEqual(screen.logic.base_speed, 1.25)
        self.assertGreaterEqual(screen.get_song_time(), 0.0)

    def test_keydown_uses_current_song_time_not_previous_frame_time(self):
        logic = SimpleNamespace(try_judge=Mock(return_value="perfect"))
        screen = self.make_screen(logic)

        with patch("ui.gameplay.event.time.perf_counter", return_value=10.5):
            handle_gameplay_event(
                screen,
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d),
            )

        logic.try_judge.assert_called_once_with(0, 0.5)
        self.assertEqual(screen.song_time, 0.5)

    def test_keydown_uses_music_position_for_real_judgment(self):
        note = SimpleNamespace(
            lane=0,
            time=1.0,
            is_long=False,
            head_judged=False,
            finished=False,
            fade_out=False,
            start_fade_out=Mock(),
        )
        logic = GameLogic([note], [], 120)
        screen = self.make_screen(logic, song_time=0.9)
        screen.get_song_time = Mock(return_value=1.0)

        with patch("ui.gameplay.event.time.perf_counter", return_value=10.9):
            handle_gameplay_event(
                screen,
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d),
            )

        self.assertEqual(logic.perfect, 1)
        self.assertEqual(logic.good, 0)

    def test_long_note_keyup_uses_tail_judgment(self):
        logic = SimpleNamespace(
            hold_miss_check=Mock(return_value="miss"),
            release_judge=Mock(return_value="perfect"),
        )
        screen = self.make_screen(logic, key_pressed=[True, False, False, False])

        with patch("ui.gameplay.event.time.perf_counter", return_value=11.0):
            handle_gameplay_event(
                screen,
                pygame.event.Event(pygame.KEYUP, key=pygame.K_d),
            )

        logic.hold_miss_check.assert_not_called()
        logic.release_judge.assert_called_once_with(0, 1.0)
        screen.spawn_hit_effect.assert_called_once_with(0, "perfect")

    def test_judgment_result_requests_matching_sound(self):
        screen = GameplayScreen.__new__(GameplayScreen)
        screen.play_se = Mock()

        with patch("ui.gameplay.screen.spawn_hit_effect") as spawn_visual:
            for result in ("perfect", "great", "good", "miss"):
                GameplayScreen.spawn_hit_effect(screen, 0, result)

        self.assertEqual(
            [call.args[0] for call in screen.play_se.call_args_list],
            ["perfect", "great", "good", "miss"],
        )
        self.assertEqual(spawn_visual.call_count, 4)

    def test_song_clock_uses_mixer_position(self):
        screen = GameplayScreen.__new__(GameplayScreen)
        screen.music_start_time = 10.0

        with patch("ui.gameplay.screen.pygame.mixer.music.get_pos", return_value=1250):
            self.assertEqual(screen.get_song_time(), 1.25)

    def test_song_clock_falls_back_when_mixer_position_is_unavailable(self):
        screen = GameplayScreen.__new__(GameplayScreen)
        screen.music_start_time = 10.0

        with patch("ui.gameplay.screen.pygame.mixer.music.get_pos", return_value=-1):
            with patch("ui.gameplay.screen.time.perf_counter", return_value=10.75):
                self.assertEqual(screen.get_song_time(), 0.75)


if __name__ == "__main__":
    unittest.main()
