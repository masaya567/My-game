import unittest

import pygame

from utils.jacket.jacket_generator import make_proseka_jacket


class JacketGeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_make_proseka_jacket_returns_shadow_and_cover(self):
        shadow, jacket = make_proseka_jacket("Test Song", base_color=(30, 80, 140), size=(180, 180))

        self.assertIsInstance(shadow, pygame.Surface)
        self.assertIsInstance(jacket, pygame.Surface)
        self.assertEqual(shadow.get_size(), (180, 180))
        self.assertEqual(jacket.get_size(), (180, 180))


if __name__ == "__main__":
    unittest.main()
