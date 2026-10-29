"""
商用品質：Song モデル（完全統合版・音声 + 自動譜面生成 + JSON 譜面 + ジャケット画像）
"""

print("[DEBUG] SongModel loaded from:", __file__)

import os
import pygame
from typing import Optional

from utils.common.utils import load_chart_json
from graphics.note import Note
from songs.analysis.audio.audio_analyzer import AudioAnalyzer
from chart.generator.auto_chart_generator import AutoChartGenerator

# ★ 曲ごとのテーマカラー
from utils.color.theme_colors import SONG_COLOR_MAP

# ★ ジャケット生成
from utils.jacket.jacket_generator import make_proseka_jacket


class Song:
    """
    商用品質：曲データモデル（音声 + 譜面 + ジャケット）
    JSON 譜面があればロード、なければ自動生成。
    ジャケット画像は曲ごとのテーマカラーで自動生成。
    """

    def __init__(
        self,
        song_id: str,
        title: str,
        audio_file: str,
        chart_file: Optional[str],
        bpm: int = 120,
        difficulty: str = "normal",
        chart_mode: str = "NORMAL",
        jacket: str = None,
    ):
        # メタ情報
        self.song_id = song_id
        self.title = title
        self.audio_file = audio_file
        self.chart_file = chart_file  # None = 自動生成
        self.bpm = bpm
        self.difficulty = difficulty
        self.chart_mode = chart_mode
        self.jacket = jacket

        # 解析結果
        self.audio_analyzer = None
        self.bpm_events = []

        # 譜面データ
        self.chart = []  # dict ノーツ
        self.notes = []  # Note オブジェクト

        self.length = 0.0
        self.loaded = False

        # ジャケット画像
        self.jacket_image = None
        self.jacket_shadow = None

        # ============================================================
        # ジャケット画像生成（曲ごとに色テーマを反映）
        # ============================================================
        base_color = SONG_COLOR_MAP.get(self.song_id, (120, 120, 255))

        try:
            self.jacket_shadow, self.jacket_image = make_proseka_jacket(
                title=self.title,
                base_color=base_color,
                image_path="assets/images/note.png",
                size=(256, 256),
            )
            self.jacket = self.jacket_image
            print(f"[Song] Jacket generated for: {self.title}")
        except Exception as e:
            print(f"[Song] Jacket generation failed for {self.title}: {e}")
            self.jacket_shadow = None
            self.jacket_image = None

    # ============================================================
    # 曲データロード（音声ロード → BPM解析 → 譜面ロード）
    # ============================================================

    def load(self):
        # 音声ファイルチェック
        if not self.audio_file or not os.path.exists(self.audio_file):
            print(f"[Song] Audio file not found: {self.audio_file}")
            return False

        # JSON 譜面チェック
        if self.chart_file is not None and not os.path.exists(self.chart_file):
            print(f"[Song] Chart file not found: {self.chart_file}")
            return False

        try:
            # AudioAnalyzer 初期化
            self.audio_analyzer = AudioAnalyzer(self.audio_file)
            self.audio_analyzer.ensure_audio()

            # BPM解析（重複防止）
            if self.audio_analyzer.bpm is None:
                self.audio_analyzer.analyze_bpm()

            self.bpm = float(self.audio_analyzer.bpm or self.bpm)
            self.bpm_events = getattr(self.audio_analyzer, "bpm_events", [])

            # 曲の長さ
            pygame.mixer.music.load(self.audio_file)
            self.length = pygame.mixer.Sound(self.audio_file).get_length()

            # JSON 譜面ロード（自動生成は GameplayScreen に移動）
            if self.chart_file is not None:
                self.chart = load_chart_json(self.chart_file)
                self.build_notes()
            else:
                # ★ 初期ロードでは譜面生成しない（高速化）
                self.chart = []
                self.notes = []

            self.loaded = True
            print(f"[Song] Loaded: {self.title} ({self.chart_mode})")
            return True

        except Exception as e:
            print(f"[Song] Load failed: {e}")
            self.loaded = False
            return False

    # ============================================================
    # dict → Note オブジェクト変換
    # ============================================================

    def build_notes(self):
        self.notes = []

        if not self.chart:
            return

        for item in self.chart:
            lane = item.get("lane", 0)
            time = item.get("time", 0.0)
            note_type = item.get("type", "tap")

            if note_type == "tap":
                duration = 0.0
            else:
                duration = item.get("duration", 0.0)
                if "end_time" in item:
                    duration = max(0.0, item["end_time"] - time)

            self.notes.append(Note(lane, time, duration))

    # ============================================================
    # 再生制御
    # ============================================================

    def play(self, start_pos: float = 0.0):
        if not self.loaded:
            print("[Song] Not loaded.")
            return
        pygame.mixer.music.play(start=round(start_pos, 2))

    def stop(self):
        pygame.mixer.music.stop()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    # ============================================================
    # 情報取得
    # ============================================================

    def get_info(self) -> dict:
        return {
            "song_id": self.song_id,
            "title": self.title,
            "audio": self.audio_file,
            "chart": self.chart_file,
            "bpm": self.bpm,
            "difficulty": self.difficulty,
            "chart_mode": self.chart_mode,
            "length": self.length,
            "loaded": self.loaded,
        }

    def __repr__(self):
        return f"<Song id='{self.song_id}' title='{self.title}' mode='{self.chart_mode}'>"
