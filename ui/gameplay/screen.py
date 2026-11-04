import sys
import os
import pygame
import pygame.gfxdraw
import time

from ui.base_screen import BaseScreen
from graphics.effects.effect_manager import EffectManager
from graphics.judge_text_anim import JudgeTextAnim
from .draw import draw_gameplay
from .event import handle_gameplay_event
from .update import update_gameplay
from .effects import spawn_hit_effect

from constants import (
    JUDGE_LINE,
    WIDTH,
    HEIGHT,
    LANE_WIDTH,
    NOTE_HEIGHT,
    UI_SCALE,
    JUDGE_LINE_WIDTH,
)

# アプリ化対応：ベースディレクトリ／アセット／データパス
BASE_DIR = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")


class GameplayScreen(BaseScreen):

    OFFSCREEN_MARGIN = 200

    def __init__(self, manager, args, logic=None):
        print("[DEBUG] Gameplay args =", args)

        super().__init__(manager)

        # 曲・難易度
        self.song = args["song"]
        raw_diff = args.get("difficulty", getattr(self.song, "difficulty", "normal"))
        self.difficulty = str(raw_diff).lower()
        self.song.difficulty = self.difficulty

        # 難易度別に譜面再生成
        try:
            chart_difficulty = str(getattr(self.song, "chart_difficulty", "")).lower()
            if chart_difficulty != self.difficulty or not getattr(self.song, "chart", None):
                from chart.generator.auto_chart_generator import AutoChartGenerator
                generator = AutoChartGenerator(self.song.audio_analyzer, self.difficulty)
                self.song.chart = generator.generate() or []
                self.song.chart_difficulty = self.difficulty
            self.song.build_notes()
        except Exception as e:
            print("[GameplayScreen] Chart regeneration failed:", e)

        # 設定（破損対策込み）
        try:
            settings = getattr(manager, "settings", {}) or {}
        except Exception:
            settings = {}
        self.speed = settings.get("note_speed", 1.0)

        # GameLogic 初期化
        if logic is None:
            from game.game_logic import GameLogic

            notes = getattr(self.song, "notes", [])
            self.logic = GameLogic(
                notes=notes,
                bpm_events=getattr(self.song, "bpm_events", []),
                song_bpm=getattr(self.song, "bpm", 120),
                difficulty=self.difficulty,
                base_speed=self.speed,
            )
        else:
            self.logic = logic

        # 曲再生開始（アプリ化対応パス）
        self.music_start_time = time.perf_counter()
        try:
            music_file = getattr(self.song, "audio_file", None)
            if music_file:
                music_path = os.path.join(ASSETS_DIR, "songs", music_file)
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play()
                self.music_start_time = time.perf_counter()
        except Exception:
            self.music_start_time = time.perf_counter()

        self.start_time = self.music_start_time

        self.judge_line_y = JUDGE_LINE
        self.song_time = 0.0

        # レーン位置
        try:
            from constants import LANE_X, LANES
            self.lane_x = LANE_X or [i * (WIDTH // max(1, LANES)) for i in range(LANES)]
        except ImportError:
            self.lane_x = [i * 100 for i in range(4)]

        # キー設定
        keymap = settings.get("key_config", {}) or {}
        default_keys = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
        arrow_keys = [pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT]

        self.lane_keys = []
        for lane in range(4):
            custom_key = keymap.get(f"Lane {lane + 1}")
            if isinstance(custom_key, str):
                custom_key = pygame.key.key_code(custom_key)

            lane_keys = [default_keys[lane], arrow_keys[lane], custom_key]
            self.lane_keys.append(list(dict.fromkeys(key for key in lane_keys if key is not None)))

        self.key_pressed = [False, False, False, False]
        self.pending_key_down = {}
        self.pending_key_up = {}

        # エフェクト・判定テキスト
        self.effect_manager = EffectManager()
        self.judge_text_anim = JudgeTextAnim(self.res)
        self.effect_manager.logic = self.logic

        # 演出パラメータ
        self.line_wave = 0.0
        self.line_wave_strength = 0.0
        self.line_flash = 0.0
        self.line_flash_lane = None

        self.bg_pulse = 0.0
        self.bg_pulse_strength = 0.0

        self.perfect_chain = 0
        self.fever_strength = 0.0
        self.fever_phase = 0.0

        self.logic.last_judged_lane = None

        self.combo_flash = 0.0
        self.combo_flash_phase = 0.0

        # 判定テキスト Surface（UI_SCALE 対応）
        judge_font_size = int(48 * UI_SCALE)
        self.judge_surfaces = {
            "perfect": self.get_text("Perfect", judge_font_size, (255, 255, 255)),
            "great": self.get_text("Great", judge_font_size, (255, 255, 255)),
            "good": self.get_text("Good", judge_font_size, (255, 255, 255)),
            "miss": self.get_text("Miss", judge_font_size, (255, 255, 255)),
        }

        # レーン背景
        self.lane_bg_surface = pygame.Surface((WIDTH, HEIGHT))
        self.lane_bg_surface.fill((15, 15, 20))

        # 判定ライン（UI_SCALE 対応）
        self.judge_line_surface = pygame.Surface((WIDTH, JUDGE_LINE_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(
            self.judge_line_surface,
            (255, 255, 255, 220),
            self.judge_line_surface.get_rect(),
            border_radius=2,
        )

        # レーンフラッシュ
        self.lane_flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # ==== ノーツ Surface（UI_SCALE 対応） ====
        note_w = int(LANE_WIDTH * UI_SCALE)
        note_h = NOTE_HEIGHT

        self.short_body, self.short_glow = self.create_short_note_surface(note_w, note_h)
        self.long_head, self.long_body, self.long_tail = self.create_long_note_surfaces(note_w)

    # ショートノーツ Surface
    def create_short_note_surface(self, width, height):
        body = pygame.Surface((width, height), pygame.SRCALPHA)
        for row in range(height):
            ratio = row / max(1, height)
            channel = int(255 * (0.85 + 0.15 * (1 - ratio)))
            pygame.draw.line(body, (255, channel, channel), (0, row), (width - 1, row))

        glow = pygame.Surface((width + int(20 * UI_SCALE), height + int(20 * UI_SCALE)), pygame.SRCALPHA)
        cx = glow.get_width() // 2
        cy = glow.get_height() // 2
        rx = glow.get_width() // 2
        ry = glow.get_height() // 2

        pygame.gfxdraw.filled_ellipse(glow, cx, cy, rx, ry, (255, 255, 255, 255))
        pygame.gfxdraw.aaellipse(glow, cx, cy, rx, ry, (255, 255, 255, 255))

        return body, glow

    # ロングノーツ Surface（UI_SCALE 対応）
    def create_long_note_surfaces(self, width):
        head_h = int(24 * UI_SCALE)
        tail_h = int(24 * UI_SCALE)
        body_h = int(200 * UI_SCALE)

        head = pygame.Surface((width, head_h), pygame.SRCALPHA)
        pygame.draw.ellipse(head, (180, 220, 255), (0, 0, width, head_h))
        pygame.draw.ellipse(head, (255, 255, 255), (4, 4, width - 8, head_h - 8))

        body = pygame.Surface((width, body_h), pygame.SRCALPHA)
        for y in range(body_h):
            ratio = y / body_h
            color = (
                int(170 + 60 * ratio),
                int(200 + 40 * ratio),
                255,
                int(180 + 40 * ratio),
            )
            pygame.draw.line(body, color, (0, y), (width - 1, y))

        pygame.draw.line(body, (255, 255, 255), (2, 0), (2, body_h), 2)
        pygame.draw.line(body, (255, 255, 255), (width - 4, 0), (width - 4, body_h), 2)

        core_rect = pygame.Rect(width // 2 - 3, 10, 6, body_h - 20)
        pygame.draw.rect(body, (255, 255, 255), core_rect, border_radius=3)

        tail = pygame.Surface((width, tail_h), pygame.SRCALPHA)
        pygame.draw.ellipse(tail, (180, 220, 255), (0, 0, width, tail_h))
        pygame.draw.ellipse(tail, (255, 255, 255), (4, 4, width - 8, tail_h - 8))

        return head, body, tail

    # 現在の曲時間
    def get_song_time(self):
        try:
            position_ms = pygame.mixer.music.get_pos()
        except pygame.error:
            position_ms = -1

        if position_ms >= 0:
            return position_ms / 1000.0

        return max(0.0, time.perf_counter() - self.music_start_time)

    # 中断／終了時にリザルトへ遷移
    def go_result(self):
        score = getattr(self.logic, "score", 0)
        max_combo = getattr(self.logic, "max_combo", 0)

        perfect = getattr(self.logic, "perfect_count", getattr(self.logic, "perfect", 0))
        great = getattr(self.logic, "great_count", getattr(self.logic, "great", 0))
        good = getattr(self.logic, "good_count", getattr(self.logic, "good", 0))
        miss = getattr(self.logic, "miss_count", getattr(self.logic, "miss", 0))

        pygame.mixer.music.stop()

        self.manager.request_transition(
            (
                "result",
                {
                    "score": score,
                    "max_combo": max_combo,
                    "perfect": perfect,
                    "great": great,
                    "good": good,
                    "miss": miss,
                    "song": self.song,
                    "logic": self.logic,
                },
            )
        )

    def update(self, dt):
        self.song_time = self.get_song_time()
        update_gameplay(self, dt)

        self.line_flash *= 0.85
        if self.line_flash < 0.01:
            self.line_flash = 0.0

        if hasattr(self.logic, "notes") and isinstance(self.logic.notes, list):
            try:
                _, height = self.manager.screen.get_size()
            except Exception:
                height = HEIGHT

            offscreen_threshold = height + self.OFFSCREEN_MARGIN

            new_notes = []
            for note in self.logic.notes:
                if getattr(note, "finished", False):
                    continue

                if getattr(note, "is_long", False):
                    head_y = getattr(note, "head_y", None)
                    tail_y = getattr(note, "tail_y", None)
                    if head_y is not None and tail_y is not None:
                        if head_y > offscreen_threshold and tail_y > offscreen_threshold:
                            continue
                else:
                    head_y = getattr(note, "head_y", None)
                    if head_y is not None and head_y > offscreen_threshold:
                        continue

                new_notes.append(note)

            self.logic.notes = new_notes
            if hasattr(self.logic, "normalize_current_index"):
                for lane in range(4):
                    self.logic.normalize_current_index(lane)

        song_length = getattr(self.song, "length", 0.0)
        if song_length > 0 and self.song_time >= song_length - 0.3:
            self.go_result()

    def draw(self, screen):
        draw_gameplay(self, screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            self.go_result()
            return

        handle_gameplay_event(self, event)

    def spawn_hit_effect(self, lane, judge_text):
        sound_name = {
            "perfect": "perfect",
            "great": "great",
            "good": "good",
            "miss": "miss",
        }.get(judge_text.lower())
        if sound_name:
            self.play_se(sound_name)

        spawn_hit_effect(self, lane, judge_text)
