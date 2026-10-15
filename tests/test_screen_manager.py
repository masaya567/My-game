import unittest
import pygame
from types import SimpleNamespace

from manager.screen_manager import create_manager
from songs.loader.song_loader import load_all_songs
from ui.gameplay.draw import draw_gameplay
from ui.gameplay.event import handle_gameplay_event


class ScreenManagerTransitionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_mode((400, 600))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_chart_preview_to_gameplay_transition(self):
        manager = create_manager()
        songs = load_all_songs()
        song = songs[0]

        manager.set(("chart_preview", song))
        self.assertEqual(type(manager.current).__name__, "ChartPreviewScreen")

        manager.current.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

        self.assertEqual(type(manager.current).__name__, "GameplayScreen")

    def test_gameplay_keydown_judges_immediately(self):
        calls = []

        class DummyLogic:
            def try_judge(self, lane, song_time):
                calls.append(("judge", lane, song_time))
                return "perfect"

            def release_judge(self, lane, song_time):
                calls.append(("release", lane, song_time))
                return "none"

        screen_obj = SimpleNamespace(
            manager=SimpleNamespace(
                settings={
                    "key_config": {
                        "Lane 1": pygame.K_d,
                        "Lane 2": pygame.K_f,
                        "Lane 3": pygame.K_j,
                        "Lane 4": pygame.K_k,
                    }
                }
            ),
            start_time=0.0,
            get_song_time=lambda: 0.5,
            song_time=0.0,
            key_pressed=[False, False, False, False],
            logic=DummyLogic(),
            lane_keys=[
                [pygame.K_d, pygame.K_LEFT],
                [pygame.K_f, pygame.K_DOWN],
                [pygame.K_j, pygame.K_UP],
                [pygame.K_k, pygame.K_RIGHT],
            ],
            spawn_hit_effect=lambda lane, result: calls.append(("effect", lane, result)),
            request_transition=lambda target: None,
            play_se=lambda name: None,
        )

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
        handle_gameplay_event(screen_obj, event)

        self.assertEqual(screen_obj.song_time, 0.5)
        self.assertTrue(screen_obj.key_pressed[0])
        self.assertEqual(calls, [("judge", 0, 0.5), ("effect", 0, "perfect")])

    def test_draw_gameplay_handles_missing_state(self):
        class DummyFont:
            def render(self, text, antialias, color):
                return pygame.Surface((100, 20))

        class DummyRes:
            def get_font(self, size, weight=None):
                return DummyFont()

        class DummyEffectManager:
            def draw(self, screen):
                return None

        class DummyJudgeTextAnim:
            def draw(self, screen):
                return None

        note = SimpleNamespace(
            is_long=False,
            lane=0,
            head_y=100,
            alpha=255,
            renderer=SimpleNamespace(draw_short=lambda screen, lane_x, y, alpha: None),
        )

        screen_obj = SimpleNamespace(
            song=SimpleNamespace(),
            song_time=0.0,
            logic=SimpleNamespace(notes=[note], score=0, combo=0, last_judged_lane=None),
            bg_pulse_strength=0,
            bg_pulse=0.0,
            fever_strength=0,
            fever_phase=0.0,
            combo_flash=0.0,
            combo_flash_phase=0.0,
            line_wave=0.0,
            line_wave_strength=0.0,
            line_flash=0.0,
            line_flash_lane=None,
            effect_manager=DummyEffectManager(),
            judge_text_anim=DummyJudgeTextAnim(),
            res=DummyRes(),
            draw_fade=lambda screen: None,
        )

        draw_gameplay(screen_obj, pygame.Surface((400, 600)))

    def test_auto_miss_after_note_passes(self):
        from game.game_logic import GameLogic
        from graphics.note import Note

        note = Note(0, time=0.0)
        logic = GameLogic([note], bpm_events=[], song_bpm=120)

        logic.update_notes(0.016, 0.0, 1.0)
        self.assertFalse(note.finished)

        miss_time = logic._get_judge_windows(note.time)[3]
        logic.update_notes(0.016, miss_time + 0.01, 1.0)
        logic.auto_miss_check(miss_time + 0.01)

        self.assertTrue(note.finished)
        self.assertEqual(logic.miss, 1)

    def test_fallback_chart_generates_long_notes(self):
        from types import SimpleNamespace
        from chart.generator.auto_chart_generator import _generate_fallback_chart

        song = SimpleNamespace(length=12.0, bpm=120)
        notes = _generate_fallback_chart(song, difficulty="normal")

        self.assertTrue(any(n.get("type") == "long" for n in notes))

    def test_long_note_tail_position_is_below_head(self):
        from graphics.note import Note

        note = Note(0, time=0.0, duration=1.5)
        note.update(0.016, song_time=0.0, bpm_events=[], base_speed=1.0, song_bpm=120)

        self.assertGreater(note.tail_y, note.head_y)

    def test_try_judge_skips_already_head_judged_long_note(self):
        from game.game_logic import GameLogic
        from graphics.note import Note

        note = Note(0, time=1.0, duration=1.0)
        note.head_judged = True
        note.holding = True

        logic = GameLogic([note], bpm_events=[], song_bpm=120)
        result = logic.try_judge(0, 1.0)

        self.assertEqual(result, "none")

    def test_long_note_update_uses_renderer_pulse_api(self):
        from graphics.note import Note

        note = Note(0, time=1.0, duration=1.0)
        note.song_time = 1.0
        note.bpm_events = []
        note.base_speed = 1.0
        note.song_bpm = 120
        note.holding = True

        note.update(0.016)

        self.assertGreater(note.tail_y, note.head_y)
        self.assertGreaterEqual(note.renderer.pulse_timer, 0.0)


if __name__ == "__main__":
    unittest.main()
