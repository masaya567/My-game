from typing import List
import pygame

from constants import (
    JUDGE_LINE,
    JUDGE_WINDOW,
    SCORE_PERFECT,
    SCORE_GREAT,
    SCORE_GOOD,
    SCORE_MISS,
    COMBO_MULTIPLIER,
)

from game.judge import judge_timing
from game.update.effect_update import spawn_hit_effect


class GameLogic:
    """
    商用品質：Note クラス対応ゲームロジック
    - ショートノーツ
    - ロングノーツ（ヘッド判定 → ホールド → テール判定）
    """

    def __init__(self, notes: List, bpm_events: List, song_bpm: float):
        self.notes = notes
        self.bpm_events = bpm_events
        self.song_bpm = song_bpm

        # 判定用
        self.current_index = 0

        # スコア・コンボ
        self.score = 0
        self.combo = 0
        self.max_combo = 0

        # 判定カウント
        self.perfect = 0
        self.great = 0
        self.good = 0
        self.miss = 0

    # ============================================================
    # ノーツ更新（Note クラスの update を呼ぶ）
    # ============================================================

    def update_notes(self, dt: float, song_time: float, base_speed: float):
        for note in self.notes:
            note.update(dt, song_time, self.bpm_events, base_speed, self.song_bpm)

    # ============================================================
    # 判定処理（ショート / ロングヘッド）
    # ============================================================

    def try_judge(self, lane: int, song_time: float):
        """
        キー押下時に判定を試みる
        - ショートノーツ → head_y 判定
        - ロングノーツ → head_y 判定（holding = True にする）
        """

        target = None

        # 判定ウィンドウ（秒）
        perfect_w = JUDGE_WINDOW["PERFECT"] / 1000.0
        great_w = JUDGE_WINDOW["GREAT"] / 1000.0
        good_w = JUDGE_WINDOW["GOOD"] / 1000.0

        # lane のノーツを探索
        for i in range(self.current_index, len(self.notes)):
            n = self.notes[i]

            if n.lane != lane:
                continue
            if n.finished:
                continue

            # head_y と判定ラインの距離
            dist = abs(n.head_y - JUDGE_LINE)

            # 判定ウィンドウ内なら対象
            if dist <= good_w * 900:  # px → 時間換算は Note.update が行うため px 判定でOK
                target = n
                self.current_index = i + 1
                break

        if target is None:
            return "none"

        # 時間差で判定
        result = judge_timing(song_time, target.time)

        # スコア処理
        self.apply_score(result)

        # ロングノーツなら holding 開始
        if target.is_long:
            target.holding = True
            target.head_judged = True
        else:
            target.finished = True

        # エフェクト
        spawn_hit_effect(target.lane, result)

        return result

    # ============================================================
    # ロングノーツのキー離し判定（テール判定）
    # ============================================================

    def release_judge(self, lane: int, song_time: float):
        """
        キー離し時にロングノーツのテール判定を行う
        """

        for n in self.notes:
            if not n.is_long:
                continue
            if n.lane != lane:
                continue
            if not n.holding:
                continue
            if n.finished:
                continue

            # テール位置で判定
            dist = abs(n.tail_y - JUDGE_LINE)

            perfect_w = JUDGE_WINDOW["PERFECT"] / 1000.0
            great_w = JUDGE_WINDOW["GREAT"] / 1000.0
            good_w = JUDGE_WINDOW["GOOD"] / 1000.0

            if dist <= perfect_w * 900:
                result = "perfect"
            elif dist <= great_w * 900:
                result = "great"
            elif dist <= good_w * 900:
                result = "good"
            else:
                result = "miss"

            self.apply_score(result)

            n.finished = True
            n.holding = False

            spawn_hit_effect(n.lane, result)
            return result

        return "none"

    # ============================================================
    # スコア処理（商用品質）
    # ============================================================

    def apply_score(self, result: str):
        if result == "perfect":
            self.score += int(SCORE_PERFECT * (COMBO_MULTIPLIER**self.combo))
            self.combo += 1
            self.perfect += 1

        elif result == "great":
            self.score += int(SCORE_GREAT * (COMBO_MULTIPLIER**self.combo))
            self.combo += 1
            self.great += 1

        elif result == "good":
            self.score += int(SCORE_GOOD * (COMBO_MULTIPLIER**self.combo))
            self.combo += 1
            self.good += 1

        elif result == "miss":
            self.score += SCORE_MISS
            self.combo = 0
            self.miss += 1

        self.max_combo = max(self.max_combo, self.combo)

    # ============================================================
    # 自動ミス判定（画面外）
    # ============================================================

    def auto_miss_check(self):
        for n in self.notes:
            if n.finished:
                continue

            # ショートノーツ：頭が画面外
            if not n.is_long and n.head_y > 900:
                self.apply_score("miss")
                n.finished = True

            # ロングノーツ：テールが画面外
            if n.is_long and n.tail_y > 900:
                self.apply_score("miss")
                n.finished = True

    # ============================================================
    # ゲーム終了判定
    # ============================================================

    def is_finished(self):
        return all(n.finished for n in self.notes)
