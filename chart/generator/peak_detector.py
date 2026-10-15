from bisect import bisect_left
from math import ceil
import numpy as np


class PeakDetector:
    @staticmethod
    def detect_onsets_sync(
        analyzer,
        bands,
        density=1.0,
        beat_grid=None,
        song_duration=None,
        rhythm_rate=0.25,
    ):
        onsets = getattr(analyzer, "onsets", [])
        centroids = getattr(analyzer, "centroid", {})
        band_times = sorted(float(t) for t in bands.get("melody", {}))

        candidates = []
        density = max(0.01, float(density))

        for idx, (t, strength) in enumerate(onsets):

            # density による間引き
            if density < 1.0 and int((idx + 1) * density) == int(idx * density):
                continue

            t = float(t)

            # centroid 補正（±10ms）
            c = centroids.get(round(t, 3), None)
            if c is not None:
                norm_c = np.clip((c - 500) / 2500, -1.0, 1.0)
                t += norm_c * 0.01

            # onset_strength + centroid + band_energy の複合判定
            onset_strength = strength
            centroid_value = centroids.get(round(t, 3), 0.0)

            peak_type = PeakDetector._classify_peak(
                bands,
                t,
                band_times,
                onset_strength,
                centroid_value,
            )

            lane = {
                "kick": 0,
                "snare": 1,
                "hihat": 2,
                "melody": 3,
            }.get(peak_type, 0)

            candidates.append(
                {
                    "time": t,
                    "lane": lane,
                    "peak_type": peak_type,
                    "strength": strength,
                }
            )

        # density > 1.0 の追加ノーツ生成（既存ロジック）
        if density > 1.0 and beat_grid is not None and song_duration is not None and candidates:
            occupied_times = set()
            for index, candidate in enumerate(candidates):
                step = (
                    0.25
                    if candidate.get("grid_generated")
                    else PeakDetector._beat_step(index, rhythm_rate)
                )
                occupied_times.add(round(beat_grid.snap_time(candidate["time"], step), 6))

            extra_target = max(0, ceil(len(onsets) * density) - len(occupied_times))
            extra_candidates = []

            for grid_time in beat_grid.iter_times(song_duration, beat_step=0.25):
                if round(grid_time, 6) in occupied_times:
                    continue

                peak_type = PeakDetector._classify_peak(
                    bands,
                    grid_time,
                    band_times,
                    0.0,
                    centroids.get(round(grid_time, 3), 0.0),
                )

                strength = max(
                    bands.get(name, {}).get(PeakDetector._nearest_time(band_times, grid_time), 0.0)
                    for name in ("kick", "snare", "hihat", "melody")
                )
                if strength <= 0:
                    continue

                extra_candidates.append(
                    {
                        "time": grid_time,
                        "lane": {
                            "kick": 0,
                            "snare": 1,
                            "hihat": 2,
                            "melody": 3,
                        }.get(peak_type, 0),
                        "peak_type": peak_type,
                        "strength": strength,
                        "grid_generated": True,
                    }
                )

            extra_candidates.sort(key=lambda candidate: (-candidate["strength"], candidate["time"]))
            candidates.extend(extra_candidates[:extra_target])

        return candidates

    @staticmethod
    def _classify_peak(bands, t, band_times, onset_strength, centroid_value):
        """
        peak_type 強化版（複合判定）
        - 帯域エネルギー
        - onset_strength
        - spectral_centroid
        """

        sample_time = PeakDetector._nearest_time(band_times, t)

        kick = bands.get("kick", {}).get(sample_time, 0.0)
        snare = bands.get("snare", {}).get(sample_time, 0.0)
        hihat = bands.get("hihat", {}).get(sample_time, 0.0)
        melody = bands.get("melody", {}).get(sample_time, 0.0)

        # 複合スコア
        kick_score   = kick   * 1.2 + onset_strength * 0.8
        snare_score  = snare  * 1.1 + onset_strength * 0.6
        hihat_score  = hihat  * 1.0 + centroid_value * 0.7
        melody_score = melody * 1.0 + centroid_value * 0.5

        scores = {
            "kick": kick_score,
            "snare": snare_score,
            "hihat": hihat_score,
            "melody": melody_score,
        }

        return max(scores, key=scores.get)

    @staticmethod
    def _beat_step(index, rhythm_rate):
        fine_slots = int(round(max(0.0, min(1.0, float(rhythm_rate))) * 4))
        phase = index % 4
        if phase < fine_slots:
            return 0.25
        return 0.5 if phase % 2 == 0 else 1.0

    @staticmethod
    def _nearest_time(times, target):
        if not times:
            return target
        index = bisect_left(times, target)
        if index == 0:
            return times[0]
        if index == len(times):
            return times[-1]
        before = times[index - 1]
        after = times[index]
        return before if target - before <= after - target else after
