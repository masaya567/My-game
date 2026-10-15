from bisect import bisect_right
import math


class BeatGrid:
    """Convert between song seconds and continuous beat position across BPM changes."""

    def __init__(self, bpm, bpm_events=None, beat_times=None):
        fallback_bpm = self._valid_bpm(bpm, 120.0)
        events_by_time = {}

        for event in bpm_events or []:
            if isinstance(event, dict):
                event_time = event.get("time", 0.0)
                event_bpm = event.get("bpm", fallback_bpm)
            else:
                event_time, event_bpm = event

            try:
                event_time = float(event_time)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(event_time) or event_time < 0:
                continue
            events_by_time[event_time] = self._valid_bpm(event_bpm, fallback_bpm)

        events_by_time.setdefault(0.0, fallback_bpm)
        event_times = sorted(events_by_time)
        first_bpm = events_by_time[event_times[0]]
        self._segments = [(0.0, 0.0, first_bpm)]

        for event_time in event_times[1:]:
            previous_time, previous_beat, previous_bpm = self._segments[-1]
            event_beat = previous_beat + (event_time - previous_time) * previous_bpm / 60.0
            self._segments.append((event_time, event_beat, events_by_time[event_time]))

        self._segment_times = [segment[0] for segment in self._segments]
        self._segment_beats = [segment[1] for segment in self._segments]

        valid_beats = [float(value) for value in (beat_times or []) if float(value) >= 0]
        self.anchor_beat = self.time_to_beat(valid_beats[0]) if valid_beats else 0.0

    @staticmethod
    def _valid_bpm(value, fallback):
        try:
            bpm = float(value)
        except (TypeError, ValueError):
            return fallback
        return bpm if math.isfinite(bpm) and bpm > 0 else fallback

    def time_to_beat(self, song_time):
        song_time = float(song_time)
        index = max(0, bisect_right(self._segment_times, song_time) - 1)
        start_time, start_beat, bpm = self._segments[index]
        return start_beat + (song_time - start_time) * bpm / 60.0

    def beat_to_time(self, beat):
        beat = float(beat)
        index = max(0, bisect_right(self._segment_beats, beat) - 1)
        start_time, start_beat, bpm = self._segments[index]
        return start_time + (beat - start_beat) * 60.0 / bpm

    def snap_time(self, song_time, beat_step):
        beat_step = max(0.001, float(beat_step))
        beat = self.time_to_beat(song_time)
        grid_index = math.floor((beat - self.anchor_beat) / beat_step + 0.5)
        snapped_beat = self.anchor_beat + grid_index * beat_step
        return self.beat_to_time(snapped_beat)

    def iter_times(self, end_time, beat_step=0.25, start_time=0.0):
        beat_step = max(0.001, float(beat_step))
        start_beat = self.time_to_beat(start_time)
        grid_index = math.ceil((start_beat - self.anchor_beat) / beat_step - 1e-9)
        beat = self.anchor_beat + grid_index * beat_step

        while True:
            song_time = self.beat_to_time(beat)
            if song_time >= end_time - 1e-9:
                return
            if song_time >= start_time - 1e-9:
                yield max(0.0, song_time)
            beat += beat_step
