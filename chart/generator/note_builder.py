from .beat_grid import BeatGrid
from .difficulty import DIFFICULTY_BASE, apply_style_params
from .peak_detector import PeakDetector
import random
import json
import os

# クラシック＋4レーン用レーンマップ
LANE_MAP = {
    "low": 0,
    "mid": 1,   # mid は後で 1/2 に分散
    "high": 3,
}

PEAK_PRIORITY = {
    "low": 0,
    "mid": 1,
    "high": 2,
}


def normalize_notes(notes):
    """
    ロングノーツの範囲にあるタップノーツを整理する後処理。
    - ロング中のタップを削除して、難易度の暴れを抑える
    - レーンに関係なく「ロング＋タップの同時押し」を減らす
    """
    long_ranges = []
    for n in notes:
        if n.get("type") == "long":
            long_ranges.append((float(n["time"]), float(n["end_time"])))

    if not long_ranges:
        return notes

    normalized = []
    for n in notes:
        if n.get("type") == "tap":
            t = float(n["time"])
            # ロングの範囲内ならレーン問わず削除
            if any(start <= t <= end for start, end in long_ranges):
                continue
        normalized.append(n)

    return normalized


class NoteBuilder:
    @staticmethod
    def build_sync_pro(
        candidates,
        sustain,
        style="normal",
        song_id=None,
        difficulty_params=None,
        beat_grid=None,
        song_duration=None,
    ):
        # 難易度パラメータ
        if difficulty_params is not None:
            params = dict(difficulty_params)
        else:
            base = DIFFICULTY_BASE.get(style, DIFFICULTY_BASE["normal"])
            params = apply_style_params(base, style, song_id) if song_id else dict(base)

        grid = beat_grid or BeatGrid(120)
        records = []

        # ------------------------------------------------------------
        # 1. 基本ノーツ生成
        # ------------------------------------------------------------
        prev_lane = None

        for index, candidate in enumerate(candidates):
            local_params = candidate.get("_section_params", params)

            density      = float(local_params.get("density", 1.0))
            rhythm_rate  = float(local_params.get("rhythm_rate", 0.25))
            variation    = float(local_params.get("variation", 0.0))

            # variation の暴れを抑える（NORMAL のみ）
            if style == "normal":
                variation = min(variation, 0.10)

            raw_time = float(candidate["time"])
            if raw_time < 0 or (song_duration and raw_time >= song_duration):
                continue

            beat_step = (
                0.25 if candidate.get("grid_generated")
                else PeakDetector._beat_step(index, rhythm_rate, style)
            )
            note_time = grid.snap_time(raw_time, beat_step)
            if note_time < 0 or (song_duration and note_time >= song_duration):
                continue

            peak_type = candidate.get("peak_type", "low")

            base_lane = LANE_MAP.get(peak_type, 1)
            lane = prev_lane if prev_lane is not None else base_lane

            # mid は中央 1/2 に分散
            if peak_type == "mid":
                lane = random.choice([1, 2])

            # variation によるレーン変化
            if variation > 0:
                change_period = max(2, round(1.0 / variation))
                if (index + 1) % change_period == 0:
                    direction = 1 if ((index + 1) // change_period) % 2 else -1
                    lane = (lane + direction) % 4

                # 階段配置
                if variation >= 0.35:
                    lane = NoteBuilder._apply_lane_pattern(
                        base_lane=base_lane,
                        prev_lane=prev_lane,
                        index=index,
                        peak_type=peak_type,
                        variation=variation,
                    )

            prev_lane = lane

            records.append({
                "lane": lane,
                "time": note_time,
                "peak_type": peak_type,
                "strength": float(candidate.get("strength", 0.0)),
                "_section_params": local_params,
            })

        # ------------------------------------------------------------
        # 2. density による間引き（改良版）
        # ------------------------------------------------------------
        filtered = []
        for r in records:
            local_params = r["_section_params"]
            density = float(local_params.get("density", 1.0))

            # NORMAL の密度を市販ゲーム基準に固定（最大 0.40）
            if style == "normal":
                density = min(density, 0.40)

            keep_rate = min(1.0, density)
            if random.random() <= keep_rate:
                filtered.append(r)

        records = filtered

        # ------------------------------------------------------------
        # 3. 同時刻のノーツを1つに絞る
        # ------------------------------------------------------------
        unique_records = {}
        for r in records:
            key = round(r["time"], 6)
            prev = unique_records.get(key)

            rank_r = (r["strength"], -PEAK_PRIORITY.get(r["peak_type"], 99))
            rank_prev = (prev["strength"], -PEAK_PRIORITY.get(prev["peak_type"], 99)) if prev else None

            if prev is None or rank_r > rank_prev:
                unique_records[key] = r

        records = sorted(unique_records.values(), key=lambda r: r["time"])

        # ------------------------------------------------------------
        # 4. ロング候補選定（セクションごと）
        # ------------------------------------------------------------
        ranked_records = sorted(
            records,
            key=lambda r: (
                not bool(NoteBuilder._matching_sustain(r["time"], sustain, grid)),
                r["peak_type"] != "high",  # メロディ優先でロング化
                -r["strength"],
                r["time"],
            ),
        )

        selected_longs = set()
        section_groups = {}

        for r in ranked_records:
            key = id(r["_section_params"])
            section_groups.setdefault(key, []).append(r)

        for key, group in section_groups.items():
            local_params = group[0]["_section_params"]
            long_rate = float(local_params.get("long_rate", 0.0))
            if long_rate <= 0:
                continue

            long_count = min(len(group), max(1, round(len(group) * long_rate)))
            for rr in group[:long_count]:
                selected_longs.add(round(rr["time"], 6))

        # ------------------------------------------------------------
        # 5. ロング生成（sustain に同期）
        # ------------------------------------------------------------
        output = []
        blocked_until = -float("inf")

        for r in records:
            t = r["time"]
            # ロング中は全レーンブロック（市販ゲーム寄り）
            if t <= blocked_until + 1e-7:
                continue

            is_long = round(t, 6) in selected_longs

            if is_long:
                beats = NoteBuilder._long_duration_beats(t, grid, song_duration, sustain)
                if beats is not None:
                    end_time = grid.beat_to_time(grid.time_to_beat(t) + beats)

                    # 短すぎるロングはタップに落とす
                    if end_time - t < 0.12:
                        output.append({
                            "lane": r["lane"],
                            "time": t,
                            "type": "tap",
                            "end_time": t,
                            "peak_type": r["peak_type"],
                        })
                        continue

                    output.append({
                        "lane": r["lane"],
                        "time": t,
                        "type": "long",
                        "end_time": end_time,
                        "peak_type": r["peak_type"],
                    })
                    blocked_until = end_time
                    continue

            output.append({
                "lane": r["lane"],
                "time": t,
                "type": "tap",
                "end_time": t,
                "peak_type": r["peak_type"],
            })

        # ロング中のタップ整理（市販寄り）
        output = normalize_notes(output)
        return output

    # ------------------------------------------------------------
    # 階段配置（完全版）
    # ------------------------------------------------------------
    @staticmethod
    def _apply_lane_pattern(base_lane, prev_lane, index, peak_type, variation):
        start = prev_lane if prev_lane is not None else base_lane

        if variation < 0.35:
            return start

        # high：上昇・下降階段（メロディ）
        if peak_type == "high":
            step = (index % 4) or 1
            if index % 2 == 0:
                return (start + step) % 4
            else:
                return (start - step) % 4

        # low / mid：ジグザグ階段
        if peak_type in ("low", "mid"):
            if variation >= 0.50:
                zigzag = [0, 2, 1, 3, 2, 0]
                return zigzag[index % len(zigzag)]
            return (start + (index % 4)) % 4

        return start

    # ------------------------------------------------------------
    # sustain 判定
    # ------------------------------------------------------------
    @staticmethod
    def _matching_sustain(note_time, sustain, grid):
        beat = grid.time_to_beat(note_time)
        tol = grid.beat_to_time(beat + 0.25) - note_time

        for start, end in sustain or []:
            start = float(start)
            end = float(end)

            if abs(start - note_time) <= tol or start <= note_time < end:
                if grid.time_to_beat(end) - beat >= 0.5:
                    return start, end

        return None

    # ------------------------------------------------------------
    # ロング長さ（sustain に同期）
    # ------------------------------------------------------------
    @staticmethod
    def _long_duration_beats(note_time, grid, song_duration, sustain):
        match = NoteBuilder._matching_sustain(note_time, sustain, grid)
        if match:
            _, end = match
            desired = grid.time_to_beat(end) - grid.time_to_beat(note_time)
        else:
            desired = 0.5

        if song_duration:
            available = grid.time_to_beat(song_duration) - grid.time_to_beat(note_time)
            if available < desired:
                return None

        return desired

# ============================================================
# ★ キャッシュ統合（完全版）
# ============================================================
def load_chart_cache(song_id, difficulty):
    """譜面キャッシュ読み込み"""
    path = f"cache/charts/{song_id}_{difficulty}.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[NoteBuilder] Cache broken: {e}")
    return None


def save_chart_cache(song_id, difficulty, notes):
    """譜面キャッシュ保存"""
    os.makedirs("cache/charts", exist_ok=True)
    with open(f"cache/charts/{song_id}_{difficulty}.json", "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def build_chart_with_cache(
    song,
    difficulty,
    candidates,
    sustain,
    style="normal",
    difficulty_params=None,
    beat_grid=None,
    song_duration=None,
):
    """
    譜面生成キャッシュ統合版
    - 初回：生成して保存
    - 2回目以降：キャッシュ読み込み
    """
    song_id = song.id

    # ---- キャッシュ読み込み ----
    cached = load_chart_cache(song_id, difficulty)
    if cached:
        print(f"[NoteBuilder] Loaded chart cache for {song_id} ({difficulty})")
        return cached

    print(f"[NoteBuilder] Generating chart for {song_id} ({difficulty})")

    # ---- あなたの既存の譜面生成関数 ----
    notes = NoteBuilder.build_sync_pro(
        candidates=candidates,
        sustain=sustain,
        style=style,
        song_id=song_id,
        difficulty_params=difficulty_params,
        beat_grid=beat_grid,
        song_duration=song_duration,
    )

    # ---- キャッシュ保存 ----
    save_chart_cache(song_id, difficulty, notes)
    print(f"[NoteBuilder] Saved chart cache for {song_id} ({difficulty})")

    return notes
