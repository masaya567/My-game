import os
from tempfile import TemporaryDirectory
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from chart.generator.beat_grid import BeatGrid
from chart.generator.difficulty import DIFFICULTY
from chart.generator.note_builder import NoteBuilder
from chart.generator.peak_detector import PeakDetector
from chart.generator.auto_chart_generator import AutoChartGenerator
from utils.common.utils import load_chart


class ChartGenerationTest(unittest.TestCase):
    def setUp(self):
        self.candidates = [
            {
                "time": 0.1 + index * 2.0,
                "lane": index % 4,
                "peak_type": "melody" if index % 3 == 0 else "kick",
                "strength": 1.0,
            }
            for index in range(24)
        ]
        self.grid = BeatGrid(120, [{"time": 0.0, "bpm": 120}], [0.0])

    def test_difficulty_parameters_match_requested_values(self):
        expected = {
            "easy": (0.45, 0.10, 0.10, 0.05),
            "normal": (0.58, 0.20, 0.25, 0.15),
            "hard": (0.90, 0.32, 0.45, 0.30),
            "expert": (1.20, 0.45, 0.70, 0.50),
        }

        for difficulty, values in expected.items():
            params = DIFFICULTY[difficulty]
            self.assertEqual(
                (
                    params["density"],
                    params["long_rate"],
                    params["rhythm_rate"],
                    params["variation"],
                ),
                values,
            )

    def test_beat_grid_calculates_constant_and_changing_bpm(self):
        grid = BeatGrid(
            120,
            [{"time": 0.0, "bpm": 120}, {"time": 2.0, "bpm": 60}],
            [0.0],
        )

        self.assertAlmostEqual(grid.beat_to_time(1.0), 0.5)
        self.assertAlmostEqual(grid.beat_to_time(4.0), 2.0)
        self.assertAlmostEqual(grid.beat_to_time(5.0), 3.0)
        self.assertAlmostEqual(grid.snap_time(2.26, 0.5), 2.5)

    def test_chart_uses_beat_grid_and_creates_normal_longs_without_overlap(self):
        notes = NoteBuilder.build_sync_pro(
            self.candidates,
            sustain=[],
            difficulty_params=DIFFICULTY["normal"],
            beat_grid=self.grid,
            song_duration=60.0,
        )

        self.assertTrue(any(note["type"] == "long" for note in notes))
        self.assertEqual(len(notes), len({round(note["time"], 7) for note in notes}))
        for note in notes:
            beat = self.grid.time_to_beat(note["time"])
            self.assertAlmostEqual(beat * 4, round(beat * 4), places=6)
            if note["type"] == "long":
                duration_beats = self.grid.time_to_beat(note["end_time"]) - beat
                self.assertAlmostEqual(duration_beats * 2, round(duration_beats * 2), places=6)
                self.assertFalse(
                    any(note["time"] < other["time"] <= note["end_time"] for other in notes)
                )

    def test_rhythm_rate_controls_sixteenth_note_usage(self):
        candidates = [
            {"time": 0.125 + index * 0.25, "lane": 0, "peak_type": "kick", "strength": 1.0}
            for index in range(12)
        ]

        def sixteenth_count(rhythm_rate):
            notes = NoteBuilder.build_sync_pro(
                candidates,
                sustain=[],
                difficulty_params={
                    "density": 1.0,
                    "long_rate": 0.0,
                    "rhythm_rate": rhythm_rate,
                    "variation": 0.0,
                },
                beat_grid=self.grid,
                song_duration=5.0,
            )
            ticks = [
                round((self.grid.time_to_beat(note["time"]) - self.grid.anchor_beat) * 4)
                for note in notes
            ]
            return sum(tick % 2 for tick in ticks)

        self.assertGreater(sixteenth_count(0.70), sixteenth_count(0.10))

    def test_variation_controls_lane_movement(self):
        candidates = [
            {"time": index * 2.0, "lane": 0, "peak_type": "kick", "strength": 1.0}
            for index in range(12)
        ]

        def lane_changes(variation):
            notes = NoteBuilder.build_sync_pro(
                candidates,
                sustain=[],
                difficulty_params={
                    "density": 1.0,
                    "long_rate": 0.0,
                    "rhythm_rate": 0.0,
                    "variation": variation,
                },
                beat_grid=self.grid,
                song_duration=30.0,
            )
            return sum(note["lane"] != 0 for note in notes)

        self.assertGreater(lane_changes(0.50), lane_changes(0.05))

    def test_builder_snaps_using_bpm_change_events(self):
        changing_grid = BeatGrid(
            120,
            [{"time": 0.0, "bpm": 120}, {"time": 2.0, "bpm": 60}],
            [0.0],
        )
        notes = NoteBuilder.build_sync_pro(
            [{"time": 2.26, "lane": 0, "peak_type": "kick", "strength": 1.0}],
            sustain=[],
            difficulty_params={
                "density": 1.0,
                "long_rate": 0.0,
                "rhythm_rate": 0.0,
                "variation": 0.0,
            },
            beat_grid=changing_grid,
            song_duration=5.0,
        )

        self.assertAlmostEqual(notes[0]["time"], 2.5)

    def test_generator_preserves_supplied_bpm_changes(self):
        bpm_events = [{"time": 0.0, "bpm": 120}, {"time": 2.0, "bpm": 60}]
        bands = {
            name: {2.0: 0.0, 2.26: (1.0 if name == "melody" else 0.1)}
            for name in ("kick", "snare", "hihat", "melody")
        }
        analyzer = SimpleNamespace(
            bpm=120,
            bpm_events=bpm_events.copy(),
            beat_times=[0.0],
            onsets=[(2.26, 1.0)],
            centroid={},
            y=[0.0] * 5,
            sr=1,
            analyze_bpm=Mock(),
            analyze_onsets=Mock(),
            analyze_bands=Mock(return_value=bands),
            detect_sustain=Mock(return_value=[]),
        )

        notes = AutoChartGenerator(analyzer, "expert").generate()

        self.assertEqual(analyzer.bpm_events, bpm_events)
        self.assertTrue(any(abs(note["time"] - 2.25) < 1e-6 for note in notes))

    def test_difficulty_increases_note_and_long_density(self):
        analyzer = SimpleNamespace(
            onsets=[(candidate["time"], candidate["strength"]) for candidate in self.candidates],
            centroid={},
            beat_times=[index * 0.5 for index in range(121)],
        )
        band_times = [candidate["time"] for candidate in self.candidates]
        bands = {
            peak_type: {
                candidate["time"]: (1.0 if candidate["peak_type"] == peak_type else 0.1)
                for candidate in self.candidates
            }
            for peak_type in ("kick", "snare", "hihat", "melody")
        }
        generated = {}
        for difficulty, params in DIFFICULTY.items():
            candidates = PeakDetector.detect_onsets_sync(
                analyzer,
                bands,
                params["density"],
                self.grid,
                60.0,
                params["rhythm_rate"],
            )
            generated[difficulty] = NoteBuilder.build_sync_pro(
                candidates,
                sustain=[],
                difficulty_params=params,
                beat_grid=self.grid,
                song_duration=60.0,
            )
        counts = [len(generated[name]) for name in ("easy", "normal", "hard", "expert")]
        long_counts = [
            sum(note["type"] == "long" for note in generated[name])
            for name in ("easy", "normal", "hard", "expert")
        ]

        self.assertEqual(counts, sorted(counts))
        self.assertEqual(long_counts, sorted(long_counts))
        self.assertGreater(long_counts[1], 0)

    def test_expert_density_adds_on_beat_candidates(self):
        onset_times = [index * 0.1 + 0.03 for index in range(80)]
        analyzer = SimpleNamespace(
            onsets=[(time, 1.0) for time in onset_times],
            centroid={},
            beat_times=[index * 0.5 for index in range(17)],
            bpm=120,
            bpm_events=[{"time": 0.0, "bpm": 120}],
        )
        band_times = [index * 0.01 for index in range(801)]
        bands = {
            peak: {time: (1.0 if peak == "melody" else 0.1) for time in band_times}
            for peak in ("kick", "snare", "hihat", "melody")
        }

        hard = PeakDetector.detect_onsets_sync(analyzer, bands, 0.90, self.grid, 8.0)
        expert = PeakDetector.detect_onsets_sync(analyzer, bands, 1.20, self.grid, 8.0)

        self.assertGreater(len(expert), len(hard))

    def test_no_generated_tap_during_long_hold(self):
        candidates = [
            {"time": 0.0, "lane": 0, "peak_type": "melody", "strength": 1.0},
            {"time": 0.5, "lane": 1, "peak_type": "kick", "strength": 1.0},
            {"time": 1.0, "lane": 2, "peak_type": "snare", "strength": 1.0},
        ]
        notes = NoteBuilder.build_sync_pro(
            candidates,
            sustain=[],
            difficulty_params=DIFFICULTY["normal"],
            beat_grid=self.grid,
            song_duration=4.0,
        )

        for long_note in (note for note in notes if note["type"] == "long"):
            self.assertFalse(
                any(long_note["time"] < note["time"] <= long_note["end_time"] for note in notes)
            )

    def test_legacy_chart_loader_uses_audio_file_and_fallback(self):
        with TemporaryDirectory() as temporary_directory:
            previous_directory = os.getcwd()
            try:
                os.chdir(temporary_directory)
                song = SimpleNamespace(
                    file_path=None,
                    audio_file="legacy_song.wav",
                    audio_analyzer=SimpleNamespace(ensure_audio=Mock(return_value=False)),
                    bpm=120,
                    bpm_events=[],
                    length=12.0,
                    chart=[],
                )

                self.assertTrue(load_chart(song, "NORMAL"))
                self.assertTrue(song.chart)
                self.assertTrue(any(note["type"] == "long" for note in song.chart))
                self.assertTrue(os.path.exists("songs/charts/legacy_song_chart.json"))
            finally:
                os.chdir(previous_directory)


if __name__ == "__main__":
    unittest.main()
