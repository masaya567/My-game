import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pygame

from manager.screen_manager import ScreenManager, create_manager
from ui.key_config_screen import KeyConfigScreen
from ui.settings_screen import SettingsScreen


class KeyConfigFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_create_manager_registers_key_config_screen(self):
        with patch("manager.screen_manager.ResourceManager") as resource_manager:
            with patch.object(ScreenManager, "set"):
                manager = create_manager()

        resource_manager.return_value.initialize.assert_called_once()
        self.assertIs(manager.screens["key_config"], KeyConfigScreen)

    def test_settings_enter_opens_key_config(self):
        manager = SimpleNamespace(
            settings={
                "master_volume": 100,
                "note_speed": 1.0,
                "theme_color": "Blue",
                "key_config": {"Lane 1": pygame.K_d},
            },
            resources=object(),
        )
        screen = SettingsScreen(manager)
        screen.index = next(
            index for index, option in enumerate(screen.options) if option.get("action")
        )
        screen.play_se = Mock()
        screen.request_transition = Mock()

        screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

        screen.request_transition.assert_called_once_with("key_config")

    def test_manager_dispatches_assignment_and_escape_saves_binding(self):
        settings = {
            "key_config": {
                "Lane 1": pygame.K_d,
                "Lane 2": pygame.K_f,
                "Lane 3": pygame.K_j,
                "Lane 4": pygame.K_k,
            }
        }
        screen = KeyConfigScreen.__new__(KeyConfigScreen)
        screen.keys = ["Lane 1", "Lane 2", "Lane 3", "Lane 4"]
        screen.bindings = settings["key_config"].copy()
        screen.index = 0
        screen.waiting_input = True
        screen.manager = SimpleNamespace(settings=settings)
        screen.play_se = Mock()
        screen.request_transition = Mock()

        manager = ScreenManager.__new__(ScreenManager)
        manager.current = screen

        manager.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q))
        self.assertEqual(screen.bindings["Lane 1"], pygame.K_q)
        self.assertEqual(settings["key_config"]["Lane 1"], pygame.K_d)

        manager.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))

        self.assertEqual(settings["key_config"]["Lane 1"], pygame.K_q)
        screen.request_transition.assert_called_once_with("settings")

    def test_settings_save_does_not_overwrite_key_config_action(self):
        key_config = {"Lane 1": pygame.K_q}
        manager = SimpleNamespace(
            settings={"key_config": key_config},
            resources=object(),
        )
        screen = SettingsScreen(manager)

        screen.save_settings()

        self.assertIs(manager.settings["key_config"], key_config)

    def test_settings_persist_and_merge_with_defaults(self):
        with TemporaryDirectory() as temporary_directory:
            settings_path = Path(temporary_directory) / "settings.json"
            with patch("manager.screen_manager.SETTINGS_PATH", settings_path):
                with patch("manager.screen_manager.ResourceManager"):
                    manager = ScreenManager()
                    manager.settings["theme_color"] = "Gold"
                    manager.settings["key_config"]["Lane 1"] = pygame.K_q
                    manager.save_settings()

                    restored = ScreenManager()

            self.assertEqual(restored.settings["theme_color"], "Gold")
            self.assertEqual(restored.settings["key_config"]["Lane 1"], pygame.K_q)
            self.assertEqual(restored.settings["key_config"]["Lane 2"], pygame.K_f)
            self.assertEqual(restored.settings["note_speed"], 1.0)


if __name__ == "__main__":
    unittest.main()
