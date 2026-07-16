# game/judge.py

from typing import Tuple
from constants import JUDGE_LINE, LANE_WIDTH

# ============================================================
# ショートノーツ & LNヘッド判定（押した瞬間）
# ============================================================


def handle_keydown(
    notes,
    lane_pressed: int,
    current_time: float,
    score: int,
    combo: int,
    max_combo: int,
    perfect_count: int,
    great_count: int,
    good_count: int,
    miss_count: int,
    judge_callback=None,  # GlowEffect / JudgeBeam を同期
):
    """
    商用品質：ショート判定 + LNヘッド判定（UI方式・時間ベース）
    """

    # 対象レーンの未処理ノーツ
    lane_notes = [n for n in notes if n.lane == lane_pressed and not n.finished]
    if not lane_notes:
        return score, combo, max_combo, None, perfect_count, great_count, good_count, miss_count

    # 最も判定ラインに近いノーツ（時間ベース）
    note = min(lane_notes, key=lambda n: abs(n.time - current_time))
    diff = note.time - current_time
    diff_abs = abs(diff)

    # 判定幅（秒）
    PERFECT = 0.033
    GREAT = 0.066
    GOOD = 0.100

    # 判定処理
    if diff_abs <= PERFECT:
        judge = "perfect"
        score += 1000
        combo += 1
        perfect_count += 1

    elif diff_abs <= GREAT:
        judge = "great"
        score += 700
        combo += 1
        great_count += 1

    elif diff_abs <= GOOD:
        judge = "good"
        score += 300
        combo += 1
        good_count += 1

    else:
        judge = "miss"
        combo = 0
        miss_count += 1

        # ショートノーツなら即終了
        if not note.is_long:
            note.finished = True

        if judge_callback:
            judge_callback(judge)

        return score, combo, max_combo, judge, perfect_count, great_count, good_count, miss_count

    # ロングノーツのヘッド判定
    if not note.is_long:
        note.finished = True
    else:
        note.holding = True
        note.head_judged = True

    max_combo = max(max_combo, combo)

    if judge_callback:
        judge_callback(judge)

    return score, combo, max_combo, judge, perfect_count, great_count, good_count, miss_count


# ============================================================
# ロングノーツ：ホールド判定（押し続け）
# ============================================================


def handle_long_hold(
    note,
    is_pressed: bool,
    combo: int,
    miss_count: int,
    judge_callback=None,
):
    """
    ロングノーツのホールド判定（押し続けているか）
    """

    if note.finished or not note.head_judged:
        return combo, miss_count

    # 離した瞬間に MISS
    if not is_pressed:
        note.finished = True
        combo = 0
        miss_count += 1

        if judge_callback:
            judge_callback("miss")

    return combo, miss_count


# ============================================================
# ロングノーツ：テール判定（離した瞬間）
# ============================================================


def handle_long_tail(
    note,
    current_time: float,
    score: int,
    combo: int,
    max_combo: int,
    perfect_count: int,
    great_count: int,
    good_count: int,
    miss_count: int,
    judge_callback=None,
):
    """
    ロングノーツのテール判定（離す）
    """

    if note.finished or not note.head_judged:
        return score, combo, max_combo, None, perfect_count, great_count, good_count, miss_count

    diff = note.tail_time - current_time
    diff_abs = abs(diff)

    PERFECT = 0.033
    GREAT = 0.066
    GOOD = 0.100

    if diff_abs <= PERFECT:
        judge = "perfect"
        score += 1000
        combo += 1
        perfect_count += 1

    elif diff_abs <= GREAT:
        judge = "great"
        score += 700
        combo += 1
        great_count += 1

    elif diff_abs <= GOOD:
        judge = "good"
        score += 300
        combo += 1
        good_count += 1

    else:
        judge = "miss"
        combo = 0
        miss_count += 1

    note.finished = True
    note.holding = False
    max_combo = max(max_combo, combo)

    if judge_callback:
        judge_callback(judge)

    return score, combo, max_combo, judge, perfect_count, great_count, good_count, miss_count
