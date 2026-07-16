import pygame
import random
import math
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, UI_COLORS, UI_SCALE
from songs.chart.chart_generator import build_notes_from_chart


class ChartPreviewScreen(BaseScreen):
    """
    商用品質：Auto Chart 譜面プレビュー画面（フル強化版）
    - ジャケット表示
    - 曲名 / 作曲者 / 難易度
    - ノーツ総数 / ロング数
    - レーン別色分けタイムライン
    - ロングノーツ長さ（レーン別高さ）
    - 密度ヒートマップ（滑らかグラデーション）
    - BPM 変化表示
    - 再生バー発光（ガウスぼかし風）
    - 背景光粒子（ジャケット色連動）
    - 曲の再生時間表示
    - Auto Chart 設定 UI（密度・ロング率）
    """

    def __init__(self, manager, song):
        super().__init__(manager)
        self.song = song

        # Auto Chart 生成
        build_notes_from_chart(self.song)

        # プレビュー用
        self.notes = self.song.notes
        self.timeline_surface = pygame.Surface((WIDTH, 140), pygame.SRCALPHA)

        # 曲の長さ（秒）
        self.song_length = getattr(song, "length", 120.0)

        # 再生バー
        self.preview_time = 0.0

        # レーン色
        self.lane_colors = [
            (255, 120, 160),
            (120, 200, 255),
            (120, 255, 160),
            (255, 220, 120),
        ]

        # BPM 変化
        self.bpm_changes = getattr(song, "bpm_changes", [])

        # ジャケット色抽出（簡易：中央ピクセル）
        jacket_img = getattr(self.song, "jacket", None)
        if jacket_img:
            w, h = jacket_img.get_size()
            center_color = jacket_img.get_at((w // 2, h // 2))
            self.particle_color = (center_color.r, center_color.g, center_color.b, 40)
        else:
            self.particle_color = (255, 255, 255, 40)

        # 背景光粒子
        self.particles = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 1.0)]
            for _ in range(40)
        ]

        # Auto Chart 設定（簡易）
        self.chart_density = 1.0  # 0.5〜1.5
        self.long_rate = 1.0  # 0.5〜1.5

        # 設定UI用ボタン領域
        self.density_rect = pygame.Rect(
            int(WIDTH * 0.1), int(HEIGHT * 0.82), int(WIDTH * 0.35), int(30 * UI_SCALE)
        )
        self.long_rect = pygame.Rect(
            int(WIDTH * 0.55), int(HEIGHT * 0.82), int(WIDTH * 0.35), int(30 * UI_SCALE)
        )

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        # 再生バー
        self.preview_time += dt * 1.0
        if self.preview_time > self.song_length:
            self.preview_time = 0.0

        # 光粒子アニメーション
        for p in self.particles:
            p[1] += p[2] * 20 * dt
            if p[1] > HEIGHT:
                p[0] = random.randint(0, WIDTH)
                p[1] = -10

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen):
        screen.fill(UI_COLORS["bg_select"])

        # ------------------------------------------------------------
        # 背景光粒子（ジャケット色連動）
        # ------------------------------------------------------------
        for x, y, s in self.particles:
            pygame.draw.circle(screen, self.particle_color, (int(x), int(y)), int(3 * s))

        # タイトル
        self.center_text(
            screen,
            "CHART PREVIEW",
            size=48,
            y=int(60 * UI_SCALE),
            color=UI_COLORS["title_glow"],
            weight="bold",
        )

        # ------------------------------------------------------------
        # ジャケット画像
        # ------------------------------------------------------------
        jacket_img = getattr(self.song, "jacket", None)
        if jacket_img:
            jacket_size = int(200 * UI_SCALE)
            jacket = pygame.transform.smoothscale(jacket_img, (jacket_size, jacket_size))
            rect = jacket.get_rect(center=(WIDTH // 2, int(200 * UI_SCALE)))
            screen.blit(jacket, rect)

        # ------------------------------------------------------------
        # 曲情報
        # ------------------------------------------------------------
        self.center_text(
            screen, self.song.title, 40, int(340 * UI_SCALE), UI_COLORS["text_primary"], "bold"
        )
        artist = getattr(self.song, "artist", "Unknown Artist")
        self.center_text(screen, artist, 28, int(380 * UI_SCALE), UI_COLORS["text_secondary"])
        self.center_text(
            screen,
            f"Difficulty: {self.song.chart_mode}",
            26,
            int(420 * UI_SCALE),
            UI_COLORS["text_secondary"],
        )

        # ------------------------------------------------------------
        # ノーツ統計
        # ------------------------------------------------------------
        total_notes = len(self.notes)
        long_notes = sum(1 for n in self.notes if n["type"] == "long")
        self.center_text(
            screen,
            f"Notes: {total_notes}   Long: {long_notes}",
            24,
            int(460 * UI_SCALE),
            UI_COLORS["text_secondary"],
        )

        # ------------------------------------------------------------
        # タイムライン（レーン別色分け + ロングノーツ長さ・レーン別高さ）
        # ------------------------------------------------------------
        self.timeline_surface.fill((0, 0, 0, 0))

        if self.notes:
            max_time = max(n["time"] for n in self.notes)

            for n in self.notes:
                x = int((n["time"] / max_time) * WIDTH)
                lane = n["lane"]
                color = self.lane_colors[lane]

                # TAP
                if n["type"] == "tap":
                    pygame.draw.line(self.timeline_surface, color, (x, 0), (x, 140), 3)

                # LONG
                else:
                    end_x = int((n["end_time"] / max_time) * WIDTH)
                    y_offset = 20 * lane  # レーンごとに高さを変える
                    pygame.draw.line(self.timeline_surface, color, (x, 0), (x, 140), 3)
                    pygame.draw.rect(
                        self.timeline_surface,
                        (*color, 140),
                        (x, 20 + y_offset, max(4, end_x - x), 12),
                    )

        screen.blit(self.timeline_surface, (0, int(520 * UI_SCALE)))

        # ------------------------------------------------------------
        # BPM 変化表示
        # ------------------------------------------------------------
        for bpm_time, bpm_value in self.bpm_changes:
            x = int((bpm_time / self.song_length) * WIDTH)
            pygame.draw.line(
                screen, (120, 200, 255), (x, int(520 * UI_SCALE)), (x, int(660 * UI_SCALE)), 2
            )

        # ------------------------------------------------------------
        # 密度ヒートマップ（滑らかグラデーション）
        # ------------------------------------------------------------
        bins = 20
        density = [0] * bins

        for n in self.notes:
            idx = int((n["time"] / self.song_length) * bins)
            idx = min(idx, bins - 1)
            density[idx] += 1

        max_d = max(density) if density else 1

        for i, d in enumerate(density):
            x = int((i / bins) * WIDTH)
            w = int(WIDTH / bins)

            ratio = d / max_d  # 0〜1

            # HSV風グラデーション（青→黄→赤）
            # h: 0.66 (青) → 0.0 (赤)
            h = 0.66 * (1 - ratio)
            s = 1.0
            v = 0.9

            r, g, b = self._hsv_to_rgb(h, s, v)
            color = (int(r), int(g), int(b))

            pygame.draw.rect(screen, color, (x, int(670 * UI_SCALE), w, int(20 * UI_SCALE)))

        # ------------------------------------------------------------
        # 再生バー（ガウスぼかし風発光）
        # ------------------------------------------------------------
        bar_x = int((self.preview_time / self.song_length) * WIDTH)

        # 中心線
        pygame.draw.line(
            screen, (255, 255, 255), (bar_x, int(520 * UI_SCALE)), (bar_x, int(660 * UI_SCALE)), 3
        )

        # 残像（指数減衰）
        for i in range(1, 6):
            alpha = int(180 * (0.6**i))
            offset = i * 5
            color = (255, 255, 255, alpha)
            pygame.draw.line(
                screen,
                color,
                (bar_x - offset, int(520 * UI_SCALE)),
                (bar_x - offset, int(660 * UI_SCALE)),
                2,
            )

        # ------------------------------------------------------------
        # 曲の再生時間表示
        # ------------------------------------------------------------
        current_sec = int(self.preview_time)
        total_sec = int(self.song_length)
        time_str = f"{current_sec // 60:02d}:{current_sec % 60:02d} / {total_sec // 60:02d}:{total_sec % 60:02d}"
        self.center_text(
            screen, time_str, 22, int(HEIGHT - 120 * UI_SCALE), UI_COLORS["text_secondary"]
        )

        # ------------------------------------------------------------
        # Auto Chart 設定 UI（密度・ロング率）
        # ------------------------------------------------------------
        pygame.draw.rect(screen, (30, 30, 30), self.density_rect, border_radius=6)
        pygame.draw.rect(screen, (30, 30, 30), self.long_rect, border_radius=6)

        # スライダー風バー
        self._draw_slider(screen, self.density_rect, self.chart_density, "Density")
        self._draw_slider(screen, self.long_rect, self.long_rate, "Long Rate")

        # 操作説明
        self.center_text(
            screen,
            "Enter: Start   Esc: Back   Click sliders to adjust Auto Chart",
            20,
            int(HEIGHT - 60 * UI_SCALE),
            UI_COLORS["text_secondary"],
        )

        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:
                self.play_se("se_decide")
                # 設定値を song に反映（chart_generator 側で使う前提）
                self.song.auto_density = self.chart_density
                self.song.auto_long_rate = self.long_rate
                self.request_transition(("gameplay", self.song))

            elif event.key == pygame.K_ESCAPE:
                self.play_se("se_back")
                self.request_transition("difficulty")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Density スライダー
            if self.density_rect.collidepoint(mx, my):
                ratio = (mx - self.density_rect.x) / self.density_rect.width
                self.chart_density = 0.5 + ratio * 1.0  # 0.5〜1.5

            # Long Rate スライダー
            if self.long_rect.collidepoint(mx, my):
                ratio = (mx - self.long_rect.x) / self.long_rect.width
                self.long_rate = 0.5 + ratio * 1.0  # 0.5〜1.5

    # ============================================================
    # 補助メソッド
    # ============================================================

    def _hsv_to_rgb(self, h, s, v):
        """0〜1のHSVをRGBに変換"""
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        i = i % 6

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return r * 255, g * 255, b * 255

    def _draw_slider(self, screen, rect, value, label):
        # 枠
        pygame.draw.rect(screen, (80, 80, 80), rect, 2, border_radius=6)

        # バー
        ratio = (value - 0.5) / 1.0  # 0〜1
        knob_x = rect.x + int(rect.width * ratio)
        pygame.draw.line(
            screen, (180, 180, 180), (rect.x + 8, rect.centery), (rect.right - 8, rect.centery), 3
        )
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, rect.centery), 7)

        # ラベル
        font = self.res.get_font(18, weight="medium")
        text = font.render(f"{label}: {value:.2f}", True, UI_COLORS["text_secondary"])
        screen.blit(text, (rect.x, rect.y - 22))
