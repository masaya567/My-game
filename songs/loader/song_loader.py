"""
商用品質：Song Loader（アプリ化対応・音声のみ読み込み）
"""

import os
import sys
from songs.model.song_model import Song

TITLE_JP = {
    "arabesque1": "アラベスク 第1番",
    "aux-enfers": "地獄のオルフェ",
    "carmen": "カルメン前奏曲",
    "erize": "エリーゼのために",
    "fantaisie": "幻想即興曲",
    "gline": "G線上のアリア",
    "hungarian5": "ハンガリー舞曲 第5番",
    "lacampanella": "ラ・カンパネラ",
    "moonlight": "月光ソナタ 第1楽章",
    "music": "テスト曲",
    "otomenoinori": "乙女の祈り",
    "trukish": "トルコ行進曲",
    "wakareno": "別れの曲",
}


# ============================================================
# ★ アプリ化対応：BASE_DIR を統一
# ============================================================

def get_base_dir():
    # PyInstaller 対応
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def resolve_music_dir():
    base = get_base_dir()
    return os.path.join(base, "assets", "music")


# ============================================================
# ★ SongLoader（完全版）
# ============================================================

class SongLoader:

    def __init__(self, music_dir=None):
        self.music_dir = music_dir or resolve_music_dir()
        self.songs = []

    def load_all(self):
        """assets/music 内の曲をすべて読み込み、Song オブジェクトを構築する"""

        if not os.path.exists(self.music_dir):
            print(f"[SongLoader] ❌ music フォルダが見つかりません: {self.music_dir}")
            return []

        AUDIO_EXT = (".wav", ".mp3", ".ogg")

        print(f"[SongLoader] 読み込み開始: {self.music_dir}")

        for filename in sorted(os.listdir(self.music_dir)):
            if not filename.lower().endswith(AUDIO_EXT):
                continue

            raw_title = os.path.splitext(filename)[0]
            audio_path = os.path.join(self.music_dir, filename)

            jp_title = TITLE_JP.get(raw_title, raw_title)
            song_id = raw_title.lower().replace(" ", "_")

            song = Song(
                song_id=song_id,
                title=jp_title,
                audio_file=audio_path,
                chart_file=None,  # 譜面は自動生成
                bpm=120,
                difficulty="normal",
                chart_mode="NORMAL",
            )

            if not song.load():
                print(f"[SongLoader] ❌ ロード失敗: {jp_title}")
                continue

            self.songs.append(song)
            print(f"[SongLoader] ✔ Loaded: {jp_title}")

        print(f"[SongLoader] ✔ Total songs: {len(self.songs)}")
        return self.songs


def load_all_songs():
    loader = SongLoader()
    return loader.load_all()


def get_songs_as_dict():
    return {song.song_id: song for song in load_all_songs()}
