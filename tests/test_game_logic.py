import unittest
from types import SimpleNamespace

from game.game_logic import GameLogic


def make_note(lane=0, time=1.0, is_long=False, duration=1.0):
    note = SimpleNamespace(
        lane=lane,
        time=time,
        is_long=is_long,
        duration=duration,
        finished=False,
        head_judged=False,
        holding=False,
        fade_out=False,
    )
    note.start_fade_out = lambda: setattr(note, "fade_out", True)
    return note


class DynamicJudgmentTest(unittest.TestCase):
    def test_bpm_events_do_not_desynchronize_note_judgment_windows(self):
        logic = GameLogic(
            [make_note(time=1.0), make_note(lane=1, time=2.0)],
            bpm_events=[{"time": 2.0, "bpm": 240}],
            song_bpm=120,
        )

        first_result = logic.try_judge(0, 1.04)
        second_result = logic.try_judge(1, 2.04)

        self.assertEqual(first_result, "perfect")
        self.assertEqual(second_result, "perfect")

    def test_judgment_window_tracks_difficulty(self):
        easy = GameLogic([make_note()], [], 120, difficulty="easy")
        expert = GameLogic([make_note()], [], 120, difficulty="expert")

        self.assertEqual(easy.try_judge(0, 1.05), "perfect")
        self.assertEqual(expert.try_judge(0, 1.05), "great")

    def test_judgment_window_tracks_note_speed(self):
        normal_speed = GameLogic([make_note()], [], 120)
        faster_speed = GameLogic([make_note()], [], 120, base_speed=2.0)

        self.assertEqual(normal_speed.try_judge(0, 1.04), "perfect")
        self.assertEqual(faster_speed.try_judge(0, 1.04), "great")

    def test_judge_windows_use_shared_note_fall_speed(self):
        from constants import JUDGE_LINE, NOTE_FALL_TIME, NOTE_START_Y, calc_judge_times

        base_speed = 1.25
        logic = GameLogic([], [], 120, base_speed=base_speed)
        expected_speed = (JUDGE_LINE - NOTE_START_Y) / NOTE_FALL_TIME * base_speed

        self.assertEqual(logic._get_judge_windows(2.0), calc_judge_times(expected_speed))

    def test_repeated_same_lane_taps_judge_each_short_note_once(self):
        first = make_note(lane=0, time=1.0)
        second = make_note(lane=0, time=1.1)
        logic = GameLogic([first, second], [], 120)

        first_result = logic.try_judge(0, 1.0)
        second_result = logic.try_judge(0, 1.1)

        self.assertEqual((first_result, second_result), ("perfect", "perfect"))
        self.assertTrue(first.head_judged)
        self.assertTrue(second.head_judged)
        self.assertEqual(logic.perfect, 2)
        self.assertEqual(logic.combo, 2)

    def test_short_note_search_does_not_start_at_current_index(self):
        notes = [
            make_note(lane=0, time=1.0),
            make_note(lane=1, time=1.1),
            make_note(lane=2, time=1.2),
        ]
        logic = GameLogic(notes, [], 120)
        logic.current_index = len(notes)

        results = [logic.try_judge(note.lane, note.time) for note in notes]

        self.assertEqual(results, ["perfect", "perfect", "perfect"])
        self.assertEqual(logic.perfect, 3)

    def test_long_note_head_hold_and_tail_judgment_are_preserved(self):
        note = make_note(lane=0, time=1.0, is_long=True, duration=1.0)
        logic = GameLogic([note], [], 120)

        head_result = logic.try_judge(0, 1.0)
        mid_hold_result = logic.try_judge(0, 1.5)
        tail_result = logic.release_judge(0, 2.0)

        self.assertEqual(head_result, "perfect")
        self.assertEqual(mid_hold_result, "none")
        self.assertEqual(tail_result, "perfect")
        self.assertTrue(note.head_judged)
        self.assertTrue(note.tail_judged)
        self.assertFalse(note.holding)
        self.assertEqual(logic.perfect, 2)

    def test_long_note_does_not_start_holding_after_failed_head(self):
        note = make_note(lane=0, time=1.0, is_long=True, duration=1.0)
        logic = GameLogic([note], [], 120)
        good_window = logic._get_judge_windows(note.time)[2]

        result = logic.try_judge(0, note.time + good_window * 1.2)

        self.assertEqual(result, "none")
        self.assertFalse(note.holding)
        self.assertFalse(note.head_judged)
        self.assertEqual(logic.miss, 0)

    def test_auto_miss_window_tracks_note_speed(self):
        slow_note = make_note(time=0.0)
        slow_logic = GameLogic([slow_note], [], song_bpm=120)
        fast_note = make_note(time=0.0)
        fast_logic = GameLogic([fast_note], [], song_bpm=120, base_speed=2.0)

        slow_logic.auto_miss_check(0.2)
        fast_logic.auto_miss_check(0.2)

        self.assertFalse(slow_note.finished)
        self.assertTrue(fast_note.finished)

    def test_auto_miss_uses_configured_window_without_extra_delay(self):
        note = make_note(time=0.0)
        logic = GameLogic([note], [], 120)
        miss_window = logic._get_judge_windows(note.time)[3]

        logic.auto_miss_check(miss_window - 0.001)
        self.assertFalse(note.finished)

        logic.auto_miss_check(miss_window)
        self.assertTrue(note.finished)

    def test_update_accepts_gameplay_arguments_and_syncs_note_speed(self):
        note = make_note(time=5.0)
        note.update = lambda dt, **kwargs: None
        logic = GameLogic([note], [], 120)

        logic.update(1 / 60, 0.5, 1.25, [], 120)

        self.assertEqual(note.song_time, 0.5)
        self.assertEqual(note.base_speed, 1.25)
        self.assertEqual(note.song_bpm, 120)


if __name__ == "__main__":
    unittest.main()
