"""
曲リスト管理モジュール

曲のメタデータと譜面情報を一元管理します。
"""

from typing import Any, Dict, List

from graphics import make_jacket


class Song:
    """曲データ構造"""

    def __init__(
        self, title: str, file: str, bpm: int, difficulty: int, chart_mode: str = "NORMAL"
    ):
        """曲データを初期化

        Args:
            title: 曲名
            file: 音声ファイルパス
            bpm: BPM（拍/分）
            difficulty: 難易度（1-11）
            chart_mode: 譜面生成モード（EASY, NORMAL, HARD, PRO）
        """
        self.title = title
        self.file = file
        self.jacket = make_jacket()
        self.difficulty = difficulty
        self.bpm = bpm
        self.chart_mode = chart_mode
        self.length = 0.0
        self.chart: List[Dict[str, Any]] = []
        self.notes: List[Any] = []
        self.pro_onset_times: List[float] = []
        self.pro_rms: List[float] = []
        self.pro_centroid_norm: List[float] = []

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換（互換性維持用）"""
        return {
            "title": self.title,
            "file": self.file,
            "jacket": self.jacket,
            "difficulty": self.difficulty,
            "bpm": self.bpm,
            "chart_mode": self.chart_mode,
            "length": self.length,
            "chart": self.chart,
            "notes": self.notes,
            "pro_onset_times": self.pro_onset_times,
            "pro_rms": self.pro_rms,
            "pro_centroid_norm": self.pro_centroid_norm,
        }


# ===========================
# 曲リスト定義
# ===========================
SONG_LIST: List[Song] = [
    Song("エリーゼのために", "assets/music/erize.wav", 130, 4, "NORMAL"),
    Song("トルコ行進曲", "assets/music/trukish.wav", 140, 6, "NORMAL"),
    Song("G線上のアリア", "assets/music/gline.wav", 66, 3, "EASY"),
    Song("乙女の祈り", "assets/music/otomenoinori.wav", 110, 5, "NORMAL"),
    Song("別れの曲", "assets/music/wakareno.wav", 72, 7, "HARD"),
    Song("月光ソナタ 第1楽章", "assets/music/moonlight.wav", 52, 8, "HARD"),
    Song("ラ・カンパネラ", "assets/music/lacampanella.wav", 180, 11, "PRO"),
    Song("ハンガリー舞曲第5番", "assets/music/hungarian5.wav", 140, 7, "HARD"),
    Song("アラベスク第1番", "assets/music/arabesque1.wav", 120, 5, "NORMAL"),
    Song("幻想即興曲", "assets/music/fantaisie.wav", 150, 9, "PRO"),
    Song("ハバネラ（カルメン）", "assets/music/carmen.wav", 132, 7, "HARD"),
    Song("天国と地獄（序曲）", "assets/music/aux-enfers.wav", 160, 9, "PRO"),
]


def get_songs_as_dict() -> List[Dict[str, Any]]:
    """曲リストを辞書形式で取得"""
    return [song.to_dict() for song in SONG_LIST]
