import pygame
import time

from ui.base_screen import BaseScreen
from graphics.effects.effect_manager import EffectManager
from graphics.judge_text_anim import JudgeTextAnim
from .draw import draw_gameplay
from .event import handle_gameplay_event
from .update import update_gameplay
from .effects import spawn_hit_effect


class GameplayScreen(BaseScreen):

    OFFSCREEN_MARGIN = 200

    def __init__(self, manager, args, logic=None):
        """
        args = {
            "song": Song,
            "difficulty": "easy" | "normal" | "hard" | "expert"
        }
        """
        super().__init__(manager)

        # 曲・難易度
        self.song = args["song"]
        raw_diff = args.get("difficulty", getattr(self.song, "difficulty", "normal"))
        self.difficulty = str(raw_diff).lower()
        self.song.difficulty = self.difficulty

        # 難易度別に譜面再生成
        try:
            from chart.generator.auto_chart_generator import AutoChartGenerator
            generator = AutoChartGenerator(self.song.audio_analyzer, self.difficulty)
            self.song.chart = generator.generate()
            self.song.build_notes()
        except Exception as e:
            print("[GameplayScreen] Chart regeneration failed:", e)

        # 設定
        settings = getattr(manager, "settings", {}) or {}
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

        # 曲再生開始
        self.music_start_time = time.perf_counter()
        try:
            music_file = getattr(self.song, "audio_file", None)
            if music_file:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play()
                self.music_start_time = time.perf_counter()
        except Exception:
            self.music_start_time = time.perf_counter()

        self.start_time = self.music_start_time

        from constants import JUDGE_LINE
        self.judge_line_y = JUDGE_LINE
        self.song_time = 0.0

        # レーン位置
        try:
            from constants import LANE_X, WIDTH, LANES
            self.lane_x = LANE_X or [i * (WIDTH // max(1, LANES)) for i in range(LANES)]
        except ImportError:
            self.lane_x = [i * 100 for i in range(4)]

        # キー設定
        keymap = settings.get("key_config", {}) or {}
        default_keys = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
        arrow_keys = [pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT]

        self.lane_keys = [
            [
                default_keys[lane],
                arrow_keys[lane],
                keymap.get(f"Lane {lane + 1}"),
            ]
            for lane in range(4)
        ]

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

    def get_song_time(self):
        try:
            position_ms = pygame.mixer.music.get_pos()
        except pygame.error:
            position_ms = -1

        if position_ms >= 0:
            return position_ms / 1000.0

        return max(0.0, time.perf_counter() - self.music_start_time)

    def update(self, dt):
        self.song_time = self.get_song_time()
        update_gameplay(self, dt)

        # レーンフラッシュ減衰（商用品質）
        self.line_flash *= 0.85
        if self.line_flash < 0.01:
            self.line_flash = 0.0

        # ノーツ削除
        if hasattr(self.logic, "notes") and isinstance(self.logic.notes, list):
            try:
                _, height = self.manager.screen.get_size()
            except Exception:
                height = 720

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
                self.logic.normalize_current_index()

    def draw(self, screen):
        draw_gameplay(self, screen)

    def handle_event(self, event):
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
