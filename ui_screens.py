"""
ゲームの UI 画面（メニュー、選曲、オプションなど）
"""

import math
import sys

import pygame

from classes_professional import BGGlow, BGTile
from constants import *
from utils import render_fit_text, wrap_text


def title_screen(
    clock,
    screen,
    font,
    font_small,
    font_large,
    font_medium,
    songs,
    song_select_screen,
    option_screen,
    how_to_play_screen,
):
    """タイトル画面"""
    print("TITLE SCREEN START")

    # ★ キー状態を完全リセット（最重要）
    pygame.key.set_mods(0)
    pygame.key.set_repeat(0)

    difficulty = "NORMAL"
    speed_level = 3
    key_config = {pygame.K_d: 0, pygame.K_f: 1, pygame.K_j: 2, pygame.K_k: 3}

    bg_tiles = [BGTile() for _ in range(8)]
    selected = 0

    menu_items = [
        "ゲームスタート",
        "エディタで作る",
        "自動生成で遊ぶ",
        "オプション",
        "あそびかた",
        "ゲーム終了",
    ]

    t = 0

    while True:
        dt = clock.tick(60) / 1000.0
        screen.fill(WHITE)

        # 背景
        for tile in bg_tiles:
            tile.update(dt)
            tile.draw(screen)

        # タイトルロゴ
        t += dt
        offset = int(5 * math.sin(t * 2))
        glow = int(150 + 100 * math.sin(t * 2))
        title_color = (glow, glow, 255)

        title = font_large.render("Piano Tiles", True, title_color)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120 + offset))

        # メニュー
        for i, text in enumerate(menu_items):
            is_selected = i == selected
            w, h = 320, 60
            x = WIDTH // 2 - w // 2
            y = 300 + i * 80

            color = (80, 120, 255) if is_selected else (200, 220, 255)
            pygame.draw.rect(screen, color, (x, y, w, h), border_radius=20)

            label = font_small.render(text, True, BLACK)
            screen.blit(
                label,
                (
                    x + w // 2 - label.get_width() // 2,
                    y + h // 2 - label.get_height() // 2,
                ),
            )

        # 入力処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_items)

                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_items)

                elif event.key == pygame.K_SPACE:

                    # ゲームスタート
                    if selected == 0:
                        selected_song = song_select_screen(key_config, difficulty, speed_level)
                        if selected_song:
                            return (
                                difficulty,
                                speed_level,
                                key_config,
                                selected_song,
                                "play",
                            )

                    # エディタ
                    elif selected == 1:
                        selected_song = song_select_screen(key_config, difficulty, speed_level)
                        if selected_song:
                            return (
                                difficulty,
                                speed_level,
                                key_config,
                                selected_song,
                                "edit",
                            )

                    # 自動生成
                    elif selected == 2:
                        selected_song = song_select_screen(key_config, difficulty, speed_level)
                        if selected_song:
                            return (
                                difficulty,
                                speed_level,
                                key_config,
                                selected_song,
                                "auto",
                            )

                    # オプション
                    elif selected == 3:
                        difficulty, speed_level, key_config = option_screen(
                            difficulty, speed_level, key_config
                        )

                    # あそびかた
                    elif selected == 4:
                        how_to_play_screen()

                    # 終了
                    elif selected == 5:
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()


def option_screen(
    clock,
    screen,
    font,
    font_small,
    font_large,
    font_medium,
    difficulty,
    speed_level,
    key_config,
):
    """オプション画面"""
    menu_items = ["難易度", "ノーツ速度", "キー設定", "戻る"]
    index = 0

    while True:
        screen.fill(WHITE)

        # タイトル
        title = font_large.render("オプション", True, (30, 30, 30))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        # メニュー項目（左ラベル + 右値）
        for i, item in enumerate(menu_items):
            color = (60, 120, 255) if i == index else (30, 30, 30)

            # ラベル
            label = font_small.render(item, True, color)
            label_x = 30
            label_y = 180 + i * 70
            screen.blit(label, (label_x, label_y))

            # 値（戻る以外）
            if item == "難易度":
                value = font.render(difficulty, True, (60, 120, 255))
            elif item == "ノーツ速度":
                value = font.render(f"x{speed_level}", True, (60, 120, 255))
            elif item == "キー設定":
                key_names = " ".join([pygame.key.name(k).upper() for k in key_config.keys()])
                value = font.render(key_names, True, (60, 120, 255))
            else:
                continue  # 戻るには値なし

            # ★ ラベルの右隣に値を配置（はみ出し防止）
            value_x = label_x + label.get_width() + 40
            value_y = label_y - 5
            screen.blit(value, (value_x, value_y))

        # 入力処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    index = (index - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    index = (index + 1) % len(menu_items)

                elif event.key == pygame.K_SPACE:
                    if index == 0:
                        difficulty = change_difficulty_screen(
                            clock,
                            screen,
                            font_small,
                            font_large,
                            font_medium,
                            difficulty,
                        )
                    elif index == 1:
                        speed_level = change_speed_screen(
                            clock,
                            screen,
                            font_small,
                            font_large,
                            font_medium,
                            speed_level,
                        )
                    elif index == 2:
                        key_config = key_config_screen(
                            clock,
                            screen,
                            font_small,
                            font_large,
                            font_medium,
                            key_config,
                        )
                    elif index == 3:
                        return difficulty, speed_level, key_config

                elif event.key == pygame.K_ESCAPE:
                    return difficulty, speed_level, key_config

        pygame.display.flip()
        clock.tick(60)


def change_difficulty_screen(clock, screen, font_small, font_large, font_medium, current):
    """難易度変更画面"""
    options = ["EASY", "NORMAL", "HARD", "PRO"]
    index = options.index(current)

    while True:
        screen.fill(WHITE)

        title = font_large.render("難易度", True, (30, 30, 30))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))

        for i, opt in enumerate(options):
            color = (60, 120, 255) if i == index else (30, 30, 30)
            t = font_medium.render(opt, True, color)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 180 + i * 60))

        # ★ 折り返し説明文
        info_text = "↑↓で選択 / SPACEで決定 / ESCで戻る"
        lines = wrap_text(info_text, font_small, WIDTH - 80)

        y = 440
        for line in lines:
            surf = font_small.render(line, True, (30, 30, 30))
            x = WIDTH // 2 - surf.get_width() // 2
            screen.blit(surf, (x, y))
            y += 28

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    index = (index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    index = (index + 1) % len(options)
                elif event.key == pygame.K_SPACE:
                    return options[index]
                elif event.key == pygame.K_ESCAPE:
                    return current

        pygame.display.flip()
        clock.tick(60)


def change_speed_screen(clock, screen, font_small, font_large, font_medium, speed_level):
    """速度変更画面"""
    while True:
        screen.fill(WHITE)

        title = font_large.render("ノーツ速度", True, (30, 30, 30))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))

        speed_text = font_large.render(f"x{speed_level}", True, (60, 120, 255))
        screen.blit(speed_text, (WIDTH // 2 - speed_text.get_width() // 2, 200))

        # ★ 折り返し説明文
        info_text = "← → で変更 / SPACEで決定 / ESCで戻る"
        lines = wrap_text(info_text, font_small, WIDTH - 80)

        y = 440
        for line in lines:
            surf = font_small.render(line, True, (30, 30, 30))
            x = WIDTH // 2 - surf.get_width() // 2
            screen.blit(surf, (x, y))
            y += 28

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    speed_level = max(1, speed_level - 1)
                elif event.key == pygame.K_RIGHT:
                    speed_level = min(7, speed_level + 1)
                elif event.key == pygame.K_SPACE:
                    return speed_level
                elif event.key == pygame.K_ESCAPE:
                    return speed_level

        pygame.display.flip()
        clock.tick(60)


def key_config_screen(clock, screen, font_small, font_large, font_medium, key_config):
    """キー設定画面"""
    lanes = ["Lane 1", "Lane 2", "Lane 3", "Lane 4"]

    # ★ レーン順でキーを並べる（これが完全版）
    keys = [None, None, None, None]
    for k, v in key_config.items():
        keys[v] = k

    index = 0

    while True:
        screen.fill(WHITE)

        title = font_large.render("キー設定", True, (30, 30, 30))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))

        for i, lane in enumerate(lanes):
            color = (60, 120, 255) if i == index else (30, 30, 30)
            key_name = pygame.key.name(keys[i])
            text = font_medium.render(f"{lane}: {key_name}", True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 180 + i * 60))

        # ★ 折り返し説明文
        info_text = "↑↓で選択 / 任意のキーで変更 / ESCで戻る"
        lines = wrap_text(info_text, font_small, WIDTH - 80)

        y = 440
        for line in lines:
            surf = font_small.render(line, True, (30, 30, 30))
            x = WIDTH // 2 - surf.get_width() // 2
            screen.blit(surf, (x, y))
            y += 28

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    index = (index - 1) % 4
                elif event.key == pygame.K_DOWN:
                    index = (index + 1) % 4
                elif event.key == pygame.K_ESCAPE:
                    return key_config
                else:
                    # キー変更
                    keys[index] = event.key
                    key_config = {
                        keys[0]: 0,
                        keys[1]: 1,
                        keys[2]: 2,
                        keys[3]: 3,
                    }
                    return key_config

        pygame.display.flip()
        clock.tick(60)


def how_to_play_screen(clock, screen, font_small, font_large):
    """あそびかた画面"""
    lines = [
        "あそびかた",
        "",
        "・ノーツに合わせて押します。",
        "・初期キー：D / F / J / K（変更可能）",
        "・ロングノーツは押しっぱなしです。",
        "",
        "SPACEキーで戻ります。",
    ]

    max_width = 300

    while True:
        screen.fill(WHITE)

        # タイトル中央揃え
        title = font_large.render(lines[0], True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        # 本文
        y = 150
        for line in lines[2:]:
            if line == "":
                y += 50
                continue

            wrapped_lines = wrap_text(line, font_small, max_width)
            for wrapped_line in wrapped_lines:
                text = font_small.render(wrapped_line, True, BLACK)
                screen.blit(text, (40, y))
                y += 28

            y += 12

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
