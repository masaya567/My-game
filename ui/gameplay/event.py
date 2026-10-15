import pygame
import time


def handle_gameplay_event(screen_obj, event):
    # ============================================================
    # 曲時間の更新（get_song_time 優先）
    # ============================================================
    get_song_time = getattr(screen_obj, "get_song_time", None)
    if callable(get_song_time):
        screen_obj.song_time = get_song_time()
    else:
        start_time = getattr(screen_obj, "music_start_time", None)
        if start_time is None:
            start_time = screen_obj.start_time
        screen_obj.song_time = max(0.0, time.perf_counter() - start_time)

    # None を除去して高速化
    lane_keys = [[k for k in keys if k is not None] for keys in screen_obj.lane_keys]

    # ============================================================
    # KEYDOWN（押した瞬間の即時判定）
    # ============================================================
    if event.type == pygame.KEYDOWN:
        for lane, keys in enumerate(lane_keys):
            if event.key in keys:

                # 連打ガード
                if screen_obj.key_pressed[lane]:
                    continue

                # 物理キー状態更新
                screen_obj.key_pressed[lane] = True

                # ★ レーン発光（商用品質）
                screen_obj.line_flash = 255
                screen_obj.line_flash_lane = lane

                # ★ ロング中の hold 判定（離していたらミス）
                screen_obj.logic.hold_miss_check(lane, True)

                # ★ ヘッド判定（即時）
                result = screen_obj.logic.try_judge(lane, screen_obj.song_time)
                if result != "none":
                    screen_obj.spawn_hit_effect(lane, result)

        # ESC → タイトルへ戻る
        if event.key == pygame.K_ESCAPE:
            pygame.mixer.music.stop()
            screen_obj.play_se("se_back")
            screen_obj.request_transition("title")

    # ============================================================
    # KEYUP（離した瞬間の即時ロング判定）
    # ============================================================
    elif event.type == pygame.KEYUP:
        for lane, keys in enumerate(lane_keys):
            if event.key in keys:

                # 物理キー状態更新
                screen_obj.key_pressed[lane] = False

                # ★ ロング中の hold ミス判定（離した瞬間）
                screen_obj.logic.hold_miss_check(lane, False)

                # ★ テール判定
                result = screen_obj.logic.release_judge(lane, screen_obj.song_time)
                if result != "none":
                    screen_obj.spawn_hit_effect(lane, result)
