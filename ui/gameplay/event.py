import pygame
import time
from game.logger import long_logger

def handle_gameplay_event(screen_obj, event):

    # 曲時間更新
    get_song_time = getattr(screen_obj, "get_song_time", None)
    if callable(get_song_time):
        screen_obj.song_time = get_song_time()
    else:
        start_time = getattr(screen_obj, "music_start_time", None)
        if start_time is None:
            start_time = screen_obj.start_time
        screen_obj.song_time = max(0.0, time.perf_counter() - start_time)

    lane_keys = [[k for k in keys if k is not None] for keys in screen_obj.lane_keys]

    # ============================================================
    # KEYDOWN
    # ============================================================
    if event.type == pygame.KEYDOWN:
        for lane, keys in enumerate(lane_keys):
            if event.key in keys:

                if screen_obj.key_pressed[lane]:
                    continue

                screen_obj.key_pressed[lane] = True

                screen_obj.line_flash = 255
                screen_obj.line_flash_lane = lane

                # ★ HEAD 判定（result, note を受け取る）
                result, note = screen_obj.logic.try_judge(lane, screen_obj.song_time)

                # ロング開始
                if note and note.is_long and result != "none":
                    note.holding = True
                    note.head_judged = True
                    long_logger.info(f"[LONG] HOLD CONFIRMED: note_id={note.id}")

                if result != "none":
                    screen_obj.spawn_hit_effect(lane, result)

        if event.key == pygame.K_ESCAPE:
            pygame.mixer.music.stop()
            screen_obj.play_se("se_back")
            screen_obj.request_transition("title")

    # ============================================================
    # KEYUP
    # ============================================================
    elif event.type == pygame.KEYUP:
        for lane, keys in enumerate(lane_keys):
            if event.key in keys:

                screen_obj.key_pressed[lane] = False

                # ロング中断チェック
                screen_obj.logic.hold_miss_check(lane, False)

                # ★ TAIL 判定（result, note を受け取る）
                result, note = screen_obj.logic.release_judge(lane, screen_obj.song_time)

                if note and note.is_long:
                    if result == "miss":
                        long_logger.info(f"[LONG] MISS (released early): note_id={note.id}")
                    else:
                        long_logger.info(f"[LONG] TAIL HIT: note_id={note.id}, judge={result}")

                if result != "none":
                    screen_obj.spawn_hit_effect(lane, result)
