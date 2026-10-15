import unittest

import pygame

from songs.model.song_model import Song
from utils.color.theme_colors import SONG_COLOR_MAP


class SongModelJacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_song_color_map_uses_rgb_values(self):
        for color in SONG_COLOR_MAP.values():
            self.assertEqual(len(color), 3)
            self.assertTrue(all(0 <= channel <= 255 for channel in color))

    def test_song_exposes_generated_jacket_for_song_select(self):
        song = Song("arabesque1", "アラベスク 第1番", "", None)

        self.assertIsInstance(song.jacket, pygame.Surface)
        self.assertEqual(song.jacket.get_size(), (256, 256))


if __name__ == "__main__":
    unittest.main()
