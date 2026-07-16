"""
商用仕様：音響解析モジュール（完全版）

音声ファイルからスペクトラム・ピーク・周波数分布を抽出し、
譜面生成やビジュアルエフェクトに利用する。
"""

import librosa
import numpy as np


class AudioAnalyzer:
    """
    商用仕様：音響解析クラス
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sr = 0
        self.y = None
        self.spectrum = None
        self.peaks = []
        self.freq_distribution = None

    # ============================================================
    # 音声ロード
    # ============================================================

    def load_audio(self):
        """音声ファイルをロード"""
        try:
            self.y, self.sr = librosa.load(self.file_path)
            print(f"[AudioAnalyzer] Loaded audio: {self.file_path}")
            return True
        except Exception as e:
            print(f"[AudioAnalyzer] Load failed: {e}")
            return False

    # ============================================================
    # スペクトラム解析
    # ============================================================

    def analyze_spectrum(self):
        """スペクトラム解析（周波数成分抽出）"""
        if self.y is None:
            print("[AudioAnalyzer] Audio not loaded.")
            return None

        stft = np.abs(librosa.stft(self.y))
        self.spectrum = librosa.amplitude_to_db(stft, ref=np.max)
        self.freq_distribution = np.mean(self.spectrum, axis=1)
        print(f"[AudioAnalyzer] Spectrum analyzed. Shape={self.spectrum.shape}")
        return self.spectrum

    # ============================================================
    # ピーク検出
    # ============================================================

    def detect_peaks(self, threshold: float = 0.6):
        """音量ピークを検出"""
        if self.y is None:
            print("[AudioAnalyzer] Audio not loaded.")
            return []

        rms = librosa.feature.rms(y=self.y)[0]
        peaks = np.where(rms > np.max(rms) * threshold)[0]
        times = librosa.frames_to_time(peaks, sr=self.sr)
        self.peaks = times.tolist()
        print(f"[AudioAnalyzer] Detected {len(self.peaks)} peaks.")
        return self.peaks

    # ============================================================
    # 結果取得
    # ============================================================

    def get_summary(self):
        """解析結果を辞書形式で取得"""
        return {
            "sample_rate": self.sr,
            "peak_count": len(self.peaks),
            "freq_distribution": (
                self.freq_distribution.tolist()[:50] if self.freq_distribution is not None else []
            ),
        }
