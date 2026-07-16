"""
商用仕様：Song モデル（完全統合版）

音響解析・譜面生成・譜面ロード・再生制御・メタ情報管理を統合した
ゲーム全体の中心となる曲データモデル。
"""

import os
import pygame
from utils.common.utils import load_chart


class Song:
    """
    商用仕様：曲データモデル（ゲーム全体の中心）
    """

    def __init__(
        self,
        song_id: str,
        title: str,
        file: str,
        bpm: int = 120,
        difficulty: int = 1,
        chart_mode: str = "NORMAL",
        jacket: str = None,
    ):
        # 基本情報
        self.song_id = song_id
        self.title = title
        self.file = file
        self.bpm = bpm
        self.difficulty = difficulty
        self.chart_mode = chart_mode
        self.jacket = jacket

        # 音響解析データ（audio_analyzer が埋める）
        self.pro_onset_times = []
        self.pro_rms = []
        self.pro_centroid_norm = []
        self.pro_sustain = []
        self.pro_sub_onsets = {}

        # BPM 変化イベント（可変 BPM 曲対応）
        self.bpm_events = []  # 例: [{"time": 12.5, "bpm": 180}]

        # 譜面データ
        self.chart = None  # JSON or 自動生成
        self.notes = []  # 最終的な Note オブジェクト

        # 曲の長さ
        self.length = 0.0
        self.loaded = False

    # ============================================================
    # 音響解析結果セット
    # ============================================================

    def set_analysis(
        self,
        onset_times,
        rms,
        centroid_norm,
        sustain,
        sub_onsets=None,
    ):
        """音響解析結果を Song にセットする"""
        self.pro_onset_times = onset_times
        self.pro_rms = rms
        self.pro_centroid_norm = centroid_norm
        self.pro_sustain = sustain
        self.pro_sub_onsets = sub_onsets or {}

    # ============================================================
    # BPM 変化イベントセット
    # ============================================================

    def set_bpm_events(self, events):
        """可変 BPM 曲の BPM イベントをセット"""
        self.bpm_events = events

    # ============================================================
    # 曲データロード
    # ============================================================

    def load(self):
        """音声ファイルと譜面データをロード"""
        if not os.path.exists(self.file):
            print(f"[Song] File not found: {self.file}")
            return False

        try:
            pygame.mixer.music.load(self.file)
            self.length = pygame.mixer.Sound(self.file).get_length()

            # 譜面ロード（JSON or 自動生成）
            load_chart(self, self.chart_mode)

            self.loaded = True
            print(f"[Song] Loaded: {self.title} ({self.chart_mode})")
            return True

        except Exception as e:
            print(f"[Song] Load failed: {e}")
            self.loaded = False
            return False

    # ============================================================
    # 再生制御
    # ============================================================

    def play(self, start_pos: float = 0.0):
        if not self.loaded:
            print("[Song] Not loaded.")
            return
        pygame.mixer.music.play(start=round(start_pos, 2))
        print(f"[Song] Playing from {start_pos:.2f}s")

    def stop(self):
        pygame.mixer.music.stop()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    # ============================================================
    # 譜面 → notes 変換
    # ============================================================

    def build_notes(self):
        """chart → notes の変換（自動譜面生成後に呼ぶ）"""
        notes = []

        for item in self.chart:
            if item["type"] == "tap":
                notes.append({"time": item["time"], "lane": item["lane"], "type": "tap"})
            elif item["type"] == "long":
                notes.append(
                    {
                        "time": item["time"],
                        "lane": item["lane"],
                        "type": "long",
                        "end_time": item["end_time"],
                    }
                )

        self.notes = notes

    # ============================================================
    # 情報取得
    # ============================================================

    def get_info(self) -> dict:
        return {
            "song_id": self.song_id,
            "title": self.title,
            "file": self.file,
            "bpm": self.bpm,
            "difficulty": self.difficulty,
            "chart_mode": self.chart_mode,
            "length": self.length,
            "loaded": self.loaded,
        }

    def __repr__(self):
        return f"<Song id='{self.song_id}' title='{self.title}' mode='{self.chart_mode}'>"
