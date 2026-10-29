from .music_analysis import MusicAnalysis
from .difficulty import DIFFICULTY_BASE, apply_style_params
from .beat_grid import BeatGrid
from .peak_detector import PeakDetector
from .note_builder import NoteBuilder
from .style_detector import StyleDetector


class AutoChartGenerator:
    def __init__(self, analyzer, difficulty="normal"):
        self.analyzer = analyzer
        self.difficulty = difficulty if difficulty in DIFFICULTY_BASE else "normal"

    def generate(self):
        # ============================================================
        # BPM解析
        # ============================================================
        supplied_bpm_events = list(getattr(self.analyzer, "bpm_events", []) or [])

        if not hasattr(self.analyzer, "bpm") or self.analyzer.bpm is None:
            self.analyzer.analyze_bpm()

        # 安全にテンポマップ判定
        def _event_time(ev):
            if isinstance(ev, dict):
                return float(ev.get("time", 0.0))
            if isinstance(ev, (list, tuple)) and len(ev) > 0:
                return float(ev[0])
            return 0.0  # int / float / その他は無視

        has_tempo_map = (
            len(supplied_bpm_events) > 1
            or any(_event_time(event) > 0.0 for event in supplied_bpm_events)
        )

        if has_tempo_map:
            self.analyzer.bpm_events = supplied_bpm_events

        # ============================================================
        # オンセット解析
        # ============================================================
        if not hasattr(self.analyzer, "onsets") or not self.analyzer.onsets:
            self.analyzer.analyze_onsets()

        # ============================================================
        # 周波数帯解析・サステイン解析
        # ============================================================
        analysis = MusicAnalysis(self.analyzer)
        bands = analysis.analyze_bands()
        sustain = analysis.detect_sustain()

        # 曲のスタイル判定
        style = StyleDetector.detect(bands)

        # 難易度パラメータ + 曲別補正
        base_params = DIFFICULTY_BASE[self.difficulty]
        params = apply_style_params(
            base_params,
            self.difficulty,
            getattr(self.analyzer, "song_id", None),
        )

        density = params["density"]
        bpm = float(getattr(self.analyzer, "bpm", None) or 120.0)

        # bpm_events が壊れていても安全にフォールバック
        bpm_events = getattr(self.analyzer, "bpm_events", [])
        if not bpm_events:
            bpm_events = [{"time": 0.0, "bpm": bpm}]

        beat_times = getattr(self.analyzer, "beat_times", [])
        beat_grid = BeatGrid(bpm, bpm_events, beat_times)

        audio = getattr(self.analyzer, "y", None)
        sample_rate = getattr(self.analyzer, "sr", 0)
        song_duration = (
            len(audio) / sample_rate if audio is not None and sample_rate > 0 else None
        )

        # ============================================================
        # セクション難易度（density / variation / long_rate / rhythm_rate）
        # ============================================================
        sections = analysis.analyze_sections()
        section_candidates = []

        for sec in sections:
            sec_start = sec.get("start", 0.0)
            sec_end = sec.get("end", song_duration)
            energy = sec.get("energy", 0.5)

            # ① density 補正（ノーツ量）
            sec_density = density * (0.80 + energy * 0.40)

            # ② variation 補正（レーン変化）
            sec_variation = params["variation"] * (0.60 + energy * 0.70)

            # ③ long_rate 補正（ロング率）
            sec_long_rate = params["long_rate"] * (1.10 - energy * 0.70)

            # ④ rhythm_rate 補正（細かい拍）
            sec_rhythm_rate = params["rhythm_rate"] * (0.55 + energy * 0.65)

            # セクション専用 params
            sec_params = dict(params)
            sec_params["variation"] = sec_variation
            sec_params["long_rate"] = sec_long_rate
            sec_params["rhythm_rate"] = sec_rhythm_rate

            # ⑤ セクション内のピーク検出
            sec_candidates = PeakDetector.detect_onsets_sync(
                self.analyzer,
                bands,
                sec_density,
                beat_grid,
                sec_end - sec_start,
                sec_rhythm_rate,
                style,
            )

            # セクション開始位置に合わせて時間補正
            for c in sec_candidates:
                c["time"] += sec_start
                c["_section_params"] = sec_params  # NoteBuilder に渡す

            section_candidates.extend(sec_candidates)

        candidates = section_candidates

        # ============================================================
        # ノーツ構築（セクション補正済み params を使用）
        # ============================================================
        notes = NoteBuilder.build_sync_pro(
            candidates,
            sustain,
            difficulty_params=params,  # fallback
            beat_grid=beat_grid,
            song_duration=song_duration,
        )

        # ============================================================
        # 正規化
        # ============================================================
        from .note_normalizer import normalize_notes

        notes = normalize_notes(notes)
        notes.sort(key=lambda n: n["time"])

        return notes
