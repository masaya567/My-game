"""
ゲームで使う全クラス定義

このモジュールは、Piano Tiles ゲームの全ゲームオブジェクトと
エフェクトを実装しています。型ヒントとドキュメント文字列を
完全装備しているプロフェッショナル仕様です。
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Tuple

import pygame

from constants import *


# ========================================
# Note クラス（光る処理つき）
# ========================================
class Note:
    """
    ゲーム内のノーツ（音符）クラス

    Short ノーツと Long ノーツの両方を処理します。
    BPM連動で速度が変わるプロセカ式対応です。
    """

    short_surface: Optional[pygame.Surface] = None

    def __init__(self, lane: int, start_time: float, end_time: float, speed: float) -> None:
        """
        ノーツを初期化

        Args:
            lane: レーン番号 (0-3)
            start_time: ノーツ出現時刻（秒）
            end_time: ノーツ終了時刻（秒）（long ノーツの場合）
            speed: 基本速度（ピクセル/秒）
        """
        # キャッシュ生成（最初の1回だけ）
        if Note.short_surface is None:
            Note.short_surface = pygame.Surface((LANE_WIDTH, NOTE_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(Note.short_surface, (0, 200, 255), (0, 0, LANE_WIDTH, NOTE_HEIGHT))
            pygame.draw.rect(
                Note.short_surface, (255, 255, 255), (0, 0, LANE_WIDTH, NOTE_HEIGHT), 3
            )

        self.lane: int = lane
        self.start_time: float = start_time
        self.end_time: float = end_time
        self.speed: float = speed

        # 位置情報
        self.y: float = -NOTE_HEIGHT
        self.head_y: float = self.y
        self.tail_y: float = self.y + NOTE_HEIGHT

        # ノーツ種別
        self.is_long: bool = (end_time - start_time) >= 0.2
        self.length_px: float = NOTE_HEIGHT

        # 状態管理
        self.finished: bool = False
        self.holding: bool = False
        self.active: bool = False
        self.flash: bool = False
        self.flash_timer: float = 0

    def update(
        self,
        dt: float,
        t: float,
        bpm_events: List[Dict[str, Any]],
        base_speed: float,
        default_bpm: float,
    ) -> None:
        """
        ノーツを更新

        Args:
            dt: デルタ時間（秒）
            t: 現在時刻（秒）
            bpm_events: BPM変化イベント
            base_speed: 基本速度
            default_bpm: デフォルト BPM
        """
        if t < self.start_time:
            return

        # 現在の BPM を取得
        bpm = default_bpm
        for ev in bpm_events:
            if t >= ev["time"]:
                bpm = ev["bpm"]
            else:
                break

        # BPM連動速度
        current_speed = base_speed * (bpm / 120)
        self.y += current_speed * dt
        self.head_y = self.y

        # long の長さも BPM 連動
        if self.is_long:
            duration = max(0.05, self.end_time - self.start_time)
            self.length_px = duration * current_speed
            self.tail_y = self.head_y + self.length_px
        else:
            self.length_px = NOTE_HEIGHT
            self.tail_y = self.y + NOTE_HEIGHT

        # フラッシュ処理
        if self.flash:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash = False

    def draw(self, screen: pygame.Surface, t: float) -> None:
        """
        ノーツを描画

        Args:
            screen: 描画対象のサーフェス
            t: 現在時刻（秒）
        """
        x = self.lane * LANE_WIDTH

        # 落下ゆらぎ（sin 波）
        base_wobble = math.sin(t * 12 + self.lane * 1.5) * 2
        wobble = base_wobble * (0.3 if self.holding else 1.0)
        x += wobble

        if t < self.start_time:
            return

        if not self.is_long:
            self._draw_short_note(screen, x)
        else:
            self._draw_long_note(screen, x, t)

    def _draw_short_note(self, screen: pygame.Surface, x: float) -> None:
        """Short ノーツを描画"""
        # 爆光エフェクト
        if self.flash:
            flash = pygame.Surface((LANE_WIDTH + 60, NOTE_HEIGHT + 60), pygame.SRCALPHA)
            for i in range(25):
                alpha = int(255 * (1 - i / 25) * self.flash_timer)
                pygame.draw.ellipse(
                    flash,
                    (255, 255, 255, alpha),
                    (30 - i, 30 - i, LANE_WIDTH + i * 2, NOTE_HEIGHT + i * 2),
                )
            screen.blit(flash, (x - 30, self.y - 30))

        # 発光レイヤー
        glow = pygame.Surface((LANE_WIDTH + 30, NOTE_HEIGHT + 30), pygame.SRCALPHA)
        for i in range(15):
            alpha = int(120 * (1 - i / 15))
            pygame.draw.ellipse(
                glow,
                (80, 180, 255, alpha),
                (15 - i, 15 - i, LANE_WIDTH + i * 2, NOTE_HEIGHT + i * 2),
            )
        screen.blit(glow, (x - 15, self.y - 15))

        # シャドウ
        shadow = pygame.Surface((LANE_WIDTH + 20, NOTE_HEIGHT + 20), pygame.SRCALPHA)
        for i in range(10):
            alpha = int(70 * (1 - i / 10))
            pygame.draw.ellipse(
                shadow,
                (0, 0, 0, alpha),
                (10 - i, 10 - i, LANE_WIDTH + i * 2, NOTE_HEIGHT + i * 2),
            )
        screen.blit(shadow, (x - 10, self.y - 10))

        # 本体（グラデーション）
        body = pygame.Surface((LANE_WIDTH, NOTE_HEIGHT), pygame.SRCALPHA)
        for i in range(NOTE_HEIGHT):
            c = 170 + int(60 * (i / NOTE_HEIGHT))
            pygame.draw.line(body, (0, c, 255), (0, i), (LANE_WIDTH, i))
        screen.blit(body, (x, self.y))

        # 縁取り
        pygame.draw.ellipse(screen, (255, 255, 255), (x, self.y, LANE_WIDTH, NOTE_HEIGHT), 3)

        # コア
        pygame.draw.ellipse(
            screen,
            (255, 255, 255),
            (x + LANE_WIDTH // 2 - 4, self.y + 4, 8, NOTE_HEIGHT - 8),
        )

    def _draw_long_note(self, screen: pygame.Surface, x: float, t: float) -> None:
        """Long ノーツを描画"""
        height = self.length_px
        head_y = self.head_y
        tail_y = self.tail_y

        pulse = 0
        if self.holding:
            pulse = (math.sin(t * 20) + 1) * 0.5

        # シャドウ
        shadow = pygame.Surface((LANE_WIDTH + 20, int(height) + 40), pygame.SRCALPHA)
        for i in range(12):
            alpha = int(55 * (1 - i / 12))
            pygame.draw.rect(
                shadow,
                (0, 0, 0, alpha),
                (10 - i, 20 - i, LANE_WIDTH + i * 2, int(height) + i * 2),
                border_radius=20,
            )
        screen.blit(shadow, (x - 10, head_y - 20))

        # 光の帯
        if self.holding:
            beam = pygame.Surface((LANE_WIDTH, int(height)), pygame.SRCALPHA)
            for i in range(int(height)):
                intensity = 150 + int(80 * pulse)
                alpha = int(90 + 80 * pulse)
                pygame.draw.line(
                    beam,
                    (intensity, intensity, 255, alpha),
                    (LANE_WIDTH // 2 - 6, i),
                    (LANE_WIDTH // 2 + 6, i),
                    3,
                )
            screen.blit(beam, (x, head_y))

        # ボディ
        body = pygame.Surface((LANE_WIDTH, int(height)), pygame.SRCALPHA)
        for i in range(int(height)):
            c = 170 + int(60 * (i / max(1, height)))
            pygame.draw.line(body, (0, c, 255), (0, i), (LANE_WIDTH, i))
        screen.blit(body, (x, head_y))

        # 縁取り
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (x, head_y, LANE_WIDTH, height),
            3,
            border_radius=16,
        )

        # コア
        core_rect = pygame.Rect(x + LANE_WIDTH // 2 - 4, head_y + 10, 8, max(8, int(height) - 20))
        pygame.draw.rect(screen, (255, 255, 255), core_rect, border_radius=4)

        # ヘッド
        pygame.draw.ellipse(screen, (0, 200, 255), (x, head_y - 14, LANE_WIDTH, 28))
        pygame.draw.ellipse(screen, (255, 255, 255), (x + 8, head_y - 6, LANE_WIDTH - 16, 12))

        # テール
        pygame.draw.ellipse(screen, (0, 200, 255), (x, tail_y - 14, LANE_WIDTH, 28))
        pygame.draw.ellipse(screen, (255, 255, 255), (x + 8, tail_y - 6, LANE_WIDTH - 16, 12))

    def check_release(
        self, lane_pressed: bool, released: bool, effects: List[LongEndEffect]
    ) -> None:
        """
        ロングノーツのリリース判定

        Args:
            lane_pressed: レーンが押されているか
            released: リリースされたか
            effects: エフェクトリスト
        """
        if not self.is_long:
            return

        if not self.holding and lane_pressed:
            self.holding = True

        if self.holding and released:
            self.holding = False
            self.finished = True

            effects.append(
                LongEndEffect(self.lane * LANE_WIDTH + LANE_WIDTH // 2, JUDGE_LINE, (60, 120, 255))
            )


# ========================================
# 背景要素クラス
# ========================================
class BGTile:
    """背景タイル（装飾用）"""

    def __init__(self) -> None:
        """背景タイルを初期化"""
        self.reset()

    def reset(self) -> None:
        """タイルをリセット"""
        self.x: float = random.randint(0, WIDTH)
        self.y: float = random.randint(-HEIGHT, 0)
        self.w: int = random.randint(60, 120)
        self.h: int = random.randint(200, 350)
        self.speed: float = random.uniform(80, 150)
        self.color: Tuple[int, int, int] = (230, 230, 255)

    def update(self, dt: float) -> None:
        """タイルを更新"""
        self.y += self.speed * dt
        if self.y > HEIGHT:
            self.reset()

    def draw(
        self, screen: pygame.Surface, color_override: Optional[Tuple[int, int, int]] = None
    ) -> None:
        """タイルを描画"""
        color = color_override if color_override is not None else self.color
        pygame.draw.rect(screen, color, (self.x, self.y, self.w, self.h), border_radius=20)


# ========================================
# エフェクトクラス
# ========================================
class JudgeEffect:
    """判定エフェクト（Perfect/Great/Good/Miss）"""

    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int]) -> None:
        """
        判定エフェクトを初期化

        Args:
            x: X座標
            y: Y座標
            text: 表示テキスト
            color: 色 (R, G, B)
        """
        self.x: float = x
        self.y: float = y
        self.text: str = text
        self.color: Tuple[int, int, int] = color
        self.alpha: int = 255
        self.timer: float = 0

        self.ring_radius: float = 0
        self.ring_max: float = 45
        self.scale: float = 1.0

        self.sparks: List[List[float]] = [
            [random.uniform(-2, 2), random.uniform(-2, -0.5), random.randint(3, 6)]
            for _ in range(10)
        ]

    def update(self, dt: float) -> None:
        """エフェクトを更新"""
        self.timer += dt

        if self.timer < 0.12:
            self.scale = 1.4 - (self.timer / 0.12) * 0.4
        else:
            self.scale += (1.0 - self.scale) * 0.15

        self.alpha = max(0, 255 - int(self.timer * 700))
        self.ring_radius += 260 * dt

        for s in self.sparks:
            s[1] += 12 * dt
            s[2] -= 22 * dt

    def draw(self, screen: pygame.Surface) -> None:
        """エフェクトを描画"""
        size = int(40 * self.scale)
        pop_font = pygame.font.SysFont(None, size)

        surf = pop_font.render(self.text, True, self.color)
        surf.set_alpha(self.alpha)

        text_x = self.x - surf.get_width() // 2
        text_y = self.y - surf.get_height() // 2

        # 縁取り
        outline = pop_font.render(self.text, True, (0, 0, 0))
        outline.set_alpha(self.alpha)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            screen.blit(outline, (text_x + dx, text_y + dy))

        screen.blit(surf, (text_x, text_y))

        # リング
        if self.ring_radius < self.ring_max:
            ring_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(
                ring_surf,
                (*self.color, int(self.alpha)),
                (100, 100),
                int(self.ring_radius),
                3,
            )
            screen.blit(ring_surf, (self.x - 100, self.y - 100))

        # スパーク
        for s in self.sparks:
            if s[2] > 0:
                spark_x = self.x + s[0] * 12
                spark_y = self.y + s[1] * 12
                pygame.draw.circle(
                    screen,
                    (*self.color, int(self.alpha)),
                    (int(spark_x), int(spark_y)),
                    int(s[2]),
                )


class LongEndEffect:
    """ロング終了エフェクト"""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        """ロング終了エフェクトを初期化"""
        self.x: float = x
        self.y: float = y
        self.color: Tuple[int, int, int] = color
        self.alpha: int = 255
        self.timer: float = 0
        self.radius: float = 0
        self.max_radius: float = 70

        self.sparks: List[List[float]] = [
            [random.uniform(-2, 2), random.uniform(-2, 2), random.randint(4, 7)] for _ in range(12)
        ]

    def update(self, dt: float) -> None:
        """エフェクトを更新"""
        self.timer += dt
        self.radius += 300 * dt
        self.alpha = max(0, 255 - int(self.timer * 900))

        for s in self.sparks:
            s[0] *= 1.05
            s[1] *= 1.05
            s[2] -= 25 * dt

    def draw(self, screen: pygame.Surface) -> None:
        """エフェクトを描画"""
        glow = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(
            glow,
            (255, 255, 255, int(self.alpha * 0.8)),
            (100, 100),
            int(self.radius * 0.6),
        )
        screen.blit(glow, (self.x - 100, self.y - 100))

        ring = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(
            ring,
            (*self.color, int(self.alpha)),
            (100, 100),
            int(self.radius),
            4,
        )
        screen.blit(ring, (self.x - 100, self.y - 100))

        for s in self.sparks:
            if s[2] > 0:
                sx = self.x + s[0] * 15
                sy = self.y + s[1] * 15
                pygame.draw.circle(
                    screen,
                    (*self.color, int(self.alpha)),
                    (int(sx), int(sy)),
                    int(s[2]),
                )


class BGGlow:
    """背景発光（コンボ連動）"""

    def __init__(self) -> None:
        """背景発光を初期化"""
        self.intensity: float = 0.0
        self.flash: float = 0.0

    def update(self, dt: float, combo: int, judge_text: str) -> None:
        """発光を更新"""
        target = min(1.0, combo / 150)
        self.intensity += (target - self.intensity) * 0.05

        if judge_text == "Perfect!":
            self.flash = 1.0

        self.flash -= dt * 3
        if self.flash < 0:
            self.flash = 0

    def draw(self, screen: pygame.Surface) -> None:
        """発光を描画"""
        power = min(1.0, self.intensity + self.flash)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((80, 120, 255, int(180 * power)))
        screen.blit(overlay, (0, 0))


class JudgeBeam:
    """判定ラインの光の帯"""

    def __init__(self) -> None:
        """判定ビームを初期化"""
        self.timer: float = 0.0

    def trigger(self) -> None:
        """ビームをトリガー"""
        self.timer = 1.0

    def update(self, dt: float) -> None:
        """ビームを更新"""
        if self.timer > 0:
            self.timer -= dt * 2
            if self.timer < 0:
                self.timer = 0

    def draw(self, screen: pygame.Surface) -> None:
        """ビームを描画"""
        JUDGE_LINE = HEIGHT - 100
        base = pygame.Surface((WIDTH, 20), pygame.SRCALPHA)
        pygame.draw.rect(base, (120, 160, 255, 80), (0, 0, WIDTH, 20))
        screen.blit(base, (0, JUDGE_LINE - 10))

        if self.timer > 0:
            beam = pygame.Surface((WIDTH, 20), pygame.SRCALPHA)
            for i in range(8):
                alpha = int(200 * self.timer * (1 - i / 8))
                pygame.draw.rect(beam, (255, 255, 255, alpha), (i * 40, 0, 30, 20))
            screen.blit(beam, (0, JUDGE_LINE - 10))


class ShortHitEffect:
    """ショートノーツ着弾エフェクト"""

    def __init__(self, x: float, y: float) -> None:
        """エフェクトを初期化"""
        self.x = x
        self.y = y
        self.alpha = 255
        self.radius = 0

    def update(self, dt: float) -> None:
        """エフェクトを更新"""
        self.radius += 300 * dt
        self.alpha = max(0, self.alpha - 900 * dt)

    def draw(self, screen: pygame.Surface) -> None:
        """エフェクトを描画"""
        surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, int(self.alpha)), (100, 100), int(self.radius), 4)
        screen.blit(surf, (self.x - 100, self.y - 100))


class RippleEffect:
    """波紋エフェクト"""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        """波紋を初期化"""
        self.x = x
        self.y = y
        self.color = color
        self.radius = 0.0
        self.alpha = 200.0

    def update(self, dt: float) -> None:
        """波紋を更新"""
        self.radius += 450 * dt
        self.alpha -= 350 * dt
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, screen: pygame.Surface) -> None:
        """波紋を描画"""
        if self.alpha <= 0:
            return

        surf = pygame.Surface((300, 80), pygame.SRCALPHA)
        pygame.draw.ellipse(
            surf,
            (*self.color, int(self.alpha)),
            (
                150 - self.radius,
                40 - self.radius * 0.25,
                self.radius * 2,
                self.radius * 0.5,
            ),
            3,
        )
        screen.blit(surf, (self.x - 150, self.y - 40))
