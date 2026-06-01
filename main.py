"""Piano Tiles - メインプログラム（プロフェッショナル版）

モダンなプロジェクト構造を採用し、各モジュールが独立して動作します。
"""

import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import pygame

from audio_analyzer import analyze_songs
from chart_generator import auto_generate_chart
from classes_professional import (
    BGGlow,
    BGTile,
    JudgeBeam,
    JudgeEffect,
    LongEndEffect,
    Note,
    RippleEffect,
    ShortHitEffect,
)
from constants import *
from logger import get_logger
from songs import get_songs_as_dict
from utils import get_system_font, load_chart, render_fit_text, wrap_text

logger = get_logger(__name__)

# Pygame初期化
pygame.init()
pygame.mixer.init()

# グローバル状態
effects: List[Any] = []
lane_flash: List[float] = [0, 0, 0, 0]
camera_shake: float = 0
judge_flash: float = 0
judge_beam: Optional[JudgeBeam] = None

# グローバルリソース
screen: Optional[pygame.Surface] = None
clock: Optional[pygame.time.Clock] = None
font: Optional[pygame.font.Font] = None
font_small: Optional[pygame.font.Font] = None
font_large: Optional[pygame.font.Font] = None
font_medium: Optional[pygame.font.Font] = None

# 曲リスト
songs: List[Dict[str, Any]] = get_songs_as_dict()


def initialize_display() -> None:
    """ディスプレイ初期化"""
    global screen, clock, font, font_small, font_large, font_medium

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Piano Tiles")
    clock = pygame.time.Clock()

    # フォント取得
    font_path = get_system_font()
    if font_path and os.path.exists(font_path):
        try:
            font = pygame.font.Font(font_path, 48)
            font_small = pygame.font.Font(font_path, 32)
            font_large = pygame.font.Font(font_path, 64)
            font_medium = pygame.font.Font(font_path, 40)
        except Exception as e:
            logger.warning(f"Failed to load font from {font_path}: {e}. Using system fonts.")
            font = pygame.font.SysFont("arial", 48)
            font_small = pygame.font.SysFont("arial", 32)
            font_large = pygame.font.SysFont("arial", 64)
            font_medium = pygame.font.SysFont("arial", 40)
    else:
        font = pygame.font.SysFont("arial", 48)
        font_small = pygame.font.SysFont("arial", 32)
        font_large = pygame.font.SysFont("arial", 64)
        font_medium = pygame.font.SysFont("arial", 40)

    logger.info("Display initialized successfully")


def load_all_songs() -> None:
    """すべての曲情報をロード"""
    global songs
    songs = analyze_songs(songs)
    logger.info(f"Loaded {len(songs)} songs")


def build_notes_from_chart(song: Dict[str, Any]) -> None:
    """譜面からノーツを生成"""
    VISIBLE_TIME = 1.2
    SPAWN_Y = -NOTE_HEIGHT
    distance = JUDGE_LINE - SPAWN_Y
    base_speed = distance / VISIBLE_TIME

    notes = []
    current_bpm = song["bpm"]

    for n in song["chart"]:
        if "bpm" in n:
            current_bpm = n["bpm"]
            continue

        start = n["time"]
        bpm = current_bpm
        speed = base_speed * (bpm / 120)

        if n["type"] == "long":
            end = max(n.get("end", start + 0.5), start + 0.2)
        else:
            end = start

        lane = n["lane"]
        notes.append(Note(lane, start, end, speed))

    song["notes"] = notes


def song_select_screen(
    key_config: Dict, difficulty: str, speed_level: int
) -> Optional[Dict[str, Any]]:
    """曲選択画面"""
    index = 0
    scroll_x = 0
    target_scroll = 0

    CARD_W = 220
    CARD_H = 300
    GAP = 60

    bg_tiles = [BGTile() for _ in range(8)]
    last_preview_index = -1

    while True:
        dt = clock.tick(60) / 1000.0
        screen.fill((255, 255, 255))

        # 背景
        for tile in bg_tiles:
            tile.update(dt)
            tile.draw(screen)

        # タイトル
        title = font_large.render("Select Song", True, (60, 120, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        # スクロール
        scroll_x += (target_scroll - scroll_x) * 0.2

        # 曲カード
        for i, song in enumerate(songs):
            if i == index:
                scale = 1.10
                color = (80, 120, 255)
            else:
                scale = 0.92
                color = (200, 220, 255)

            w = int(CARD_W * scale)
            h = int(CARD_H * scale)
            x = WIDTH // 2 + i * (CARD_W + GAP) - w // 2 + scroll_x
            CARD_CENTER_Y = 330
            y = CARD_CENTER_Y - h // 2

            rect = pygame.Rect(x, y, w, h)

            # 影
            shadow_rect = rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(screen, (180, 180, 200), shadow_rect, border_radius=20)

            # カード
            pygame.draw.rect(screen, color, rect, border_radius=20)

            # ジャケット
            jacket_surf = song["jacket"].copy()
            jacket_h = int(h * 0.48)
            jacket = pygame.transform.scale(jacket_surf, (w - 40, jacket_h))
            jacket_rect = jacket.get_rect()
            jacket_rect.centerx = rect.centerx
            jacket_rect.top = rect.top + int(h * 0.12)
            screen.blit(jacket, jacket_rect)

            # 情報
            base_y = jacket_rect.bottom + int(h * 0.02)
            max_info_width = w - 40
            LINE = int(h * 0.09)

            title_surf = render_fit_text(song["title"], font_small, max_info_width, (0, 0, 0))
            screen.blit(title_surf, (rect.centerx - title_surf.get_width() // 2, base_y))

            diff_surf = render_fit_text(
                str(song["difficulty"]), font_small, max_info_width, (0, 0, 0)
            )
            screen.blit(diff_surf, (rect.centerx - diff_surf.get_width() // 2, base_y + LINE))

            bpm_surf = render_fit_text(f"BPM: {song['bpm']}", font_small, max_info_width, (0, 0, 0))
            screen.blit(bpm_surf, (rect.centerx - bpm_surf.get_width() // 2, base_y + LINE * 2))

            m = int(song["length"]) // 60
            s = int(song["length"]) % 60
            len_surf = render_fit_text(f"{m}分{s}秒", font_small, max_info_width, (0, 0, 0))
            screen.blit(len_surf, (rect.centerx - len_surf.get_width() // 2, base_y + LINE * 3))

        # 操作説明
        info_text = "← → で選択 / SPACEで決定 / ESCで戻る"
        info_surf = render_fit_text(info_text, font_small, WIDTH - 40, (60, 120, 255))
        screen.blit(info_surf, (WIDTH // 2 - info_surf.get_width() // 2, 520))

        # プレビュー
        if index != last_preview_index:
            last_preview_index = index
            pygame.mixer.music.stop()
            pygame.mixer.music.load(songs[index]["file"])
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(0.3)

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    index = (index - 1) % len(songs)
                    target_scroll = -(index * (CARD_W + GAP))
                elif event.key == pygame.K_RIGHT:
                    index = (index + 1) % len(songs)
                    target_scroll = -(index * (CARD_W + GAP))
                elif event.key == pygame.K_SPACE:
                    pygame.mixer.music.stop()
                    return songs[index]
                elif event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return None

        pygame.display.flip()


def handle_keydown(
    notes: List[Note],
    lane_pressed: int,
    score: int,
    combo: int,
    max_combo: int,
    judge_text: str,
    judge_timer: float,
    perfect_count: int,
    great_count: int,
    good_count: int,
    miss_count: int,
) -> Tuple:
    """キー押下処理"""
    global effects, camera_shake, judge_beam, judge_flash

    lane_notes = [n for n in notes if n.lane == lane_pressed and not n.finished]
    if not lane_notes:
        return (
            score,
            combo,
            max_combo,
            judge_text,
            judge_timer,
            perfect_count,
            great_count,
            good_count,
            miss_count,
        )

    note = min(lane_notes, key=lambda n: abs(n.head_y - JUDGE_LINE))
    dist = abs(note.head_y - JUDGE_LINE)

    PERFECT, GREAT, GOOD = 40, 80, 120
    x = note.lane * LANE_WIDTH + LANE_WIDTH // 2
    y = JUDGE_LINE

    if dist <= PERFECT:
        judge = "Perfect!"
        score += 1000
        combo += 1
        perfect_count += 1
        effects.append(JudgeEffect(x, y - 60, "Perfect!", (60, 120, 255)))
        effects.append(RippleEffect(x, y, (60, 120, 255)))
        camera_shake = 2
        judge_beam.trigger()
        judge_flash = 1.0

    elif dist <= GREAT:
        judge = "Great!"
        score += 700
        combo += 1
        great_count += 1
        effects.append(JudgeEffect(x, y - 60, "Great!", (120, 200, 255)))
        effects.append(RippleEffect(x, y, (120, 200, 255)))
        camera_shake = 3
        judge_flash = 0.8

    elif dist <= GOOD:
        judge = "Good!"
        score += 300
        combo += 1
        good_count += 1
        effects.append(JudgeEffect(x, y - 60, "Good!", (200, 200, 255)))
        effects.append(RippleEffect(x, y, (200, 200, 255)))
        judge_flash = 0.5

    else:
        judge = "Miss!"
        combo = 0
        miss_count += 1
        effects.append(JudgeEffect(x, y - 60, "Miss!", (255, 120, 120)))
        effects.append(RippleEffect(x, y, (255, 120, 120)))
        camera_shake = 6
        if not note.is_long:
            note.finished = True
        return (
            score,
            combo,
            max_combo,
            judge,
            0.2,
            perfect_count,
            great_count,
            good_count,
            miss_count,
        )

    if not note.is_long:
        note.finished = True
    else:
        note.holding = True
        note.active = True

    max_combo = max(max_combo, combo)
    return score, combo, max_combo, judge, 0.2, perfect_count, great_count, good_count, miss_count


def game_loop(selected_song: Dict[str, Any], key_config: Dict) -> Any:
    """ゲームループ"""
    global lane_flash, effects, judge_flash, camera_shake, judge_beam

    effects.clear()
    judge_flash = 0.0
    camera_shake = 0

    song_bpm = selected_song["bpm"]
    bpm_events = [ev for ev in selected_song["chart"] if "bpm" in ev]

    VISIBLE_TIME = 1.2
    SPAWN_Y = -NOTE_HEIGHT
    distance = JUDGE_LINE - SPAWN_Y
    base_speed = distance / VISIBLE_TIME

    paused = False
    bg_tiles = [BGTile() for _ in range(6)]
    bg_glow = BGGlow()
    judge_beam = JudgeBeam()

    pygame.mixer.music.load(selected_song["file"])
    pygame.mixer.music.play()

    notes = selected_song["notes"]

    score = combo = max_combo = 0
    judge_text = ""
    judge_timer = 0
    perfect_count = great_count = good_count = miss_count = 0

    start_time = time.perf_counter()

    while True:
        dt = clock.tick(60) / 1000.0
        t = time.perf_counter() - start_time

        # イベント処理
        if not paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        return "title"

                    lane_pressed = key_config.get(event.key)
                    if lane_pressed is not None:
                        lane_flash[lane_pressed] = 0.2
                        (
                            score,
                            combo,
                            max_combo,
                            judge_text,
                            judge_timer,
                            perfect_count,
                            great_count,
                            good_count,
                            miss_count,
                        ) = handle_keydown(
                            notes,
                            lane_pressed,
                            score,
                            combo,
                            max_combo,
                            judge_text,
                            judge_timer,
                            perfect_count,
                            great_count,
                            good_count,
                            miss_count,
                        )
                        if judge_text != "Miss!":
                            effects.append(
                                ShortHitEffect(
                                    lane_pressed * LANE_WIDTH + LANE_WIDTH // 2, JUDGE_LINE
                                )
                            )

                elif event.type == pygame.KEYUP:
                    # キーリリース時：ロングノーツを終了
                    lane_released = key_config.get(event.key)
                    if lane_released is not None:
                        for note in notes:
                            if note.is_long and note.lane == lane_released and note.holding:
                                note.finished = True
                                note.holding = False
                                break

        # ノーツ更新
        for note in notes:
            note.update(dt, t, bpm_events, base_speed, song_bpm)

        bg_glow.update(dt, combo, judge_text)
        judge_beam.update(dt)

        # ノーツ削除
        new_notes = []
        for note in notes:
            if note.finished:
                continue
            if not note.is_long and note.y > HEIGHT:
                # ショートノーツ：頭が画面を超えたら削除
                combo = 0
                miss_count += 1
                camera_shake = 6
                continue
            if note.is_long and note.tail_y > HEIGHT:
                # ロングノーツ：尻尾が画面を超えたら削除
                continue
            new_notes.append(note)

        notes = new_notes

        # エフェクト更新
        for effect in effects[:]:
            effect.update(dt)
            if effect.alpha <= 0:
                effects.remove(effect)

        # 曲終了判定
        if (not pygame.mixer.music.get_busy()) and len(notes) == 0:
            return score, max_combo, perfect_count, great_count, good_count, miss_count

        # 描画
        screen.fill((255, 255, 255))

        # 背景
        for tile in bg_tiles:
            tile.update(dt)
            tile.draw(screen)

        # 判定ライン
        pygame.draw.line(screen, (60, 120, 255), (0, JUDGE_LINE), (WIDTH, JUDGE_LINE), 3)

        # ノーツ描画
        for note in notes:
            note.draw(screen, t)

        # エフェクト描画
        for effect in effects:
            effect.draw(screen)

        # スコア表示
        score_surf = font_small.render(f"Score: {score}", True, (30, 30, 30))
        screen.blit(score_surf, (10, 10))

        combo_surf = font_small.render(f"Combo: {combo}", True, (60, 120, 255))
        screen.blit(combo_surf, (10, 50))

        pygame.display.flip()


def result_screen(
    score: int, max_combo: int, perfect: int, great: int, good: int, miss: int
) -> None:
    """リザルト画面"""
    total = perfect + great + good + miss
    accuracy = (perfect * 1.0 + great * 0.8 + good * 0.5) / total * 100 if total > 0 else 0

    if accuracy >= 97:
        rank = "S"
    elif accuracy >= 90:
        rank = "A"
    elif accuracy >= 80:
        rank = "B"
    elif accuracy >= 70:
        rank = "C"
    else:
        rank = "D"

    while True:
        screen.fill((255, 255, 255))

        # ランク
        rank_surf = font_large.render(rank, True, (255, 215, 0))
        screen.blit(rank_surf, (WIDTH // 2 - rank_surf.get_width() // 2, 100))

        # スコア
        score_surf = font_medium.render(f"Score: {score}", True, (60, 120, 255))
        screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 200))

        acc_surf = font_medium.render(f"Accuracy: {accuracy:.2f}%", True, (60, 120, 255))
        screen.blit(acc_surf, (WIDTH // 2 - acc_surf.get_width() // 2, 250))

        # 判定詳細
        judge_title = font_small.render("Judges", True, (40, 80, 180))
        screen.blit(judge_title, (WIDTH // 2 - judge_title.get_width() // 2, 320))

        perfect_surf = font_small.render(f"Perfect: {perfect}", True, (40, 120, 255))
        screen.blit(perfect_surf, (WIDTH // 2 - perfect_surf.get_width() // 2, 360))

        great_surf = font_small.render(f"Great: {great}", True, (80, 160, 255))
        screen.blit(great_surf, (WIDTH // 2 - great_surf.get_width() // 2, 400))

        good_surf = font_small.render(f"Good: {good}", True, (120, 200, 255))
        screen.blit(good_surf, (WIDTH // 2 - good_surf.get_width() // 2, 440))

        miss_surf = font_small.render(f"Miss: {miss}", True, (160, 200, 255))
        screen.blit(miss_surf, (WIDTH // 2 - miss_surf.get_width() // 2, 480))

        # リトライボタン
        pygame.draw.rect(screen, (80, 120, 255), (WIDTH // 2 - 150, 550, 300, 50), border_radius=20)
        retry_text = font_small.render("Press SPACE to Continue", True, (255, 255, 255))
        screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, 565))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

        pygame.display.flip()
        clock.tick(60)


def main() -> None:
    """メインループ"""
    initialize_display()
    load_all_songs()

    difficulty = "NORMAL"
    speed_level = 3
    key_config = {pygame.K_d: 0, pygame.K_f: 1, pygame.K_j: 2, pygame.K_k: 3}

    while True:
        # タイトル画面（簡易版：フォーカスは曲選択）
        selected_song = song_select_screen(key_config, difficulty, speed_level)
        if selected_song is None:
            pygame.quit()
            sys.exit()

        # JSON から譜面を読み込み（なければ自動生成）
        chart_mode = selected_song.get("chart_mode", "NORMAL")
        load_chart(selected_song, chart_mode)

        # 手動チャートを Note に変換
        build_notes_from_chart(selected_song)

        # ゲーム開始
        result = game_loop(selected_song, key_config)

        if isinstance(result, str):
            # 画面遷移
            if result == "title":
                continue
        else:
            # リザルト表示
            score, max_combo, perfect, great, good, miss = result
            result_screen(score, max_combo, perfect, great, good, miss)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        pygame.quit()
        sys.exit(1)
