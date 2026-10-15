import pygame
import random
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE
from chart.generator.auto_chart_generator import AutoChartGenerator


class ChartPreviewScreen(BaseScreen):
    """
    商用品質：Auto Chart 譜面プレビュー画面（タイムライン + スクロール譜面）
    """

    def __init__(self, manager, args):
        super().__init__(manager)

        # ★ dict から受け取る（重要）
        self.song = args["song"]
        self.difficulty = args.get("difficulty", getattr(self.song, "difficulty", "normal"))

        # Auto Chart 生成（難易度反映）
        auto_chart_generator = AutoChartGenerator(
            self.song.audio_analyzer,
            difficulty=self.difficulty
        )
        self.notes = auto_chart_generator.generate() or []

        # タイムライン用サーフェス
        self.timeline_surface = pygame.Surface((WIDTH, 140), pygame.SRCALPHA)

        # 曲の長さ
        self.song_length = getattr(self.song, "length", 120.0)
        if self.song_length <= 0:
            self.song_length = 1.0

        # 再生バー
        self.preview_time = 0.0

        # レーン色
        self.lane_colors = [
            (255, 120, 160),
            (120, 200, 255),
            (120, 255, 160),
            (255, 220, 120),
        ]

        # BPM変化（★修正）
        self.bpm_changes = getattr(self.song, "bpm_changes", [])

        # 背景光粒子
        self.particles = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 1.0)]
            for _ in range(40)
        ]

        # UIスライダー
        self.chart_density = 1.0
        self.long_rate = 1.0

        self.density_rect = pygame.Rect(
            int(WIDTH * 0.1), int(HEIGHT * 0.78), int(WIDTH * 0.35), int(24 * UI_SCALE)
        )
        self.long_rect = pygame.Rect(
            int(WIDTH * 0.55), int(HEIGHT * 0.78), int(WIDTH * 0.35), int(24 * UI_SCALE)
        )

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        self.preview_time += dt
        if self.preview_time > self.song_length:
            self.preview_time = 0.0

        for p in self.particles:
            p[1] += p[2] * 20 * dt
            if p[1] > HEIGHT:
                p[0] = random.randint(0, WIDTH)
                p[1] = -10

    # ============================================================
    # スクロール譜面描画
    # ============================================================

    def draw_scroll_notes(self, screen):
        judge_y = int(HEIGHT * 0.72)
        scroll_speed = 320

        pygame.draw.line(screen, (255, 255, 255), (0, judge_y), (WIDTH, judge_y), 3)

        for n in self.notes:
            dt = n["time"] - self.preview_time
            y = judge_y - dt * scroll_speed

            if y < -80 or y > HEIGHT + 80:
                continue

            lane_x = int(WIDTH * 0.25 + n["lane"] * 80)
            color = self.lane_colors[n["lane"]]

            if n["type"] == "tap":
                pygame.draw.circle(screen, color, (lane_x, int(y)), 12)
            else:
                end_dt = n["end_time"] - self.preview_time
                end_y = judge_y - end_dt * scroll_speed
                rect_h = int(y - end_y)
                if rect_h > 0:
                    long_surf = pygame.Surface((20, rect_h), pygame.SRCALPHA)
                    long_surf.fill((*color, 180))
                    screen.blit(long_surf, (lane_x - 10, int(end_y)))

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen):
        screen.fill(UI_COLORS["bg_select"])

        # 背景光粒子
        for x, y, s in self.particles:
            glow = pygame.Surface((int(6 * s), int(6 * s)), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 255, 40),
                               (glow.get_width() // 2, glow.get_height() // 2),
                               int(3 * s))
            screen.blit(glow, (int(x) - glow.get_width() // 2, int(y) - glow.get_height() // 2))

        self.center_text(screen, "譜面プレビュー", 34, int(40 * UI_SCALE),
                         UI_COLORS["title_glow"], "bold")

        self.center_text(screen, self.song.title, 24, int(220 * UI_SCALE),
                         UI_COLORS["text_primary"], "bold")

        self.draw_scroll_notes(screen)
        self.draw_timeline(screen)

        current_sec = int(self.preview_time)
        total_sec = int(self.song_length)
        time_str = f"{current_sec//60:02d}:{current_sec%60:02d} / {total_sec//60:02d}:{total_sec%60:02d}"

        self.center_text(screen, time_str, 18, int(HEIGHT - 100 * UI_SCALE),
                         UI_COLORS["text_secondary"])

        pygame.draw.rect(screen, (30, 30, 30), self.density_rect, border_radius=6)
        pygame.draw.rect(screen, (30, 30, 30), self.long_rect, border_radius=6)

        self._draw_slider(screen, self.density_rect, self.chart_density, "Density")
        self._draw_slider(screen, self.long_rect, self.long_rate, "Long Rate")

        self.center_text(screen, "Enter: 開始   Esc: 戻る", 16,
                         int(HEIGHT - 55 * UI_SCALE), UI_COLORS["text_secondary"])

        self.draw_fade(screen)

    # ============================================================
    # タイムライン描画
    # ============================================================

    def draw_timeline(self, screen):
        self.timeline_surface.fill((0, 0, 0, 0))

        if self.notes:
            max_time = max(n["time"] for n in self.notes)
            if max_time <= 0:
                max_time = 1.0

            for n in self.notes:
                x = int((n["time"] / max_time) * WIDTH)
                lane = n["lane"]
                color = self.lane_colors[lane]

                pygame.draw.line(self.timeline_surface, color, (x, 0), (x, 140), 3)

                if n["type"] != "tap":
                    end_x = int((n["end_time"] / max_time) * WIDTH)
                    y_offset = 20 * lane
                    rect_w = max(4, end_x - x)
                    long_surf = pygame.Surface((rect_w, 12), pygame.SRCALPHA)
                    long_surf.fill((*color, 140))
                    self.timeline_surface.blit(long_surf, (x, 20 + y_offset))

        screen.blit(self.timeline_surface, (0, int(330 * UI_SCALE)))

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.play_se("se_decide")

                self.song.auto_density = self.chart_density
                self.song.auto_long_rate = self.long_rate

                # ★ dict で渡す（重要）
                self.request_transition(("gameplay", {
                    "song": self.song,
                    "difficulty": self.difficulty
                }))

            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")

                # ★ DifficultyScreen は Song を直接受け取る
                self.request_transition(("difficulty", self.song))

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.density_rect.collidepoint(mx, my):
                ratio = (mx - self.density_rect.x) / self.density_rect.width
                self.chart_density = 0.5 + ratio * 1.0

            if self.long_rect.collidepoint(mx, my):
                ratio = (mx - self.long_rect.x) / self.long_rect.width
                self.long_rate = 0.5 + ratio * 1.0

    # ============================================================
    # スライダー描画
    # ============================================================

    def _draw_slider(self, screen, rect, value, label):
        pygame.draw.rect(screen, (80, 80, 80), rect, 2, border_radius=6)
        ratio = (value - 0.5) / 1.0
        knob_x = rect.x + int(rect.width * ratio)

        pygame.draw.line(screen, (180, 180, 180),
                         (rect.x + 8, rect.centery),
                         (rect.right - 8, rect.centery), 3)

        pygame.draw.circle(screen, (255, 255, 255), (knob_x, rect.centery), 7)

        font = self.res.get_font(18, weight="medium")
        text = font.render(f"{label}: {value:.2f}", True, UI_COLORS["text_secondary"])
        screen.blit(text, (rect.x, rect.y - 22))
