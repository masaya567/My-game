import math
import pygame
from constants import (
    LANE_X,
    NOTE_START_Y,
    BPM_SMOOTHING,
)

from graphics.note_renderer import NoteRenderer


class Note:
    """
    商用品質：NoteRenderer と完全同期した最終統合版 Note クラス
    - ショートノーツ
    - ロングノーツ（head / body / tail / shadow / beam）
    - BPM変化対応
    - speed対応
    - プロセカ級落下フィール（イージング＋揺れ＋フェードイン）
    """

    def __init__(self, lane, time, duration=0.0):
        self.lane = lane
        self.time = time
        self.duration = duration

        self.is_long = duration > 0.0
        self.finished = False
        self.holding = False
        self.head_judged = False

        # 座標
        self.head_y = NOTE_START_Y
        self.tail_y = NOTE_START_Y

        # 描画位置
        self.x = LANE_X[lane]

        # 視覚用アルファ
        self.alpha = 255

        # 描画統合クラス
        self.renderer = NoteRenderer()

    # ============================================================
    # 座標更新（BPM変化＋speed＋プロセカ級落下フィール）
    # ============================================================

    def update(self, dt, song_time, bpm_events, base_speed, song_bpm):
        # BPMスムージング（既存仕様）
        bpm = song_bpm
        for ev_time, ev_bpm in bpm_events:
            if song_time >= ev_time:
                bpm = bpm + (ev_bpm - bpm) * BPM_SMOOTHING

        # BPM連動速度
        drop_speed = base_speed * (bpm / 120.0)

        # 進行度（0〜1）※判定タイミング self.time に向かって落ちる
        progress = (song_time - self.time) * drop_speed
        progress = max(0.0, min(1.0, progress))

        # イージング（プロセカ寄りの指数カーブ）
        ease = progress**1.12

        # 微揺れ（±2px）
        wobble = math.sin(song_time * 3.5) * 2

        # 曲開始時フェードイン
        self.alpha = min(255, int(song_time * 2 * 255))

        # head の最終位置
        self.head_y = NOTE_START_Y + ease * 900 + wobble

        # ロングノーツ tail
        if self.is_long:
            end_time = self.time + self.duration

            tail_progress = (song_time - end_time) * drop_speed
            tail_progress = max(0.0, min(1.0, tail_progress))

            tail_ease = tail_progress**1.12

            self.tail_y = NOTE_START_Y + tail_ease * 900 + wobble

            # ロングノーツの波動更新（既存ロジックと同期）
            self.renderer.update_long(dt, self.holding)

    # ============================================================
    # 描画（NoteRenderer に委譲）
    # ============================================================

    def draw(self, screen):
        if self.finished:
            return

        if not self.is_long:
            self.renderer.draw_short(screen, self.x, self.head_y, alpha=self.alpha)
        else:
            self.renderer.draw_long(
                screen,
                self.x,
                self.head_y,
                self.tail_y,
                holding=self.holding,
                alpha=self.alpha,
            )
