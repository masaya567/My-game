from typing import List

from constants import (
    SCORE_PERFECT,
    SCORE_GREAT,
    SCORE_GOOD,
    SCORE_MISS,
    COMBO_MULTIPLIER,
    DIFFICULTY_JUDGE_SCALE,
    calc_judge_times,
    JUDGE_LINE,
    NOTE_START_Y,
    NOTE_FALL_TIME,
)


class GameLogic:
    """
    商用品質：Note クラス対応ゲームロジック（完全曲同期版）
    """

    def __init__(
        self, notes: List, bpm_events: List, song_bpm: float, difficulty="normal", base_speed=1.0
    ):

        # BPMイベント
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

        # 判定インデックス
        self.current_index = 0

        # スコア
        self.score = 0
        self.combo = 0
        self.max_combo = 0

        self.perfect = 0
        self.great = 0
        self.good = 0
        self.miss = 0

    # ============================================================
    # 判定ウィンドウ（Note.update と完全同期）
    # ============================================================

    def _get_judge_windows(self, song_time):
        distance = JUDGE_LINE - NOTE_START_Y
        note_speed = distance / NOTE_FALL_TIME * self.base_speed

        difficulty_scale = DIFFICULTY_JUDGE_SCALE.get(self.difficulty, 1.0)
        return tuple(window * difficulty_scale for window in calc_judge_times(note_speed))

    # ============================================================
    # メイン更新
    # ============================================================

    def update(self, dt, song_time, base_speed, bpm_events, song_bpm, on_miss=None):

        # BPMイベント更新
        self.bpm_events = [
            (float(ev.get("time", 0.0)), float(ev.get("bpm", song_bpm)))
            for ev in bpm_events
        ]
        self.bpm_events.sort(key=lambda event: event[0])
        self.song_bpm = song_bpm
        self.base_speed = max(0.01, float(base_speed))

        # ノーツ更新（曲同期）
        self.update_notes(dt, song_time, self.base_speed)

        # 自動ミス判定
        self.auto_miss_check(song_time, on_miss)

    # ============================================================
    # current_index 補正
    # ============================================================

    def normalize_current_index(self):
        self.current_index = max(0, min(self.current_index, len(self.notes)))

        while self.current_index < len(self.notes) and getattr(
            self.notes[self.current_index], "finished", False
        ):
            self.current_index += 1

    # ============================================================
    # 現在判定対象ノーツ取得
    # ============================================================

    def get_current_note(self, lane):

        self.normalize_current_index()

        for i in range(self.current_index, len(self.notes)):
            n = self.notes[i]

            if n is None:
                continue
            if getattr(n, "finished", False):
                continue
            if n.lane != lane:
                continue

            return n

        return None

    # ============================================================
    # ノーツ更新（曲同期）
    # ============================================================

    def update_notes(self, dt, song_time, base_speed):
        for note in self.notes:
            if getattr(note, "finished", False):
                continue

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
    # 判定タイミング
    # ============================================================

    def judge_timing(self, song_time, note_time):
        diff = abs(song_time - note_time)
        perfect_window, great_window, good_window, _ = self._get_judge_windows(note_time)

        if diff <= perfect_window:
            return "perfect"
        elif diff <= great_window:
            return "great"
        elif diff <= good_window:
            return "good"
        else:
            return "miss"

    # ============================================================
    # ヘッド判定
    # ============================================================

    def try_judge(self, lane, song_time):
        best_note = None
        best_diff = float("inf")

        for n in self.notes:
            if n is None or n.lane != lane:
                continue
            if getattr(n, "finished", False) or getattr(n, "fade_out", False):
                continue
            if getattr(n, "head_judged", False):
                continue

            diff = abs(song_time - n.time)
            good_window = self._get_judge_windows(n.time)[2]
            if diff > good_window:
                continue

            if diff < best_diff:
                best_diff = diff
                best_note = n

        if best_note is None:
            return "none"

        result = self.judge_timing(song_time, best_note.time)
        if result == "miss":
            return "none"

        best_note.judge_text = result
        self.apply_score(result)

        if best_note.is_long:
            best_note.holding = True
            best_note.head_judged = True
            best_note.tail_judged = False
            return result

        best_note.head_judged = True
        best_note.start_fade_out()

        return result

    # ============================================================
    # ロング：持続ミス
    # ============================================================

    def hold_miss_check(self, lane, is_pressed):
        for n in self.notes:
            if not n.is_long:
                continue
            if n.lane != lane:
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
                return "miss"

        return "none"

    # ============================================================
    # ロング：テール判定
    # ============================================================

    def _get_tail_time(self, n):
        return getattr(n, "tail_time", None) or n.time + getattr(n, "duration", 0.0)

    def release_judge(self, lane, song_time):
        for n in self.notes:
            if not n.is_long:
                continue
            if n.lane != lane:
                continue
            if not getattr(n, "holding", False):
                continue
            if getattr(n, "finished", False):
                continue

            tail_time = self._get_tail_time(n)
            _, _, good_window, _ = self._get_judge_windows(tail_time)

            if song_time < tail_time - good_window:
                n.judge_text = "miss"
                self.apply_score("miss")
                n.start_fade_out()
                n.holding = False
                return "miss"

            diff = abs(tail_time - song_time)
            perfect_window, great_window, good_window, _ = self._get_judge_windows(tail_time)

            if diff <= perfect_window:
                result = "perfect"
            elif diff <= great_window:
                result = "great"
            elif diff <= good_window:
                result = "good"
            else:
                result = "miss"

            n.judge_text = result
            self.apply_score(result)
            n.start_fade_out()
            n.holding = False
            n.tail_judged = True

            renderer = getattr(n, "renderer", None)
            if renderer is not None and hasattr(renderer, "trigger_tail_spark"):
                renderer.trigger_tail_spark(
                    n.x,
                    n.tail_y,
                    getattr(renderer.long_head, "base_color", (120, 200, 255)),
                    1.0,
                )

            return result

        return "none"

    # ============================================================
    # スコア処理
    # ============================================================

    def apply_score(self, result):
        if result == "perfect":
            self.score += int(SCORE_PERFECT * (COMBO_MULTIPLIER ** self.combo))
            self.combo += 1
            self.perfect += 1

        elif result == "great":
            self.score += int(SCORE_GREAT * (COMBO_MULTIPLIER ** self.combo))
            self.combo += 1
            self.great += 1

        elif result == "good":
            self.score += int(SCORE_GOOD * (COMBO_MULTIPLIER ** self.combo))
            self.combo += 1
            self.good += 1

        elif result == "miss":
            self.score += SCORE_MISS
            self.combo = 0
            self.miss += 1

        self.max_combo = max(self.max_combo, self.combo)

    # ============================================================
    # 自動ミス判定
    # ============================================================

    def auto_miss_check(self, song_time, on_miss=None):

        for n in self.notes:
            if getattr(n, "finished", False):
                continue
            if getattr(n, "fade_out", False):
                continue

            # ショート
            if not n.is_long:
                _, _, _, miss_window = self._get_judge_windows(n.time)

                if song_time - n.time >= miss_window:
                    n.judge_text = "miss"
                    self.apply_score("miss")
                    n.start_fade_out()
                    n.finished = True

                    if on_miss:
                        on_miss(n.lane, "miss")

                    break

            # ロング
            else:
                if not getattr(n, "head_judged", False):
                    _, _, _, miss_window = self._get_judge_windows(n.time)
                else:
                    miss_window = None

                if miss_window is not None and song_time - n.time >= miss_window:
                    n.judge_text = "miss"
                    self.apply_score("miss")
                    n.start_fade_out()
                    n.finished = True
                    n.holding = False

                    if on_miss:
                        on_miss(n.lane, "miss")

                    break

                elif getattr(n, "head_judged", False):
                    tail_time = self._get_tail_time(n)
                    _, _, _, tail_miss_window = self._get_judge_windows(tail_time)

                    if song_time - tail_time >= tail_miss_window:
                        n.judge_text = "miss"
                        self.apply_score("miss")
                        n.start_fade_out()
                        n.finished = True
                        n.holding = False

                        if on_miss:
                            on_miss(n.lane, "miss")

                        break

    # ============================================================
    # ゲーム終了判定
    # ============================================================

    def is_finished(self):
        return all(getattr(n, "finished", False) for n in self.notes)
