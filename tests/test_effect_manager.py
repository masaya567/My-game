import unittest
from unittest.mock import patch

import pygame

from graphics.effects.effect_manager import EffectManager
from graphics.effects.glow_circle import GlowCircle
from graphics.effects.glow_effect import GlowEffect
from graphics.effects.judge_beam import JudgeBeam
from graphics.effects.judge_burst import JudgeBurst
from graphics.effects.hit_line import HitLine
from graphics.effects.lane_flash import LaneFlash
from graphics.effects.ripple_effect import RippleEffect
from graphics.effects.judge_ring import JudgeRing
from graphics.note_renderer import NoteRenderer


class EffectManagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_spawn_hit_effect_accepts_and_uses_strength(self):
        manager = EffectManager()
        font = pygame.font.Font(None, 24)

        manager.spawn_hit_effect(100, "perfect", font, strength=0.4)

        self.assertAlmostEqual(manager.effects[0].strength, 0.4)
        self.assertAlmostEqual(manager.effects[1].strength, 0.4)

    def test_draw_does_not_retry_an_effect_after_type_error(self):
        calls = []

        class BrokenEffect:
            def draw(self, screen):
                calls.append(screen)
                raise TypeError("effect draw failed")

        manager = EffectManager()
        manager.effects.append(BrokenEffect())
        screen = pygame.Surface((10, 10))

        with self.assertRaisesRegex(TypeError, "effect draw failed"):
            manager.draw(screen)

        self.assertEqual(calls, [screen])

    def test_glow_circle_reuses_scaled_surface_between_frames(self):
        glow = GlowCircle(100, 100)
        glow.radius = 40
        screen = pygame.Surface((200, 200))
        glow.draw(screen)

        with patch(
            "graphics.effects.glow_circle.pygame.transform.smoothscale",
            wraps=pygame.transform.smoothscale,
        ) as smoothscale:
            glow.draw(screen)

        smoothscale.assert_not_called()

    def test_beam_and_ripple_reuse_draw_surfaces(self):
        screen = pygame.Surface((400, 600))
        beam = JudgeBeam(100, 400, (120, 180, 255), 1.0)
        ripple = RippleEffect(400, (120, 180, 255), 1.0)

        beam.draw(screen)
        ripple.draw(screen)
        beam_surface = beam._surface
        ripple_surface = ripple._surface

        beam.draw(screen)
        ripple.draw(screen)

        self.assertIs(beam._surface, beam_surface)
        self.assertIs(ripple._surface, ripple_surface)

    def test_hit_effect_drawers_do_not_allocate_surfaces_per_frame(self):
        screen = pygame.Surface((400, 600))
        lane_flash = LaneFlash(50, 100, 1.0)
        lane_flash.trigger()
        effects = [
            JudgeBurst((100, 300), (120, 180, 255)),
            JudgeRing((100, 300), (120, 180, 255)),
            HitLine(100, 300, (120, 180, 255), 1.0),
            lane_flash,
        ]
        for effect in effects:
            effect.draw(screen)

        with patch("graphics.effects.judge_burst.pygame.Surface", wraps=pygame.Surface) as factory:
            for effect in effects:
                effect.draw(screen)

        factory.assert_not_called()

    def test_glow_effect_reuses_instance_surface(self):
        effect = GlowEffect(100, 100)
        screen = pygame.Surface((200, 200))

        with patch("graphics.effects.glow_effect.pygame.Surface") as factory:
            effect.draw(screen)

        factory.assert_not_called()

    def test_hit_flash_reuses_cached_surface(self):
        manager = EffectManager()
        manager.spawn_hit_flash(100)
        screen = pygame.Surface((400, 600))

        manager.draw(screen)

        with patch(
            "graphics.effects.effect_manager.pygame.Surface", wraps=pygame.Surface
        ) as factory:
            manager.draw(screen)

        factory.assert_not_called()

    def test_short_note_render_uses_cached_surfaces_and_skips_long_parts(self):
        renderer = NoteRenderer(0)
        screen = pygame.Surface((400, 600))
        renderer.draw_short(screen, 50, 100)

        with patch("graphics.note_renderer.pygame.Surface", wraps=pygame.Surface) as factory:
            renderer.draw_short(screen, 50, 120)

        factory.assert_not_called()
        self.assertIsNone(renderer.long_head)
        self.assertIsNone(renderer.long_beam)

    def test_hit_flash_updates_by_elapsed_time_not_draw_calls(self):
        renderer = NoteRenderer(0)
        renderer.trigger_head_flash(50, 100, (255, 255, 255), 1.0)

        renderer.update(0.05)

        self.assertAlmostEqual(renderer.hit_flash.timer, 0.05)


if __name__ == "__main__":
    unittest.main()
