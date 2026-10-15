"""
商用品質：Song Loader（音声のみ読み込み・譜面は自動生成に統一）
"""

import os
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


def _resolve_music_dir(music_dir="assets/music"):
    if os.path.isabs(music_dir):
        return music_dir

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.abspath(os.path.join(repo_root, music_dir))


class SongLoader:

    def __init__(self, music_dir="assets/music"):
        self.music_dir = _resolve_music_dir(music_dir)
        self.songs = []

    def load_all(self):
        """assets/music 内の曲をすべて読み込み、Song オブジェクトを構築する"""

        if not os.path.exists(self.music_dir):
            print(f"[SongLoader] Directory not found: {self.music_dir}")
            return []

        AUDIO_EXT = (".wav", ".mp3", ".ogg")

        for filename in sorted(os.listdir(self.music_dir)):
            if not filename.lower().endswith(AUDIO_EXT):
                continue

            raw_title = os.path.splitext(filename)[0]
            audio_path = os.path.join(self.music_dir, filename)

            jp_title = TITLE_JP.get(raw_title, raw_title)
            song_id = raw_title.lower().replace(" ", "_")

            # ★ 譜面は読み込まない（自動生成に統一）
            song = Song(
                song_id=song_id,
                title=jp_title,
                audio_file=audio_path,
                chart_file=None,
                bpm=120,
                difficulty="normal",
                chart_mode="NORMAL",
            )

            # AudioAnalyzer をロード
            if not song.load():
                print(f"[SongLoader] Failed to load: {jp_title}")
                continue

            self.songs.append(song)
            print(f"[SongLoader] Loaded: {jp_title}")

        print(f"[SongLoader] Total songs: {len(self.songs)}")
        return self.songs


def load_all_songs(music_dir="assets/music"):
    loader = SongLoader(music_dir)
    return loader.load_all()


def get_songs_as_dict(music_dir="assets/music"):
    return {song.song_id: song for song in load_all_songs(music_dir)}
