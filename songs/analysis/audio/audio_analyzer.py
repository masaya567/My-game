import librosa
import numpy as np
import json
import os


class AudioAnalyzer:
    """
    商用仕様：音響解析クラス（ゲーム完全統合版）
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sr = 0
        self.y = None

        # キャッシュ
        self.spectrum = None
        self.freq_distribution = None
        self.band_energy = None
        self.sustain_regions = None
        self.sections = None

        # BPM
        self.bpm = None
        self.beat_times = []
        self.bpm_events = []  # AutoChartGenerator 用
        self.onsets = None
        self.centroid = {}

        # STFT / 時間変換
        self.hop_length = 512  # AutoChartGenerator と統一

    # ============================================================
    # キャッシュ読み込み
    # ============================================================

    def load_cache(self, song_id):
        path = f"cache/audio/{song_id}.json"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[AudioAnalyzer] Cache broken: {e}")
        return None

    # ============================================================
    # キャッシュ保存
    # ============================================================

    def save_cache(self, song_id, data):
        os.makedirs("cache/audio", exist_ok=True)
        with open(f"cache/audio/{song_id}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ============================================================
    # 音声ロード
    # ============================================================

    def ensure_audio(self) -> bool:
        if self.y is None:
            try:
                self.y, self.sr = librosa.load(self.file_path, sr=None)
                if self.sr <= 0 or self.y is None or self.y.size == 0:
                    self.y = None
                    self.sr = 0
                    print("[AudioAnalyzer] Load failed: audio contains no samples")
                    return False
                print(f"[AudioAnalyzer] Loaded audio: {self.file_path}")
                return True
            except Exception as e:
                print(f"[AudioAnalyzer] Load failed: {e}")
                return False
        return True

    def load_audio(self, file_path: str):
        self.file_path = file_path
        return True

    # ============================================================
    # フレーム → 時間変換
    # ============================================================

    def frame_to_time(self, frame: int) -> float:
        return float(librosa.frames_to_time(frame, sr=self.sr, hop_length=self.hop_length))

    # ============================================================
    # スペクトラム解析
    # ============================================================

    def analyze_spectrum(self):
        if not self.ensure_audio():
            return None

        stft = np.abs(librosa.stft(self.y, hop_length=self.hop_length))
        self.spectrum = librosa.amplitude_to_db(stft, ref=np.max)
        self.freq_distribution = np.mean(self.spectrum, axis=1)
        return self.spectrum

    # ============================================================
    # BPM 推定
    # ============================================================

    def analyze_bpm(self):
        if not self.ensure_audio():
            self.bpm = 120.0
            self.beat_times = []
            self.bpm_events = []
            return self.bpm, self.beat_times

        tempo, beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr)

        if tempo is None:
            tempo = 120.0

        if isinstance(tempo, (np.ndarray, list)):
            tempo = float(tempo[0])
        else:
            tempo = float(tempo)

        self.bpm = tempo
        self.beat_times = librosa.frames_to_time(beat_frames, sr=self.sr).tolist()
        self.bpm_events = [{"time": 0.0, "bpm": self.bpm}]

        print(f"[AudioAnalyzer] BPM detected: {self.bpm}")
        return self.bpm, self.beat_times

    # ============================================================
    # オンセット解析
    # ============================================================

    def analyze_onsets(self):
        if self.onsets is not None:
            return self.onsets
        if not self.ensure_audio():
            self.onsets = []
            self.centroid = {}
            return self.onsets

        onset_envelope = librosa.onset.onset_strength(
            y=self.y, sr=self.sr, hop_length=self.hop_length
        )
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_envelope,
            sr=self.sr,
            hop_length=self.hop_length,
            units="frames",
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sr, hop_length=self.hop_length)

        self.onsets = [
            (float(time), float(onset_envelope[frame]))
            for frame, time in zip(onset_frames, onset_times)
            if 0 <= frame < len(onset_envelope)
        ]

        centroid_values = librosa.feature.spectral_centroid(
            y=self.y, sr=self.sr, hop_length=self.hop_length
        )[0]
        centroid_times = librosa.frames_to_time(
            np.arange(len(centroid_values)), sr=self.sr, hop_length=self.hop_length
        )

        self.centroid = {
            round(float(time), 3): float(value)
            for time, value in zip(centroid_times, centroid_values)
        }

        return self.onsets

    # ============================================================
    # 帯域別エネルギー解析
    # ============================================================

    def analyze_bands(self):
        if self.band_energy is not None:
            return self.band_energy

        if not self.ensure_audio():
            return None

        S = np.abs(librosa.stft(self.y, hop_length=self.hop_length))
        freqs = librosa.fft_frequencies(sr=self.sr, n_fft=(S.shape[0] - 1) * 2)

        hop = self.hop_length
        times = librosa.frames_to_time(np.arange(S.shape[1]), sr=self.sr, hop_length=hop)

        def band_energy(low, high):
            mask = (freqs >= low) & (freqs <= high)
            if not np.any(mask):
                return np.zeros(S.shape[1])
            return np.mean(S[mask], axis=0)

        kick = band_energy(30, 120)
        snare = band_energy(150, 250)
        hihat = band_energy(4000, 10000)
        melody = band_energy(300, 3000)

        bands = {"kick": {}, "snare": {}, "hihat": {}, "melody": {}}

        for i, t in enumerate(times):
            t_r = round(float(t), 3)
            bands["kick"][t_r] = float(kick[i])
            bands["snare"][t_r] = float(snare[i])
            bands["hihat"][t_r] = float(hihat[i])
            bands["melody"][t_r] = float(melody[i])

        self.band_energy = bands
        return bands

    # ============================================================
    # サステイン検出
    # ============================================================

    def detect_sustain(self, band_key="melody", min_length=0.3):
        if self.band_energy is None:
            if self.analyze_bands() is None:
                return []

        band_energy = self.band_energy.get(band_key)
        if band_energy is None or self.sr <= 0 or len(band_energy) == 0:
            return []

        if isinstance(band_energy, dict):
            samples = sorted((float(t), float(value)) for t, value in band_energy.items())
            times = np.asarray([sample[0] for sample in samples], dtype=float)
            energies = np.asarray([sample[1] for sample in samples], dtype=float)
        else:
            energies = np.asarray(band_energy, dtype=float)
            times = np.arange(len(energies), dtype=float) * self.hop_length / self.sr

        if energies.size == 0:
            return []

        threshold = float(np.max(energies)) * 0.5
        if threshold <= 0:
            return []

        above = energies > threshold

        sustain = []
        start = None
        hop = self.hop_length

        for i, flag in enumerate(above):
            if flag and start is None:
                start = i
            elif not flag and start is not None:
                end = i
                t_start = times[start]
                t_end = times[end] if end < len(times) else times[-1] + hop / self.sr
                if t_end - t_start >= min_length:
                    sustain.append((float(t_start), float(t_end)))
                start = None

        if start is not None:
            t_start = times[start]
            t_end = times[-1] + hop / self.sr
            if t_end - t_start >= min_length:
                sustain.append((float(t_start), float(t_end)))

        self.sustain_regions = sustain
        return sustain

    # ============================================================
    # 曲構造推定
    # ============================================================

    def analyze_sections(self, section_len=8.0):
        if not self.ensure_audio():
            return []

        y = self.y
        sr = self.sr
        duration = len(y) / sr

        bands = self.analyze_bands()
        onsets = self.analyze_onsets()

        sections = []
        t = 0.0

        while t < duration:
            start = t
            end = min(t + section_len, duration)

            seg = y[int(start * sr): int(end * sr)]
            volume_energy = float(seg.std()) * 1.2

            melody_energy = np.mean([
                v for time, v in bands["melody"].items()
                if start <= time <= end
            ]) if bands else 0.0

            kick_energy = np.mean([
                v for time, v in bands["kick"].items()
                if start <= time <= end
            ]) if bands else 0.0

            snare_energy = np.mean([
                v for time, v in bands["snare"].items()
                if start <= time <= end
            ]) if bands else 0.0

            hihat_energy = np.mean([
                v for time, v in bands["hihat"].items()
                if start <= time <= end
            ]) if bands else 0.0

            drum_energy = (
                kick_energy * 0.6 +
                snare_energy * 0.8 +
                hihat_energy * 0.4
            )

            onset_count = sum(1 for o, _ in onsets if start <= o <= end)
            onset_density = onset_count / max(1.0, (end - start))

            spectrum_energy = (
                np.mean([v for time, v in bands["kick"].items() if start <= time <= end]) +
                np.mean([v for time, v in bands["snare"].items() if start <= time <= end]) +
                np.mean([v for time, v in bands["hihat"].items() if start <= time <= end])
            ) / 3.0 if bands else 0.0

            raw_energy = (
                0.35 * volume_energy +
                0.25 * melody_energy +
                0.20 * drum_energy +
                0.10 * onset_density +
                0.10 * spectrum_energy
            )

            energy = max(0.0, min(raw_energy, 1.0))

            sections.append({
                "start": start,
                "end": end,
                "energy": energy,
            })

            t += section_len

        self.sections = sections
        return sections

    # ============================================================
    # ★ 全解析キャッシュ統合（最重要）
    # ============================================================

    def analyze_all(self, song_id):
        cache = self.load_cache(song_id)
        if cache:
            print(f"[AudioAnalyzer] Loaded cache for {song_id}")
            self.bpm = cache["bpm"]
            self.beat_times = cache["beat_times"]
            self.band_energy = cache["band_energy"]
            self.onsets = cache["onsets"]
            self.sustain_regions = cache["sustain"]
            self.sections = cache["sections"]

            # ★ 追加（抜けていた部分）
            self.spectrum = cache.get("spectrum")
            self.freq_distribution = cache.get("freq_distribution")

            return cache

        print(f"[AudioAnalyzer] Running full analysis for {song_id}")

        self.analyze_bpm()
        self.analyze_bands()
        self.analyze_onsets()
        self.detect_sustain()
        self.analyze_sections()
        self.analyze_spectrum()  # ★ スペクトラム解析を呼ぶ必要あり

        data = {
            "bpm": self.bpm,
            "beat_times": self.beat_times,
            "band_energy": self.band_energy,
            "onsets": self.onsets,
            "sustain": self.sustain_regions,
            "sections": self.sections,

            # ★ 追加（抜けていた部分）
            "spectrum": self.spectrum,
            "freq_distribution": self.freq_distribution,
        }

        self.save_cache(song_id, data)
        print(f"[AudioAnalyzer] Saved cache for {song_id}")

        return data


def analyze_songs(songs):
    if isinstance(songs, dict):
        analyzed = {}
        for song_id, song in songs.items():
            if getattr(song, "audio_analyzer", None) is None and hasattr(song, "load"):
                if not song.load():
                    continue
            analyzed[song_id] = song
        return analyzed
    return songs
