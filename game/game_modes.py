"""
商用品質：曲ロード・解析モジュール（完全版）

・例外処理（ResourceLoadError / ChartParseError）
・ログ強化
・破損曲のスキップ
・ロード時間計測
・キャッシュ対応
・呼び出し側に結果を返す
"""

import time
from songs.analysis.audio.audio_analyzer import analyze_songs
from songs.loader.song_loader import get_songs_as_dict
from exceptions import ResourceLoadError, ChartParseError
from game.logger import get_logger

logger = get_logger(__name__)

songs_cache = None


def load_all_songs():
    """
    商用品質：曲データをロードして解析する
    """

    global songs_cache

    # キャッシュがあれば即返す（商用品質）
    if songs_cache is not None:
        logger.info(f"Using cached songs ({len(songs_cache)} entries)")
        return songs_cache

    start = time.perf_counter()

    # ------------------------------------------------------------
    # 曲データ読み込み
    # ------------------------------------------------------------
    try:
        raw_songs = get_songs_as_dict()
        if not raw_songs:
            raise ResourceLoadError("songs directory")

        logger.info(f"Found {len(raw_songs)} raw songs. Starting analysis...")

    except Exception as e:
        logger.error(f"Failed to load song dictionary: {e}")
        raise ResourceLoadError("songs directory") from e

    # ------------------------------------------------------------
    # 曲解析
    # ------------------------------------------------------------
    analyzed_songs = {}
    skipped = 0

    for song_id, song_data in raw_songs.items():
        try:
            analyzed = analyze_songs({song_id: song_data})

            if analyzed and song_id in analyzed:
                analyzed_songs[song_id] = analyzed[song_id]
                logger.debug(f"Analyzed song: {song_id}")
            else:
                raise ChartParseError(song_id)

        except ChartParseError as ce:
            logger.warning(f"Skipped corrupted chart: {song_id} ({ce})")
            skipped += 1

        except Exception as e:
            logger.error(f"Unexpected error analyzing '{song_id}': {e}")
            skipped += 1

    # ------------------------------------------------------------
    # ロード結果ログ
    # ------------------------------------------------------------
    elapsed = time.perf_counter() - start

    logger.info(f"Loaded {len(analyzed_songs)} songs " f"(Skipped {skipped}) in {elapsed:.2f}s")

    songs_cache = analyzed_songs
    return analyzed_songs
