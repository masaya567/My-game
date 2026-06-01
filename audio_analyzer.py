"""
音声解析モジュール

librosa を使った音声ファイルの解析と特徴抽出を担当します。
"""

from typing import Any, Dict, List, Tuple

import librosa

from logger import get_logger

logger = get_logger(__name__)


class AudioAnalyzer:
    """音声解析クラス"""

    @staticmethod
    def analyze_song(file_path: str) -> Dict[str, Any]:
        """曲を解析して特徴データを抽出

        Args:
            file_path: 音声ファイルパス

        Returns:
            解析結果の辞書（length, onset_times, rms, centroid_norm）
        """
        try:
            y, sr = librosa.load(file_path)
            length = librosa.get_duration(y=y, sr=sr)

            # オンセット検出（リズムの開始点）
            onset_times = AudioAnalyzer._extract_onsets(y, sr)

            # RMS（音量）
            rms = librosa.feature.rms(y=y)[0]

            # スペクトル重心（周波数帯）
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            max_centroid = max(centroid) if max(centroid) > 0 else 1
            centroid_norm = centroid / max_centroid

            logger.info(f"Analyzed: {file_path} ({length:.2f}s, {len(onset_times)} onsets)")

            return {
                "length": length,
                "onset_times": onset_times,
                "rms": rms,
                "centroid_norm": centroid_norm,
            }

        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            return {
                "length": 0.0,
                "onset_times": [],
                "rms": [],
                "centroid_norm": [],
            }

    @staticmethod
    def _extract_onsets(y: List[float], sr: int) -> List[float]:
        """オンセット時刻を抽出

        Args:
            y: 波形データ
            sr: サンプリングレート

        Returns:
            オンセット時刻のリスト
        """
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=False)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)

        if len(onset_times) == 0:
            # フォールバック：0.5秒間隔で生成
            duration = librosa.get_duration(y=y, sr=sr)
            interval = 0.5
            onset_times = [i * interval for i in range(int(duration / interval))]

        return list(onset_times)


def analyze_songs(songs_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """複数の曲を解析

    Args:
        songs_list: 曲情報の辞書リスト

    Returns:
        解析結果を追加した曲情報のリスト
    """
    for song in songs_list:
        analysis = AudioAnalyzer.analyze_song(song["file"])
        song["length"] = analysis["length"]
        song["pro_onset_times"] = analysis["onset_times"]
        song["pro_rms"] = analysis["rms"]
        song["pro_centroid_norm"] = analysis["centroid_norm"]

    return songs_list
