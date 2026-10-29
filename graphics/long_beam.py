import pygame
import math
from utils.theme.theme import get_ui_scale


class LongBeam:
    """
    商用品質：ロングノーツ中央光帯（完全版）
    - head_y と同期
    - brightness / pulse と完全連動
    - holding 時に太さ・光量・波動が強化
    - 加算合成
    """

    def __init__(self, width=12):
        self.scale = get_ui_scale()
        self.base_width = int(width * self.scale)
        self.timer = 0.0

    def update(self, dt, holding: bool, pulse: float, brightness: float):
        # 波動タイマー（holding で強化）
        speed = 2.0 + pulse * 2.0
        self.timer += dt * speed

        # beam の太さ（holding で太く）
        self.width = self.base_width + int(4 * pulse * self.scale)

        # 光量（判定色の brightness と pulse で強化）
        self.glow_strength = 0.6 + brightness * 0.4 + pulse * 0.3

    def draw(self, screen, x: float, head_y: float, height: float, holding: bool, color, alpha=255):
        width = self.width
        surf = pygame.Surface((width, int(height)), pygame.SRCALPHA)

        # 波動の強さ
        wave_amp = 80 * self.glow_strength
        wobble = math.sin(self.timer * (3.5 + self.glow_strength)) * (4 + self.glow_strength * 3)

        for i in range(int(height)):
            wave = math.sin((i / 40.0) + self.timer)
            intensity = 150 + int(wave_amp * wave)

            a = int(alpha * self.glow_strength)

            pygame.draw.line(
                surf,
                (intensity, intensity, 255, a),
                (0, i),
                (width, i),
            )

        screen.blit(
            surf,
            (x - width // 2 + wobble, head_y),
            special_flags=pygame.BLEND_ADD,
        )
