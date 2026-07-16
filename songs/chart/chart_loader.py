"""
商用仕様：譜面読み込みモジュール（完全版）

JSON 譜面を読み込み、Song オブジェクトに chart を格納する。
自動生成（chart_generator）と連携する。
"""

import json
import os
from typing import Any, Dict, List

from songs.model.song_model import Song


def load_chart(song: Song) -> None:
    """
    譜面を読み込む（商用仕様）

    - assets/charts/<title>.json を探す
    - あれば読み込む
    - なければ空の chart をセット（chart_generator が後で埋める）

    Args:
        song: Song オブジェクト
    """

    # 曲名から JSON ファイル名を生成
    safe_title = song.title.replace(" ", "_")
    chart_path = os.path.join("assets", "charts", f"{safe_title}.json")

    if not os.path.exists(chart_path):
        # JSON がない → 自動生成モード
        song.chart = []
        return

    try:
        with open(chart_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # JSON の形式チェック
        if isinstance(data, list):
            song.chart = data
        elif isinstance(data, dict) and "chart" in data:
            song.chart = data["chart"]
        else:
            print(f"[WARN] 譜面 JSON の形式が不正: {chart_path}")
            song.chart = []

    except Exception as e:
        print(f"[ERROR] 譜面読み込み失敗: {chart_path} ({e})")
        song.chart = []
