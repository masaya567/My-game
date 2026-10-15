import unittest

import numpy as np
from types import SimpleNamespace

from chart.generator.peak_detector import PeakDetector
from songs.analysis.audio.audio_analyzer import AudioAnalyzer


class AudioAnalyzerTest(unittest.TestCase):
    def make_analyzer(self):
        analyzer = AudioAnalyzer("unused")
        analyzer.sr = 10
        analyzer.hop_length = 1
        return analyzer

    def test_detect_sustain_closes_region_at_end_of_audio(self):
        analyzer = self.make_analyzer()
        analyzer.band_energy = {"melody": np.array([0.0, 0.0, 1.0, 1.0, 1.0])}

        self.assertEqual(analyzer.detect_sustain(min_length=0.3), [(0.2, 0.5)])

    def test_detect_sustain_accepts_timestamp_energy_mapping(self):
        analyzer = self.make_analyzer()
        analyzer.band_energy = {"melody": {0.0: 0.0, 0.1: 0.0, 0.2: 1.0, 0.3: 1.0, 0.4: 1.0}}

        self.assertEqual(analyzer.detect_sustain(min_length=0.3), [(0.2, 0.5)])

    def test_detect_sustain_ignores_silence(self):
        analyzer = self.make_analyzer()
        analyzer.band_energy = {"melody": np.zeros(5)}

        self.assertEqual(analyzer.detect_sustain(), [])

    def test_analyze_bands_reuses_cached_result(self):
        analyzer = self.make_analyzer()
        cached_bands = {"melody": np.array([1.0])}
        analyzer.band_energy = cached_bands
        analyzer.ensure_audio = lambda: self.fail("cached band data should skip audio loading")

        self.assertIs(analyzer.analyze_bands(), cached_bands)

    def test_analyze_sections_rejects_zero_bins(self):
        analyzer = self.make_analyzer()
        analyzer.y = np.ones(10)

        with self.assertRaises(ValueError):
            analyzer.analyze_sections(bins=0)

    def test_analyze_sections_returns_empty_for_empty_audio(self):
        analyzer = self.make_analyzer()
        analyzer.y = np.array([])

        self.assertEqual(analyzer.analyze_sections(), [])

    def test_peak_detector_supports_expert_density(self):
        analyzer = SimpleNamespace(onsets=[(0.1, 1.0)], centroid={})
        bands = {
            "kick": {0.1: 1.0},
            "snare": {0.1: 0.5},
            "hihat": {0.1: 0.2},
            "melody": {0.1: 0.1},
        }

        candidates = PeakDetector.detect_onsets_sync(analyzer, bands, density=1.35)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["peak_type"], "kick")

    def test_peak_detector_uses_nearest_band_frame_after_centroid_shift(self):
        analyzer = SimpleNamespace(onsets=[(0.1, 1.0)], centroid={0.1: 3000.0})
        bands = {
            "kick": {0.1: 0.1},
            "snare": {0.1: 0.2},
            "hihat": {0.1: 0.3},
            "melody": {0.1: 1.0},
        }

        candidates = PeakDetector.detect_onsets_sync(analyzer, bands, density=1.0)

        self.assertEqual(candidates[0]["peak_type"], "melody")
        self.assertEqual(candidates[0]["lane"], 3)

    def test_peak_detector_applies_fractional_difficulty_density(self):
        analyzer = SimpleNamespace(
            onsets=[(time, 1.0) for time in (0.1, 0.2, 0.3, 0.4)],
            centroid={},
        )
        bands = {
            "kick": {time: 1.0 for time in (0.1, 0.2, 0.3, 0.4)},
            "snare": {},
            "hihat": {},
            "melody": {time: 0.0 for time in (0.1, 0.2, 0.3, 0.4)},
        }

        candidates = PeakDetector.detect_onsets_sync(analyzer, bands, density=0.75)

        self.assertEqual(len(candidates), 3)


if __name__ == "__main__":
    unittest.main()
