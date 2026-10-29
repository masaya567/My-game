from typing import List
from constants import HEIGHT

from constants import (
    JUDGE_LINE,
    LANE_WIDTH,
)

# ============================================================
# 難易度別判定補正（市販ゲーム基準）
# ============================================================

DIFFICULTY_JUDGE_SCALE = {
    "EASY":   1.40,
    "NORMAL": 1.20,
    "HARD":   1.00,
    "EXPERT": 0.85,
}

# ============================================================
# 基本判定幅（ms）
# ============================================================

BASE_PERFECT = 0.035
BASE_GREAT   = 0.070
BASE_GOOD    = 0.110
BASE_MISS    = 0.150
BASE_TAIL    = 0.050

DIFFICULTY_SPEED = {
    "EASY":   0.75,
    "NORMAL": 1.00,
    "HARD":   1.25,
    "EXPERT": 1.45,
}


def get_judge_windows(difficulty):
    scale = DIFFICULTY_JUDGE_SCALE.get(difficulty.upper(), 1.0)
    return (
        BASE_PERFECT * scale,
        BASE_GREAT   * scale,
        BASE_GOOD    * scale,
        BASE_MISS    * scale,
        BASE_TAIL    * scale,
    )


class GameLogic:
    """
    商用品質：描画キャッシュ対応ゲームロジック完全版
    """

    def __init__(
        self,
        notes: List,
        bpm_events: List,
        song_bpm: float,
        difficulty="normal",
        base_speed=1.0,
        lane_x=None,
    ):
        # BPM イベント
        self.bpm_events = [
            (float(ev.get("time", 0.0)), float(ev.get("bpm", song_bpm)))
            for ev in bpm_events
        ]
        self.bpm_events.sort(key=lambda event: event[0])

        # ノーツ
        self.notes = notes
        self.song_bpm = song_bpm
        self.difficulty = str(difficulty).upper()
        self.base_speed = max(0.01, float(base_speed))
        self.speed_mul = DIFFICULTY_SPEED.get(self.difficulty, 1.0)

        # レーン位置
        self.lane_x = lane_x or [i * LANE_WIDTH + LANE_WIDTH // 2 for i in range(4)]

        # ノーツを lane ごとに分割
        self.notes_by_lane = {0: [], 1: [], 2: [], 3: []}
        for n in self.notes:
            n.x = self.lane_x[n.lane]
            n.tail_time = getattr(n, "tail_time", None) or (
                n.time + getattr(n, "duration", 0.0)
            )
            self.notes_by_lane[n.lane].append(n)

        self.current_index = {0: 0, 1: 0, 2: 0, 3: 0}

        # スコア
        self.score = 0
        self.combo = 0
        self.max_combo = 0

        self.perfect = 0
        self.great = 0
        self.good = 0
        self.miss = 0

        # 判定幅
        (
            self.PERFECT_MS,
            self.GREAT_MS,
            self.GOOD_MS,
            self.MISS_MS,
            self.TAIL_MS,
        ) = get_judge_windows(self.difficulty)

        self.MISS_MS *= 1.3  # 市販ゲーム基準

    # ============================================================
    # 判定
    # ============================================================

    def judge_fixed(self, song_time, note_time):
        diff = abs(song_time - note_time)

        if diff <= self.PERFECT_MS:
            return "perfect"
        elif diff <= self.GREAT_MS:
            return "great"
        elif diff <= self.GOOD_MS:
            return "good"
        elif diff <= self.MISS_MS:
            return "miss"
        else:
            return "miss"

    # ============================================================
    # ノーツ位置事前計算（完全修正版）
    # ============================================================

    def compute_note_positions(self, note, song_time, speed):
        diff = song_time - note.time

        # ★ 難易度速度倍率を反映
        speed_mul = getattr(self, "speed_mul", 1.0)

        note.head_y = JUDGE_LINE + diff * speed * speed_mul * HEIGHT

        if getattr(note, "is_long", False):
            tail_diff = song_time - note.tail_time
            note.tail_y = JUDGE_LINE + tail_diff * speed * speed_mul * HEIGHT
        else:
            note.tail_y = note.head_y

    # ============================================================
    # メイン更新
    # ============================================================

    def update(self, dt, song_time, base_speed, bpm_events, song_bpm, on_miss=None):
        self.bpm_events = [
            (float(ev.get("time", 0.0)), float(ev.get("bpm", song_bpm)))
            for ev in bpm_events
        ]
        self.bpm_events.sort(key=lambda event: event[0])
        self.song_bpm = song_bpm
        self.base_speed = max(0.01, float(base_speed))

        self.update_notes(dt, song_time, self.base_speed)
        self.auto_miss_check(song_time, on_miss)

    # ============================================================
    # ノーツ更新
    # ============================================================

    def update_notes(self, dt, song_time, base_speed):
        for note in self.notes:
            if getattr(note, "finished", False):
                continue

            self.compute_note_positions(note, song_time, base_speed)

            note.song_time = song_time
            note.bpm_events = self.bpm_events
            note.base_speed = base_speed
            note.song_bpm = self.song_bpm

            note.update(
                dt,
                song_time=song_time,
                bpm_events=self.bpm_events,
                base_speed=base_speed,
                song_bpm=self.song_bpm,
            )

    # ============================================================
    # current_index 補正
    # ============================================================

    def normalize_current_index(self, lane):
        idx = self.current_index[lane]
        notes = self.notes_by_lane[lane]

        while idx < len(notes) and getattr(notes[idx], "finished", False):
            idx += 1

        self.current_index[lane] = idx

    # ============================================================
    # 現在判定対象ノーツ取得
    # ============================================================

    def get_current_note(self, lane):
        self.normalize_current_index(lane)
        notes = self.notes_by_lane[lane]

        for i in range(self.current_index[lane], len(notes)):
            n = notes[i]
            if not getattr(n, "finished", False):
                return n

        return None

    # ============================================================
    # ヘッド判定（完全修正版）
    # ============================================================

    def try_judge(self, lane, song_time):
        notes = self.notes_by_lane[lane]
        self.normalize_current_index(lane)

        best_note = None
        best_diff = float("inf")

        for n in notes[self.current_index[lane]:]:
            if getattr(n, "finished", False):
                continue
            if getattr(n, "fade_out", False):
                continue
            if getattr(n, "head_judged", False):
                continue

            diff = abs(song_time - n.time)
            if diff > self.MISS_MS:
                break

            if diff < best_diff:
                best_diff = diff
                best_note = n

        if best_note is None:
            return "none", None

        result = self.judge_fixed(song_time, best_note.time)
        if result == "miss":
            return "none", None

        best_note.judge_text = result

        # ヘッドは is_tail=False（ロングでもショートでも同じ）
        self.apply_score(result, is_tail=False)

        if getattr(best_note, "is_long", False):
            best_note.holding = True
            best_note.head_judged = True
            best_note.tail_judged = False
            return result, best_note

        best_note.head_judged = True
        best_note.start_fade_out()
        return result, best_note

    # ============================================================
    # ロング：持続ミス
    # ============================================================

    def hold_miss_check(self, lane, is_pressed):
        notes = self.notes_by_lane[lane]

        for n in notes:
            if not getattr(n, "is_long", False):
                continue
            if not getattr(n, "holding", False):
                continue
            if getattr(n, "finished", False):
                continue

            if not is_pressed:
                n.judge_text = "miss"
                self.apply_score("miss")
                n.start_fade_out()
                n.holding = False
                return "miss", n

        return "none", None

    # ============================================================
    # ロング：テール判定（完全修正版）
    # ============================================================

    def release_judge(self, lane, song_time):
        notes = self.notes_by_lane[lane]

        for n in notes:
            if not getattr(n, "is_long", False):
                continue
            if not getattr(n, "holding", False):
                continue
            if getattr(n, "finished", False):
                continue

            diff = abs(n.tail_time - song_time)

            if diff <= self.PERFECT_MS:
                result = "perfect"
            elif diff <= self.GREAT_MS:
                result = "great"
            elif diff <= self.GOOD_MS:
                result = "good"
            elif diff <= self.TAIL_MS:
                result = "miss"
            else:
                result = "miss"

            n.judge_text = result

            # ✔ テールは is_tail=True（正しい）
            self.apply_score(result, is_tail=True)

            n.start_fade_out()
            n.holding = False
            n.tail_judged = True

            renderer = getattr(n, "renderer", None)
            if renderer is not None and hasattr(renderer, "trigger_tail_spark"):
                renderer.trigger_tail_spark(
                    n.x,
                    getattr(n, "tail_y", JUDGE_LINE),
                    getattr(renderer.long_head, "base_color", (120, 200, 255)),
                    1.0,
                )

            return result, n

        return "none", None

    # ============================================================
    # スコア処理（完全版）
    # ============================================================

    def apply_score(self, result, is_tail=False):
        base_perfect = 300
        base_great   = 150
        base_good    = 50
        base_miss    = 0

        if is_tail:
            base_perfect //= 2
            base_great   //= 2
            base_good    //= 2

        combo_bonus = 1.0 + min(self.combo, 300) * 0.001

        if result == "perfect":
            self.score += int(base_perfect * combo_bonus)
            self.combo += 1
            self.perfect += 1

        elif result == "great":
            self.score += int(base_great * combo_bonus)
            self.combo += 1
            self.great += 1

        elif result == "good":
            self.score += int(base_good * combo_bonus)
            self.combo += 1
            self.good += 1

        elif result == "miss":
            self.score += base_miss
            self.combo = 0
            self.miss += 1

        self.max_combo = max(self.max_combo, self.combo)

    # ============================================================
    # 自動ミス判定
    # ============================================================

    def auto_miss_check(self, song_time, on_miss=None):
        for lane in range(4):
            notes = self.notes_by_lane[lane]

            for n in notes:
                if getattr(n, "finished", False):
                    continue
                if getattr(n, "fade_out", False):
                    continue

                if not getattr(n, "is_long", False):
                    if song_time - n.time >= self.MISS_MS:
                        n.judge_text = "miss"
                        self.apply_score("miss")
                        n.start_fade_out()
                        if on_miss:
                            on_miss(lane, "miss")
                        break

                else:
                    if not getattr(n, "head_judged", False):
                        if song_time - n.time >= self.MISS_MS:
                            n.judge_text = "miss"
                            self.apply_score("miss")
                            n.start_fade_out()
                            n.holding = False
                            if on_miss:
                                on_miss(lane, "miss")
                            break

                    elif getattr(n, "head_judged", False):
                        if song_time - n.tail_time >= self.MISS_MS:
                            n.judge_text = "miss"
                            self.apply_score("miss")
                            n.start_fade_out()
                            n.holding = False
                            if on_miss:
                                on_miss(lane, "miss")
                            break

    # ============================================================
    # ランク判定
    # ============================================================

    def get_rank(self):
        max_score = 300 * len(self.notes)

        if max_score <= 0:
            return "C"

        ratio = self.score / max_score

        if ratio >= 1.0:
            return "SS"
        elif ratio >= 0.90:
            return "S"
        elif ratio >= 0.80:
            return "A"
        elif ratio >= 0.60:
            return "B"
        else:
            return "C"

    # ============================================================
    # ゲーム終了判定
    # ============================================================

    def is_finished(self):
        return all(
            getattr(n, "finished", False) or getattr(n, "fade_out", False)
            for n in self.notes
        )
