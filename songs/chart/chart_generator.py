# songs/chart/chart_generator.py

"""
商用品質：自動譜面生成モジュール（完全版・最終形態）

NORMAL / HARD / PRO の自動譜面生成を統合。
音響解析（onset / RMS / centroid）と連携し、Song.notes を構築する。
"""

from typing import Any, Dict, List
import random
from songs.model.song_model import Song

# ============================================================
# レーン割り当て（公平分布 + 音響補正）
# ============================================================


def assign_lane(i: int, bright: float, total_lanes: int = 4) -> int:
    lane = i % total_lanes

    if bright > 0.75:
        lane = min(total_lanes - 1, lane + 1)
    elif bright < 0.25:
        lane = max(0, lane - 1)

    return lane


# ============================================================
# NORMAL（低密度）
# ============================================================


def generate_normal(song: Song) -> List[Dict[str, Any]]:
    chart = []
    for i, t in enumerate(song.pro_onset_times):
        if i % 3 != 0:
            continue
        lane = assign_lane(i, song.pro_centroid_norm[i])
        chart.append({"time": float(t), "lane": lane, "type": "tap"})
    return chart


# ============================================================
# HARD（中密度 + ロング）
# ============================================================


def generate_hard(song: Song) -> List[Dict[str, Any]]:
    chart = []
    for i, t in enumerate(song.pro_onset_times):
        lane = assign_lane(i, song.pro_centroid_norm[i])
        energy = song.pro_rms[i]

        if energy > 0.65:
            sustain = song.pro_sustain[i] if hasattr(song, "pro_sustain") else 0.35
            chart.append(
                {"time": float(t), "lane": lane, "type": "long", "end_time": float(t + sustain)}
            )
        else:
            chart.append({"time": float(t), "lane": lane, "type": "tap"})
    return chart


# ============================================================
# PRO（高密度 + 音響解析フル活用）
# ============================================================


def generate_pro(song: Song) -> List[Dict[str, Any]]:
    chart = []
    for i, t in enumerate(song.pro_onset_times):
        bright = song.pro_centroid_norm[i]
        energy = song.pro_rms[i]
        lane = assign_lane(i, bright)

        if bright > 0.8:
            lane = min(3, lane + 1)
        elif bright < 0.2:
            lane = max(0, lane - 1)

        if energy > 0.7:
            sustain = song.pro_sustain[i] if hasattr(song, "pro_sustain") else 0.45
            chart.append(
                {"time": float(t), "lane": lane, "type": "long", "end_time": float(t + sustain)}
            )
        else:
            chart.append({"time": float(t), "lane": lane, "type": "tap"})

        if hasattr(song, "pro_sub_onsets"):
            for sub in song.pro_sub_onsets.get(i, []):
                chart.append({"time": float(sub), "lane": lane, "type": "tap"})
    return chart


# ============================================================
# メイン：Song.notes を構築
# ============================================================


def build_notes_from_chart(song: Song) -> None:
    if not song.chart:
        if song.chart_mode in ("EASY", "NORMAL"):
            song.chart = generate_normal(song)
        elif song.chart_mode == "HARD":
            song.chart = generate_hard(song)
        elif song.chart_mode == "PRO":
            song.chart = generate_pro(song)

    notes = []
    for item in song.chart:
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

    song.notes = notes
