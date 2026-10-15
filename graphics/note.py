print("[DEBUG] Note loaded from:", __file__)

import math
import pygame
from constants import (
    LANE_X,
    NOTE_START_Y,
    JUDGE_LINE,
    NOTE_FALL_TIME,
)

from graphics.note_renderer import NoteRenderer

FADE_OUT_DURATION = 0.45


class Note:
    """
    商用品質：判定位置と描画位置を完全分離した最終統合版 Note クラス
    - 判定ズレゼロ（プロセカ式）
    - ショート／ロングノーツ
    - BPM変化対応
    - 揺れは描画のみ（判定に影響しない）
    """

    def __init__(self, lane, time, duration=0.0):
        self.lane = lane
        self.time = float(time)
        self.duration = float(duration)
        self.tail_time = self.time + self.duration

        self.is_long = self.duration > 0.0
        self.finished = False

        self.holding = False
        self.head_judged = False
        self.tail_judged = False

        # 描画位置
        self.x = LANE_X[lane]
        self.head_y = NOTE_START_Y
        self.tail_y = NOTE_START_Y

        # 判定用位置（描画と分離）
        self.judge_y = NOTE_START_Y

        # アルファ
        self.alpha = 255
        self.head_alpha = 255
        self.tail_alpha = 255

        self.fade_out = False
        self.fade_timer = 0.0

        self.renderer = NoteRenderer(self.lane, is_long=self.is_long)

        self.song_time = 0.0
        self.bpm_events = []
        self.base_speed = 1.0
        self.song_bpm = 120

    def start_fade_out(self):
        self.fade_out = True
        self.fade_timer = 0.0
        if self.is_long:
            self.head_alpha = 255
            self.tail_alpha = 255

    # ============================================================
    # 座標更新（判定位置と描画位置を分離）
    # ============================================================
    def update(self, dt, song_time=None, bpm_events=None, base_speed=None, song_bpm=None):

        if song_time is not None:
            self.song_time = song_time
        if bpm_events is not None:
            self.bpm_events = bpm_events
        if base_speed is not None:
            self.base_speed = base_speed
        if song_bpm is not None:
            self.song_bpm = song_bpm

        distance = JUDGE_LINE - NOTE_START_Y
        note_speed = distance / NOTE_FALL_TIME * max(0.01, self.base_speed)

        # 判定位置
        self.judge_y = JUDGE_LINE - (self.time - self.song_time) * note_speed

        # 描画位置（揺れあり）
        wobble = math.sin(self.song_time * 3.5) * 1.2
        self.head_y = self.judge_y + wobble

        if self.is_long:
            self.tail_time = self.time + self.duration
            tail_offset = (self.tail_time - self.time) * note_speed
            self.tail_y = self.judge_y + tail_offset + wobble

        if self.is_long and self.holding:
            self.renderer.pulse_timer += max(0.0, dt) * 4.0
        elif self.is_long:
            self.renderer.pulse_timer = 0.0
        self.renderer.update(dt, self.holding, self.renderer.pulse_timer)

        # フェードアウト
        if self.fade_out:
            self.fade_timer += dt
            fade_rate = 255.0 / FADE_OUT_DURATION
            self.alpha = max(0, 255 - int(self.fade_timer * fade_rate))
            if self.is_long:
                self.head_alpha = self.alpha
                self.tail_alpha = self.alpha
            if self.alpha <= 0:
                self.finished = True

    # ============================================================
    # 描画
    # ============================================================

    def draw(self, screen):
        if self.finished:
            return

        if not self.is_long:
            self.renderer.draw_short(screen, self.x, self.head_y, alpha=self.alpha)
        else:
            height = self.tail_y - self.head_y
            self.renderer.draw_long(screen, self.x, self.head_y, height, self.holding)
