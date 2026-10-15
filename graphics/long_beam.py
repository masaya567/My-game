import pygame
import math
from constants import LANE_WIDTH, HEIGHT


class LongBeam:
    """
    商用品質：判定ライン光帯＋縦光ビーム（完全版・RGBA安全化）
    """

    def __init__(self, width: int, y: float, lane_x: float, strength=1.0, color=(120, 180, 255)):
        # 横光
        self.width = width
        self.y = y
        self.height = 42

        self.alpha = 0
        self.active = False

        self.light_x = 0
        self.light_speed = 1800

        # 縦光
        self.beam_height = 0
        self.beam_alpha = 0
        self.beam_speed = 2400
        self.beam_max_height = HEIGHT * 0.85

        self.lane_x = lane_x

        # 判定強度（Perfect=1.0 / Great=0.8 / Good=0.6）
        self.strength = strength

        # 判定色
        self.color = tuple(int(channel) for channel in color[:3])

        # 内部タイマー
        self.timer = 0.0

    # ============================================================
    # トリガー処理
    # ============================================================

    def trigger(self):
        self.active = True

        # 横光
        self.alpha = 255 * self.strength
        self.light_x = -self.width

        # 縦光
        self.beam_alpha = 180 * self.strength
        self.beam_height = 0

        self.timer = 0.0

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt, holding=False, pulse=0.0):
        if pulse is not None:
            self.timer = float(pulse)

        if not self.active:
            return

        if holding:
            self.timer += dt * 4

        # easing
        ease = 1 - math.exp(-self.timer * 2)

        # 横光フェード
        self.alpha = max(0, self.alpha - 600 * dt * self.strength)
        self.light_x += self.light_speed * dt

        # 縦光フェード
        self.beam_alpha = max(0, self.beam_alpha - 300 * dt * self.strength)
        self.beam_height += self.beam_speed * dt * ease

        if self.alpha <= 0 and self.beam_alpha <= 0:
            self.active = False

    # ============================================================
    # 描画処理（完全安全版）
    # ============================================================

    def draw(self, screen, x=None, head_y=None, height=None, holding=False, color=None, alpha=None):
        if x is not None:
            self.lane_x = x
        if head_y is not None and height is not None:
            self.y = head_y + height / 2

        # ★ 修正：color=None のときは上書きしない
        if color is not None:
            if isinstance(color, (tuple, list)) and len(color) >= 3:
                self.color = tuple(int(channel) for channel in color[:3])

        if alpha is not None:
            self.alpha = alpha

        if not self.active:
            return

        # ============================================================
        # ① 横光（ライン光帯）RGBA安全版
        # ============================================================

        if self.alpha > 0:
            beam_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            # --- 上下グラデーション（RGBA安全版） ---
            for i in range(self.height):
                grad_alpha = int(self.alpha * (1 - abs(i - self.height / 2) / (self.height / 2)))
                line = pygame.Surface((self.width, 1), pygame.SRCALPHA)
                line.fill((*self.color, grad_alpha))
                beam_surface.blit(line, (0, i))

            # --- 横方向の波動光（RGBA安全版） ---
            wave = math.sin(self.timer * 3) * 40
            glow_width = 120 + wave

            light_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            for px in range(int(self.light_x - glow_width), int(self.light_x + glow_width)):
                if 0 <= px < self.width:
                    dist = abs(px - self.light_x)
                    a = int(self.alpha * (1 - dist / glow_width))

                    col = pygame.Surface((1, self.height), pygame.SRCALPHA)
                    col.fill((255, 255, 255, a))
                    light_surface.blit(col, (px, 0))

            beam_surface.blit(light_surface, (0, 0), special_flags=pygame.BLEND_ADD)

            screen.blit(beam_surface, (0, self.y - self.height // 2))

        # ============================================================
        # ② 縦光（判定ラインから上に伸びる光）RGBA安全版
        # ============================================================

        if self.beam_alpha > 0:
            surf = pygame.Surface((LANE_WIDTH, int(self.beam_height)), pygame.SRCALPHA)

            # 中心コア光（脈動）
            pulse = (math.sin(self.timer * 2) + 1) * 0.5
            core_alpha = int(self.beam_alpha * (0.8 + 0.4 * pulse))

            core = pygame.Surface((LANE_WIDTH // 2, int(self.beam_height)), pygame.SRCALPHA)
            core.fill((*self.color, core_alpha))
            surf.blit(core, (LANE_WIDTH // 4, 0))

            # 外側グロー
            glow_alpha = int(self.beam_alpha * 0.6 * (1 + pulse))
            glow = pygame.Surface((LANE_WIDTH, int(self.beam_height)), pygame.SRCALPHA)
            glow.fill((*self.color, glow_alpha))
            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

            # wobble（縦光の揺れ）
            wobble = math.sin(self.timer * 3.5) * 6 * self.strength

            screen.blit(surf, (self.lane_x + wobble, self.y - self.beam_height))
