"""
商用仕様：楽曲解析モジュール（完全版）

音声ファイルからテンポ・ピーク・セグメント情報を抽出し、
譜面自動生成に利用する。
"""

import librosa
import numpy as np


class SongAnalyzer:
    """
    商用仕様：楽曲解析クラス
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.bpm = 0
        self.beat_times = []
        self.energy_curve = []
        self.sections = []

    # ============================================================
    # 基本解析
    # ============================================================

    def analyze(self):
        """音声ファイルを解析してテンポ・ビート・エネルギーを抽出"""
        try:
            y, sr = librosa.load(self.file_path)
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            self.bpm = round(tempo)
            self.beat_times = librosa.frames_to_time(beat_frames, sr=sr)

            # エネルギー曲線（音量変化）
            rms = librosa.feature.rms(y=y)[0]
            self.energy_curve = rms / np.max(rms)

            # セクション分割（曲構成）
            self.sections = self._detect_sections(y, sr)

            print(
                f"[Analysis] BPM={self.bpm}, Beats={len(self.beat_times)}, Sections={len(self.sections)}"
            )
            return True
        except Exception as e:
            print(f"[Analysis] Failed: {e}")
            return False

    # ============================================================
    # セクション検出
    # ============================================================

    def _detect_sections(self, y, sr):
        """曲構成を簡易的に検出（静音・ピークを基準）"""
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        peaks = librosa.util.peak_pick(onset_env, 3, 3, 3, 3, 0.5, 5)
        times = librosa.frames_to_time(peaks, sr=sr)

        # セクション境界を生成
        sections = []
        prev_t = 0
        for t in times:
            if t - prev_t > 5.0:  # 5秒以上離れていれば新セクション
                sections.append((prev_t, t))
                prev_t = t
        sections.append((prev_t, librosa.get_duration(y=y, sr=sr)))
        return sections

    # ============================================================
    # 結果取得
    # ============================================================

    def get_summary(self):
        """解析結果を辞書形式で取得"""
        return {
            "bpm": self.bpm,
            "beat_count": len(self.beat_times),
            "sections": len(self.sections),
            "energy_curve": self.energy_curve.tolist()[:100],  # プレビュー用に100点まで
        }
