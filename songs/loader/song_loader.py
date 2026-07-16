"""
商用品質：Song Loader（完全版・最終形態）

assets/music 内の音声ファイルを自動スキャンし、
SongModel（songs/model/song_model.py）に合わせて Song オブジェクトを生成する。
"""

import os
from songs.model.song_model import Song


class SongLoader:
    """
    商用品質：曲一覧管理クラス
    """

    def __init__(self, music_dir: str = "assets/music"):
        self.music_dir = music_dir
        self.songs = []

    # ============================================================
    # 曲データ読み込み
    # ============================================================

    def load_all(self):
        """assets/music 内の曲データを自動読み込み"""

        if not os.path.exists(self.music_dir):
            print(f"[SongLoader] Directory not found: {self.music_dir}")
            return

        AUDIO_EXT = (".wav", ".mp3", ".ogg")

        for filename in os.listdir(self.music_dir):
            if not filename.lower().endswith(AUDIO_EXT):
                continue

            title = os.path.splitext(filename)[0]
            file_path = os.path.join(self.music_dir, filename)

            # ★ Song ID はファイル名で統一
            song_id = title.lower().replace(" ", "_")

            # ★ BPM は後で自動解析するので仮値
            bpm = 120

            # ★ 難易度は仮で NORMAL=1
            difficulty = 1

            # ★ chart_mode は NORMAL
            chart_mode = "NORMAL"

            song = Song(
                song_id=song_id,
                title=title,
                file=file_path,
                bpm=bpm,
                difficulty=difficulty,
                chart_mode=chart_mode,
            )

            self.songs.append(song)
            print(f"[SongLoader] Loaded: {title}")

        print(f"[SongLoader] Total songs: {len(self.songs)}")

    # ============================================================
    # 曲検索
    # ============================================================

    def find_by_title(self, title: str):
        """タイトルで曲を検索"""
        for song in self.songs:
            if song.title.lower() == title.lower():
                return song
        print(f"[SongLoader] Song not found: {title}")
        return None

    # ============================================================
    # 曲一覧取得
    # ============================================================

    def get_all_titles(self):
        return [song.title for song in self.songs]

    def get_all_songs(self):
        return self.songs
