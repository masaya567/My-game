import pygame
import math
from constants import LANE_X, NOTE_START_Y, JUDGE_LINE
from graphics.note_renderer import NoteRenderer

FADE_OUT_DURATION = 0.45


class Note:
    """
    商用品質：描画キャッシュ時代の最終統合版 Note クラス
    - 位置計算は GameLogic が担当（Note.update は軽量化）
    - 描画は draw_gameplay が担当（Note.draw は廃止）
    - 判定位置と描画位置は完全分離
    """

    def __init__(self, lane, time, duration=0.0):
        self.id = id(self)
        self.lane = lane
        self.time = float(time)
        self.duration = float(duration)
        self.tail_time = self.time + self.duration

        self.is_long = self.duration > 0.0
        self.finished = False

        self.holding = False
        self.head_judged = False
        self.tail_judged = False

        # 描画位置（GameLogic が毎フレーム更新）
        self.x = LANE_X[lane]
        self.head_y = NOTE_START_Y
        self.tail_y = NOTE_START_Y

        # 判定位置（GameLogic が更新）
        self.judge_y = NOTE_START_Y

        # アルファ
        self.alpha = 255
        self.head_alpha = 255
        self.tail_alpha = 255

        self.fade_out = False
        self.fade_timer = 0.0

        # レンダラー（pulse などの視覚効果のみ）
        self.renderer = NoteRenderer(self.lane, is_long=self.is_long)

        # 曲同期情報（GameLogic がセット）
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
    # 軽量 update（位置計算は GameLogic が担当）
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

        # pulse（視覚効果のみ）
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


