import pygame
import math


class JudgeTextAnim:
    """
    商用品質：判定文字アニメーション
    - PERFECT：白＋金の発光、拡大、残像、揺れ
    - GREAT：青の発光
    - GOOD：緑の軽い発光
    - MISS：赤の縮小フェード
    """

    def __init__(self, res):
        self.res = res
        self.active = False
        self.timer = 0.0
        self.judge = ""
        self.x = 0
        self.y = 0

        # 色設定
        self.colors = {
            "perfect": (255, 255, 255),
            "great": (120, 180, 255),
            "good": (120, 255, 160),
            "miss": (255, 80, 80),
        }

    def trigger(self, judge, x, y):
        self.active = True
        self.timer = 0.0
        self.judge = judge.lower()
        self.x = x
        self.y = y

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt
        if self.timer > 0.45:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        t = self.timer
        color = self.colors[self.judge]

        # フォント
        font = self.res.get_font(48, weight="bold")
        text = self.judge.upper()

        # 拡大率
        if self.judge == "perfect":
            scale = 1.0 + math.sin(t * 12) * 0.15 + (0.45 - t) * 0.8
        elif self.judge == "great":
            scale = 1.0 + (0.45 - t) * 0.4
        elif self.judge == "good":
            scale = 1.0 + (0.45 - t) * 0.2
        else:  # MISS
            scale = 1.0 - t * 0.4

        # 透明度
        alpha = int(255 * (1.0 - t / 0.45))

        # テキスト描画
        surf = font.render(text, True, color)
        surf = pygame.transform.rotozoom(surf, 0, scale)

        # 透明度適用
        surf.set_alpha(alpha)

        rect = surf.get_rect(center=(self.x, self.y))

        # PERFECT の残像
        if self.judge == "perfect":
            for i in range(3):
                ghost = pygame.transform.rotozoom(surf, 0, scale - 0.1 * (i + 1))
                ghost.set_alpha(alpha // (i + 2))
                ghost_rect = ghost.get_rect(center=(self.x, self.y - (i * 6)))
                screen.blit(ghost, ghost_rect)

        screen.blit(surf, rect)
